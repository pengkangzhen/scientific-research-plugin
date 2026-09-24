#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan_visuals.py — 项目仓库图表盘点（slide-making 技能内置脚本）

为制作 PPT 对研究项目仓库做**确定性**图表盘点：
  1. 手稿索引优先：解析 *.tex 的 \\includegraphics / \\caption（作者预选过的图，
     精度最高），再全仓扫描兜底；
  2. 只产出元数据与排序，永不读取图像内容（防 token 黑洞）；
  3. stdout 只打摘要（计数 + Top-N 候选表），全量清单写入 --out 文件
     （渐进式披露：需要更多时再读文件）；
  4. 内置硬上限：忽略目录、深度、扫描文件数封顶。

用法：
  python3 scan_visuals.py <项目根> [--tex GLOB]... [--out FILE] [--top N] [--max-files N]

设计约定（勿破坏）：
  - 纯标准库，无第三方依赖（PIL 等不可假设可用）；
  - 文档型 PDF（paper/slides/main 等命名）默认从图候选中剔除，除非被手稿引用；
  - 选图决定权在人：本脚本只给盘点与信号，不替人挑图。
"""
import argparse
import datetime as dt
import os
import re
import struct
import sys
from pathlib import Path

# ---- 硬边界（防 token 黑洞的三道闸）-----------------------------------------
IGNORE_DIRS = {  # 目录名（小写）命中即整棵剪枝
    '.git', '.svn', '.hg', '.github', '.idea', '.vscode', 'node_modules',
    '__pycache__', '.venv', 'venv', '.tox', '.mypy_cache', '.pytest_cache',
    '.ipynb_checkpoints', 'site-packages', 'miniconda3', 'anaconda3',
    '.zcode', '.claude', '.codex',
}
IMG_EXTS = {'.png', '.jpg', '.jpeg', '.pdf', '.svg', '.eps', '.gif', '.bmp', '.tif', '.tiff'}
DATA_EXTS = {'.csv', '.tsv', '.xlsx', '.xls'}
DOC_PDF_RE = re.compile(  # 文档型 PDF 命名特征（编译产物，不是图）
    r'(paper|manuscript|draft|slides?|presentation|defense|thesis|dissertation'
    r'|report|beamer|开题|答辩|论文|汇报|总结)'
)
NAME_BOOST_RE = re.compile(  # 文件名词义加分（弱信号）
    r'(fig|figure|arch|framework|flow|result|pipeline|map|network|diagram'
    r'|schematic|plot|chart|流程|框架|架构|结果|网络|示意|拓扑)', re.I)
RECENT_DAYS = 180

INCLUDE_RE = re.compile(r'\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}')
GRAPHICSPATH_RE = re.compile(r'\\graphicspath\{([^}]*)\}')
CAPTION_RE = re.compile(r'\\caption(?:\[[^\]]*\])?\s*\{')
TABLE_BEGIN_RE = re.compile(r'\\begin\{table\*?\}|\\begin\{longtable\}')
TABLE_END_RE = re.compile(r'\\end\{table\*?\}|\\end\{longtable\}')


def human_size(n):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return f'{n:.0f} {unit}' if unit == 'B' else f'{n:.1f} {unit}'
        n /= 1024


def image_dims(path):
    """尽力而为读图像尺寸（纯标准库）：PNG/JPEG 精确，PDF MediaBox 正则。"""
    try:
        b = path.read_bytes()
    except OSError:
        return ''
    if b[:8] == b'\x89PNG\r\n\x1a\n':
        return f'{struct.unpack(">I", b[16:20])[0]}\u00d7{struct.unpack(">I", b[20:24])[0]}'
    if b[:2] == b'\xff\xd8':  # JPEG: 扫 SOF0-3 段
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF:
                i += 1
                continue
            m = b[i + 1]
            if m in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack('>HH', b[i + 5:i + 9])
                return f'{w}\u00d7{h}'
            if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
                i += 2
            else:
                i += 2 + struct.unpack('>H', b[i + 2:i + 4])[0]
    if b[:5] == b'%PDF-':  # PDF: 取首个 MediaBox
        m = re.search(rb'/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)', b)
        if m:
            x0, y0, x1, y1 = map(float, m.groups())
            w, h = abs(x1 - x0), abs(y1 - y0)
            if w and h:
                return f'{w:.0f}\u00d7{h:.0f} pt' + (' 竖版' if h > w else '')
    return ''


def tex_files(root, globs):
    if globs:
        out = []
        for g in globs:
            out += [p for p in root.glob(g) if p.is_file()]
        return sorted(set(out))
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith('.')]
        if len(Path(dirpath).parts) - len(root.parts) >= 8:
            dirnames[:] = []
        out += [Path(dirpath) / f for f in filenames if f.endswith('.tex')]
    return sorted(out)


def parse_tex(tex_paths, root):
    """返回 (引用名→[tex 位置+caption], graphicspath 集合, 表环境清单)。"""
    refs, gpaths, tables = {}, set(), []
    for tex in tex_paths:
        try:
            text = tex.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        for m in GRAPHICSPATH_RE.finditer(text):
            gpaths.update(x.strip() for x in re.findall(r'\{([^}]*)\}', m.group(1)))
        lines = text.splitlines()
        i = 0
        while i < len(lines):  # 逐行扫 includegraphics，窗口找同环境 caption
            m = INCLUDE_RE.search(lines[i])
            if m:
                target = m.group(1).strip()
                cap = ''
                for j in range(i, min(i + 40, len(lines))):  # caption 通常在同 figure 环境内
                    c = CAPTION_RE.search(lines[j])
                    if c:
                        seg = lines[j][c.end():]
                        cap = seg[:120].split('}', 1)[0].strip()
                        break
                    if j > i and (TABLE_END_RE.search(lines[j]) or '\\end{figure' in lines[j]
                                  or '\\end{wrapfigure' in lines[j]):
                        break
                refs.setdefault(target, []).append(
                    f'{tex.relative_to(root)}:{i + 1}' + (f'  caption: {cap}' if cap else ''))
            for t in TABLE_BEGIN_RE.finditer(lines[i]):
                seg = '\n'.join(lines[i:i + 60])
                c = CAPTION_RE.search(seg)
                cap = c.group(0) and re.split(r'}\s*(?:\n|$)', seg[c.end():][:160])[0].strip() if c else ''
                tables.append(f'{tex.relative_to(root)}:{i + 1}' + (f'  caption: {cap}' if cap else ''))
            i += 1
    return refs, gpaths, tables


def ref_matches(ref, cand_rel, root, gpaths):
    """引用名与候选文件匹配：按 stem 相等（带目录时要求目录后缀一致），
    兼容扩展名省略与 \\graphicspath 前缀省略。"""
    r = ref.replace('\\', '/').lstrip('./')
    r_stem = re.sub(r'\.(pdf|png|jpe?g|svg|eps|gif|bmp|tiff?)$', '', r, flags=re.I)
    c_stem = str(cand_rel).rsplit('.', 1)[0].replace('\\', '/')
    if '/' in r_stem:
        return c_stem.endswith('/' + r_stem) or c_stem == r_stem
    return c_stem.rsplit('/', 1)[-1] == r_stem


def main():
    ap = argparse.ArgumentParser(description='项目图表盘点（元数据 only，stdout 摘要 + 全量落盘）')
    ap.add_argument('root')
    ap.add_argument('--tex', action='append', default=[], help='手稿 .tex 的 glob（可多次）；缺省全仓找')
    ap.add_argument('--out', default='visual-inventory.md')
    ap.add_argument('--top', type=int, default=15)
    ap.add_argument('--max-files', type=int, default=2000, help='扫描文件数封顶')
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f'目录不存在: {root}')

    tex_paths = tex_files(root, args.tex)
    refs, gpaths, tables = parse_tex(tex_paths, root)

    candidates, data_files, truncated = [], [], False
    scanned = 0
    now = dt.datetime.now()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames
                             if d not in IGNORE_DIRS and not d.startswith('.'))
        if len(Path(dirpath).parts) - len(root.parts) >= 8:
            dirnames[:] = []
        for f in sorted(filenames):
            scanned += 1
            if scanned > args.max_files:
                truncated = True
                break
            p = Path(dirpath) / f
            ext = p.suffix.lower()
            rel = p.relative_to(root)
            if ext in DATA_EXTS:
                data_files.append(p)
            elif ext in IMG_EXTS:
                stem = p.stem.lower()
                hit = [k for k in refs if ref_matches(k, rel, root, gpaths)]
                is_doc = ext == '.pdf' and DOC_PDF_RE.search(stem) and not hit
                score = 0
                if hit:
                    score += 100
                if ext == '.pdf' and not is_doc:
                    score += 8
                if NAME_BOOST_RE.search(stem):
                    score += 6
                age_days = (now - dt.datetime.fromtimestamp(p.stat().st_mtime)).days
                if age_days <= RECENT_DAYS:
                    score += 4
                if not is_doc:
                    candidates.append({
                        'path': rel, 'size': p.stat().st_size, 'dims': image_dims(p),
                        'refs': hit, 'score': score, 'age': age_days,
                    })
        if truncated:
            break

    candidates.sort(key=lambda x: (-x['score'], -x['age']))

    # ---- stdout 摘要（恒定体量：计数 + Top-N）--------------------------------
    ref_count = sum(1 for c in candidates if c['refs'])
    print(f'盘点完成：图像候选 {len(candidates)}（被手稿引用 {ref_count}）· '
          f'LaTeX 表环境 {len(tables)} · 数据文件 {len(data_files)}'
          + (' · ⚠️ 达到扫描封顶，结果可能不完整' if truncated else ''))
    print(f'手稿 .tex：{len(tex_paths)} 个；文档型 PDF 已按命名过滤（被引用者除外）')
    print(f'完整清单 → {Path(args.out).resolve()}')
    if candidates:
        print(f'\nTop {min(args.top, len(candidates))} 候选（[引用]=手稿引用，选图权在人）：')
        for i, c in enumerate(candidates[:args.top], 1):
            tag = '[引用] ' if c['refs'] else ''
            cap = ''
            if c['refs']:
                m = re.search(r'caption: (.*)', c['refs'][0])
                cap = f'  {m.group(1)[:40]}' if m else ''
            print(f' {i:>2}. {tag}{c["path"]}  ({human_size(c["size"])}, '
                  f'{dt.date.today() - dt.timedelta(days=c["age"])}{", " + c["dims"] if c["dims"] else ""}){cap}')

    # ---- 全量清单落盘（渐进式披露的"文件"层）--------------------------------
    with open(args.out, 'w', encoding='utf-8') as w:
        w.write(f'# 图表盘点 — {root}\n\n生成：{now:%Y-%m-%d %H:%M} · '
                f'扫描 {scanned} 文件（封顶 {args.max_files}，'
                f'{"已截断" if truncated else "未截断"}）\n\n')
        w.write(f'- 图像候选 {len(candidates)}，其中被手稿引用 {ref_count}\n'
                f'- LaTeX 表环境 {len(tables)}（重排版走 SKILL §3，数据表走 figure-plot）\n'
                f'- 数据文件 {len(data_files)}\n\n## 图像候选（按信号排序）\n\n')
        w.write('| # | 信号 | 路径（相对仓库根） | 大小 | 尺寸 | 修改 | 手稿引用/caption |\n'
                '|---|------|--------------------|------|------|------|------------------|\n')
        for i, c in enumerate(candidates, 1):
            w.write(f'| {i} | {"引用" if c["refs"] else ""}'
                    f'{"+" if c["refs"] and c["score"] >= 108 else ""}'
                    f'{"矢量" if c["path"].suffix == ".pdf" else ""}'
                    f'{"+新" if c["age"] <= RECENT_DAYS else ""} '
                    f'| {c["path"]} | {human_size(c["size"])} | {c["dims"] or "—"} '
                    f'| {dt.date.today() - dt.timedelta(days=c["age"])} '
                    f'| {"; ".join(c["refs"]) if c["refs"] else "—"} |\n')
        if tables:
            w.write('\n## LaTeX 表环境\n\n')
            for t in tables:
                w.write(f'- {t}\n')
        if data_files:
            w.write('\n## 数据文件（做图表请走 figure-plot 规范，勿直接截图）\n\n')
            for d in data_files:
                w.write(f'- {d.relative_to(root)}  ({human_size(d.stat().st_size)})\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())

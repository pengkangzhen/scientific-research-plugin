#!/usr/bin/env python3
"""plan JSON → 分类颜色高亮写入 PDF（zotero-pdf-highlighting 管线第 2 步）。

读取 agent 生成的高亮计划（片段必须逐字取自 extract_pages.py 的输出），
在 PDF 中定位每个片段的所有出现位置，写入类别颜色的原生 PDF 高亮。
类别-颜色映射的唯一事实源是 ../references/category-colors.yaml（严格 5 类）。

幂等：同位置同色的已有高亮自动跳过，重跑安全。
写入的是文件内嵌批注——Zotero 阅读器直接显示（带只读锁），
不是 Zotero 批注条目；换文件不影响 Zotero 数据库。

用法：
    uv run highlight_pdf.py --plan /tmp/plan.json [--dry-run] [--report /tmp/report.md]

退出码：全部片段命中（写入或已存在）为 0，存在"未找到"片段为 1。
"""
# /// script
# requires-python = ">=3.10"
# dependencies = ["pymupdf", "pyyaml"]
# ///

import argparse
import glob
import json
import os
import sys

import pymupdf
import yaml

HIGHLIGHT_TYPE = 8   # PDF_ANNOT_HIGHLIGHT 的类型编号
LINE_TOL = 2.5       # 同一视觉行的 y0 容差（pt）
DUP_OVERLAP = 0.6    # 与已有高亮的重叠面积 / 较小者面积 ≥ 此值视为重复
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(SCRIPT_DIR, "..", "references", "category-colors.yaml")


# ---------- 归一化：与 extract_pages.py 逐函数一致，改动必须两处同步 ----------

def is_cjk(ch):
    """CJK 汉字与全角符号（行拼接与词边界判定的依据，与 extract_pages.py 一致）。"""
    return ("\u4e00" <= ch <= "\u9fff" or "\u3000" <= ch <= "\u303f"
            or "\uff00" <= ch <= "\uffef" or "\u3400" <= ch <= "\u4dbf")


LIGATURES = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl"}


def line_chars(page):
    """rawdict → 按行分组的 [(字符, bbox), ...]；连字展开为普通字母（与 extract_pages.py 一致，两处同步改）。"""
    lines = []
    raw = page.get_text("rawdict")
    for block in raw["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block["lines"]:
            chars = []
            for span in line["spans"]:
                for ch in span["chars"]:
                    c, bbox = ch["c"], tuple(ch["bbox"])
                    if c in LIGATURES:
                        chars.extend((part, bbox) for part in LIGATURES[c])
                    else:
                        chars.append((c, bbox))
            if chars:
                lines.append(chars)
    return lines


def normalize_lines(lines):
    norm = []
    for line in lines:
        cleaned = []
        pending_space = None
        for c, bbox in line:
            if c.isspace():
                if cleaned and pending_space is None:
                    pending_space = bbox
            else:
                if pending_space is not None:
                    cleaned.append((" ", pending_space))
                    pending_space = None
                cleaned.append((c, bbox))
        if not cleaned:
            continue
        if norm:
            if norm[-1][0] in ("-", "\u00ad"):
                norm.pop()
            elif not (is_cjk(norm[-1][0]) or is_cjk(cleaned[0][0])):
                norm.append((" ", None))
        norm.extend(cleaned)
    text = "".join(c for c, _ in norm)
    return text, norm


def norm_span(text):
    """片段文本归一化：连续空白折叠为单空格（与页面文本的行内折叠一致）。"""
    return " ".join(text.split())


# ---------- 定位与写入 ----------

def hex_to_rgb(value):
    value = value.strip().lstrip("#")
    if len(value) != 6:
        sys.exit(f"错误：非法颜色值 {value!r}（应为 #rrggbb）")
    return tuple(int(value[k:k + 2], 16) / 255 for k in (0, 2, 4))


def occurrence_runs(entries):
    """匹配区间（norm 切片）→ 视觉行分段矩形列表。

    行间连接空格（bbox=None）或 y0 跳变都开新段；每段是段内字符框的并集。
    """
    runs, cur = [], []
    cur_y = None
    for _c, bbox in entries:
        if bbox is None:
            if cur:
                runs.append(cur)
            cur, cur_y = [], None
            continue
        if cur and abs(bbox[1] - cur_y) > LINE_TOL:
            runs.append(cur)
            cur = []
        cur.append(bbox)
        cur_y = bbox[1]
    if cur:
        runs.append(cur)
    rects = []
    for run in runs:
        rects.append(pymupdf.Rect(
            min(b[0] for b in run), min(b[1] for b in run),
            max(b[2] for b in run), max(b[3] for b in run),
        ))
    return rects


def existing_highlights(page):
    """页面已有的文件内嵌高亮 → [(外接矩形, stroke 颜色元组), ...]。"""
    out = []
    for annot in page.annots() or []:
        if annot.type[0] != HIGHLIGHT_TYPE:
            continue
        out.append((pymupdf.Rect(annot.rect), (annot.colors or {}).get("stroke")))
    return out


def same_color(a, b, tol=2.0 / 255):
    if a is None or b is None or len(a) != len(b):
        return False
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def overlap_ratio(a, b):
    inter = a & b
    if inter.is_empty:
        return 0.0
    smaller = min(a.get_area(), b.get_area())
    return inter.get_area() / smaller if smaller > 0 else 0.0


def word_aligned_occurrences(text, needle):
    """整词对齐的子串匹配（西文词边界感知，CJK 字符不算边界）。"""
    def is_word_char(ch):
        return ch.isalnum() and not is_cjk(ch)

    out = []
    s = text.find(needle)
    while s != -1:
        e = s + len(needle)
        if s > 0 and is_word_char(text[s - 1]):
            s = text.find(needle, e)  # 嵌入更长单词（nonlinear programming），跳过
            continue
        while e < len(text) and is_word_char(text[e]):
            e += 1  # 复数/屈折向后吞并
        out.append((s, e))
        s = text.find(needle, e)
    return out


def find_refs_start(page_text):
    """参考文献标题的最后出现位置 (页索引, 页内偏移)；找不到返回 None。"""
    best = None
    for i, text in page_text.items():
        for heading in ("References", "REFERENCES", "参考文献"):
            j = text.rfind(heading)
            if j != -1 and (best is None or i > best[0] or (i == best[0] and j > best[1])):
                best = (i, j)
    return best


def in_refs(page_i, start, refs):
    return bool(refs) and (page_i > refs[0] or (page_i == refs[0] and start >= refs[1]))


def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    cats = cfg.get("categories") or {}
    if not cats:
        sys.exit(f"错误：配置 {path} 缺少 categories")
    return cats, os.path.expanduser((cfg.get("zotero") or {}).get("data_dir", "~/Zotero"))


def resolve_pdf(plan, data_dir):
    if plan.get("pdf"):
        p = os.path.expanduser(str(plan["pdf"]))
        if not os.path.exists(p):
            sys.exit(f"错误：PDF 不存在：{p}")
        return p
    key = plan.get("attachment_key")
    if not key:
        sys.exit("错误：plan 需要提供 pdf 路径或 attachment_key（二选一）")
    hits = sorted(glob.glob(os.path.join(data_dir, "storage", str(key), "*.pdf")))
    if not hits:
        sys.exit(f"错误：{data_dir}/storage/{key}/ 下没有 PDF（检查 category-colors.yaml 的 data_dir）")
    if len(hits) > 1:
        sys.exit("错误：该附件目录有多个 PDF，请在 plan 里用 pdf 字段指明：\n" + "\n".join(hits))
    return hits[0]


def clip(s, n=50):
    return s if len(s) <= n else s[:n] + "…"


def main():
    ap = argparse.ArgumentParser(description="plan JSON → 分类颜色高亮写入 PDF")
    ap.add_argument("--plan", required=True, help="高亮计划 JSON 路径（schema 见 references/plan-example.json）")
    ap.add_argument("--config", default=DEFAULT_CONFIG, help="类别-颜色配置（默认 references/category-colors.yaml）")
    ap.add_argument("--dry-run", action="store_true", help="只报告将写入什么，不落盘")
    ap.add_argument("--report", help="报告另存路径（markdown）")
    args = ap.parse_args()

    with open(args.plan, encoding="utf-8") as f:
        plan = json.load(f)
    categories, data_dir = load_config(args.config)

    spans = plan.get("spans") or []
    if not spans:
        sys.exit("错误：plan 里没有 spans")
    bad = sorted({s.get("category") for s in spans} - set(categories))
    if bad:
        sys.exit(f"错误：未知类别 {bad}；只允许严格 5 类：{'、'.join(categories)}")

    pdf_path = resolve_pdf(plan, data_dir)
    rgb = {cat: hex_to_rgb(hexv) for cat, hexv in categories.items()}

    doc = pymupdf.open(pdf_path)
    if doc.needs_pass:
        sys.exit("错误：PDF 已加密，无法写入高亮")

    page_text, page_norm = {}, {}
    for i, page in enumerate(doc):
        page_text[i], page_norm[i] = normalize_lines(line_chars(page))
    existing = {i: existing_highlights(page) for i, page in enumerate(doc)}
    refs = find_refs_start(page_text)

    rows, written, dup_total, not_found = [], 0, 0, 0
    refs_total, cross_pages = 0, []
    seen = set()
    for span in spans:
        cat = span["category"]
        needle = norm_span(span.get("text", ""))
        hint = span.get("page_hint")
        prange = span.get("pages")  # [起, 止] 1 基含端：锚定该关键词所属章节的页码区间
        dedup_key = (cat, needle, hint, tuple(prange) if prange else None)
        if not needle or dedup_key in seen:
            continue
        seen.add(dedup_key)

        anchored = bool(prange or hint)  # 显式锚定（区间或单页）是有意为之，不再过滤参考文献区
        if prange:
            pages_to_search = range(max(0, prange[0] - 1), min(len(doc), prange[1]))
        elif hint:
            pages_to_search = [hint - 1]
        else:
            pages_to_search = range(len(doc))
        occurrences, refs_this = [], 0
        for i in pages_to_search:
            if not 0 <= i < len(doc):
                continue
            text = page_text[i]
            for s, e in word_aligned_occurrences(text, needle):
                if not anchored and in_refs(i, s, refs):
                    refs_this += 1  # 参考文献区命中是标题噪声，跳过；显式锚定不滤
                    continue
                occurrences.append((i, page_norm[i][s:e]))
        refs_total += refs_this

        # 出现次数上限：默认每词只标首次出现处——高亮是路标不是地图，
        # 一个关键词标多次即重复。max_hits=0 全文标注，>1 按全文均匀分布取 N 处。
        max_hits = span.get("max_hits", plan.get("max_hits_default", 1))
        total_occ = len(occurrences)
        if max_hits and total_occ > max_hits:
            if max_hits == 1:
                picks = [0]
            else:
                picks = sorted({round(k * (total_occ - 1) / (max_hits - 1)) for k in range(max_hits)})
            occurrences = [occurrences[j] for j in picks]

        if not occurrences:
            not_found += 1
            status = "未找到" if not refs_this else f"仅在参考文献区（跳过 {refs_this} 处）"
            rows.append((cat, categories[cat], needle, "—", status))
            continue

        pages_str, new_this, dup_this = [], 0, 0
        for i, entries in occurrences:
            rects = occurrence_runs(entries)
            if not rects:
                continue
            union = pymupdf.Rect(rects[0])
            for r in rects[1:]:
                union |= r
            is_dup = any(
                same_color(rgb[cat], stroke) and overlap_ratio(union, erect) >= DUP_OVERLAP
                for erect, stroke in existing[i]
            )
            if not is_dup and any(
                stroke is not None and not same_color(stroke, rgb[cat])
                and overlap_ratio(union, erect) >= DUP_OVERLAP
                for erect, stroke in existing[i]
            ):
                if i + 1 not in cross_pages:
                    cross_pages.append(i + 1)
            pages_str.append(str(i + 1))
            if is_dup:
                dup_this += 1
                continue
            if args.dry_run:
                new_this += 1  # dry-run 里按"将写入"计数
                existing[i].append((union, rgb[cat]))  # 模拟写入，让后续 span 也能感知同轮重叠
                continue
            page = doc[i]
            annot = page.add_highlight_annot(quads=rects)
            annot.set_colors(stroke=rgb[cat])
            annot.update()
            existing[i].append((pymupdf.Rect(annot.rect), rgb[cat]))
            new_this += 1
        written += new_this
        dup_total += dup_this
        if new_this == 0 and dup_this == 0:
            not_found += 1
            status = "未找到有效文本框"
            if refs_this:
                status += f"（另跳过参考文献区 {refs_this} 处）"
            rows.append((cat, categories[cat], needle, ", ".join(pages_str) or "—", status))
            continue
        if new_this == 0:
            status = "全部已存在"
        else:
            status = f"{'将写入' if args.dry_run else '新写'} {new_this} 处"
            if dup_this:
                status += f"（已存在 {dup_this} 处）"
        if max_hits and total_occ > len(occurrences):
            if len(occurrences) == 1:
                status += f"（全文命中 {total_occ} 处，取首处）"
            else:
                status += f"（全文命中 {total_occ} 处，均匀取 {len(occurrences)} 处）"
        if refs_this:
            status += f"，跳过参考文献区 {refs_this} 处"
        rows.append((cat, categories[cat], needle, ", ".join(pages_str), status))

    if written and not args.dry_run:
        try:
            doc.save(pdf_path, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
        except Exception:
            tmp = pdf_path + ".hltmp"
            doc.save(tmp, garbage=1, deflate=True)
            doc.close()
            os.replace(tmp, pdf_path)

    lines = [
        f"# 高亮报告 — {os.path.basename(pdf_path)}",
        "",
        "| 类别 | 颜色 | 关键词 | 页 | 状态 |",
        "|---|---|---|---|---|",
    ]
    for cat, hexv, frag, pages, status in rows:
        lines.append(f"| {cat} | {hexv} | {clip(frag)} | {pages} | {status} |")
    lines.append("")
    verb = "将写入" if args.dry_run else "写入"
    lines.append(f"- 关键词 {len(rows)} 个：{verb} {written} 处，已存在 {dup_total} 处，未找到 {not_found} 个")
    if refs:
        lines.append(f"- 参考文献区自动跳过 {refs_total} 处（References 起于第 {refs[0] + 1} 页；附录在 References 后的论文用 page_hint 强制）")
    if cross_pages:
        lines.append(f"- 注意：{len(cross_pages)} 页存在跨色重叠——不同类别关键词或原自带高亮在同一位置叠加（页 {', '.join(map(str, cross_pages))}），必要时调整关键词归属")
    if args.dry_run:
        lines.append("- dry-run：未改动文件")
    else:
        lines.append("- 高亮为文件内嵌批注：Zotero 里关闭该 PDF 标签页后重开即可看到；多设备同步需手动触发")
    report = "\n".join(lines)
    print(report)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(report + "\n")
    sys.exit(1 if not_found else 0)


if __name__ == "__main__":
    main()

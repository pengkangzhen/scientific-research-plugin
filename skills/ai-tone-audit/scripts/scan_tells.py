#!/usr/bin/env python3
"""ai-tone-audit Stage 1：中文手稿 AI 腔确定性扫描（零模型）。

用法:
  uv run scan_tells.py thesis.tex                       # 也支持 .md / .txt / .docx
  uv run scan_tells.py thesis.tex --json scan.json --md scan.md
  uv run scan_tells.py thesis.tex --json after.json --compare before.json   # Stage 3 回归闸门
选项: --rules data/rules_zh.jsonl  --max-per-rule 12  --min-cjk-ratio 0.3

纯 stdlib。规则全部在 data/rules_zh.jsonl（一行一条，字段 id/cat/w/scope/pattern/exempt/note）；
scope 取值：
  span    在段落全文上 finditer
  sent    逐句 search（锚定句首的规则）
  last    只匹配段落最后一句（段落 ≥2 句）
  nodigit 逐句 search，且该句不含数字/公式/百分号才算命中
  stack2  同一句命中 ≥2 次才记一条（转交类，权重 0）
exempt 是章节标题正则：命中章节（如"本章小结"）内该规则记为豁免、不计分。
统计层：分章节字数、加权分/千字、句长均值与变异系数（CV，越低越单调）。
判定遵循"看聚集不看单词"：报告给密度与重灾区，不对单个词下结论。
--compare：与旧 JSON 比较，出现新命中（按规则+匹配文本计）或总分上升 → 退出码 1。
"""

from __future__ import annotations

import argparse
import html
import json
import re
import statistics
import sys
import zipfile
from bisect import bisect_right
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_RULES = SKILL_DIR / "data" / "rules_zh.jsonl"
DEFAULT_BASELINE = SKILL_DIR / "data" / "baseline_stats_zh.json"

CAT_LABEL = {
    "Z1": "宏大开篇",
    "Z2": "讲义腔路标词",
    "Z3": "拔高套话",
    "Z4": "二分对照壳",
    "Z5": "四字格连排",
    "Z6": "机械枚举",
    "Z7": "段末升华",
    "Z8": "欧化弱动词",
    "Z9": "抽象施事",
    "Z10": "空泛评价",
    "Z11": "格式癖",
    "Z12": "节奏单调",
    "R": "转交 hedge-audit",
}

CJK = re.compile(r"[\u4e00-\u9fff]")
ASCII_WORD = re.compile(r"[A-Za-z]+")
NUMERIC = re.compile(r"[0-9０-９%％]|〈式〉")
SENT_END = re.compile(r"(?<=[。！？；!?;])")
HEADING_GUESS = re.compile(
    r"^(第[一二三四五六七八九十百\d]+[章节]|[一二三四五六七八九十]+、|\d+(\.\d+){0,3}\s+)\S{1,40}$"
)

# 暂定阈值（加权分/千字），若加载 baseline_stats_zh.json 则自动替换为经验分位阈值
DEFAULT_LEVELS = ((10.0, "高"), (4.0, "中"), (0.0, "低"))
CV_FLAT = 0.35       # 句长 CV 低于此值且句数 ≥ 10 → Z12-01 节奏单调
MIN_SENTS_FOR_CV = 10
PARA_CV_FLAT = 0.18  # 段长 CV 低于此值且段数 ≥ 4 → Z12-02 段落同构
MIN_PARAS_FOR_CV = 4


# ---------------------------------------------------------------- data model


@dataclass
class Para:
    section: str
    text: str
    anchors: list = field(default_factory=list)  # [(offset, loc_str)] 升序

    def loc(self, offset: int) -> str:
        if not self.anchors:
            return "?"
        i = bisect_right([a[0] for a in self.anchors], offset) - 1
        return self.anchors[max(i, 0)][1]


@dataclass
class Rule:
    id: str
    cat: str
    w: float
    scope: str
    rx: re.Pattern
    exempt: re.Pattern | None
    note: str


def load_rules(path: Path) -> list[Rule]:
    rules = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("//"):
            continue
        d = json.loads(line)
        try:
            rx = re.compile(d["pattern"])
        except re.error as e:
            sys.exit(f"{path}:{n} 规则 {d.get('id')} 正则错误: {e}")
        ex = re.compile(d["exempt"]) if d.get("exempt") else None
        rules.append(Rule(d["id"], d["cat"], float(d["w"]), d["scope"], rx, ex, d.get("note", "")))
    return rules


# ---------------------------------------------------------------- parsers

MATH_ENVS = {
    "equation", "equation*", "align", "align*", "gather", "gather*", "multline", "multline*",
    "eqnarray", "eqnarray*", "flalign", "flalign*", "alignat", "alignat*", "math", "displaymath",
}
DROP_ENVS = MATH_ENVS | {
    "verbatim", "verbatim*", "lstlisting", "minted", "comment", "filecontents",
    "figure", "figure*", "table", "table*", "tabular", "tabular*", "longtable", "tikzpicture",
    "algorithm", "algorithm*", "algorithmic", "thebibliography", "lstinputlisting",
}
SECTION_CMD = re.compile(
    r"\\(chapter|section|subsection|subsubsection)\*?\s*(?:\[[^\]]*\])?\{(.*)\}"
)
BEGIN_ENV = re.compile(r"\\begin\{([^}]+)\}")
END_ENV = re.compile(r"\\end\{([^}]+)\}")
INPUT_CMD = re.compile(r"\\(?:input|include|subfile)\{([^}]+)\}")
BOLD_TEX = re.compile(r"\\(textbf|bfseries)\b")


def tex_inline(s: str) -> str:
    s = s.replace("\\%", "％")
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\$\$.*?\$\$|(?<!\\)\$[^$]*\$|\\\(.*?\\\)|\\\[.*?\\\]", "〈式〉", s)
    s = re.sub(r"\\(?:cite[a-zA-Z]*|upcite)\*?(?:\[[^\]]*\])*\{[^}]*\}", "", s)
    s = re.sub(r"\\(?:ref|eqref|autoref|cref|Cref|pageref)\{[^}]*\}", "〈引〉", s)
    s = re.sub(r"\\(?:label|index|footnote|url|href)\{[^}]*\}", "", s)
    for _ in range(4):
        s = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+\*?", "", s)
    s = s.replace("{", "").replace("}", "").replace("~", " ").replace("\\\\", "")
    return s.strip()


def iter_tex_lines(path: Path, seen: set | None = None):
    """展开 \\input/\\include，逐行产出 (loc, raw_line)。"""
    seen = seen or set()
    rp = path.resolve()
    if rp in seen or not rp.exists():
        return
    seen.add(rp)
    for n, raw in enumerate(rp.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        m = INPUT_CMD.search(raw) if not raw.lstrip().startswith("%") else None
        if m:
            child = (rp.parent / m.group(1))
            if child.suffix != ".tex":
                child = child.with_suffix(".tex")
            yield from iter_tex_lines(child, seen)
            continue
        yield f"{rp.name}:{n}", raw


def parse_tex(path: Path) -> tuple[list[Para], list[tuple[str, str, str]]]:
    paras: list[Para] = []
    fmt_hits: list[tuple[str, str, str]] = []  # (section, loc, snippet)
    lines = list(iter_tex_lines(path))
    has_doc = any("\\begin{document}" in r for _, r in lines)
    in_doc = not has_doc
    section = "（正文前）"
    buf_text, buf_anchors = "", []
    drop_stack: list[str] = []
    in_display = False

    def flush():
        nonlocal buf_text, buf_anchors
        if buf_text.strip():
            paras.append(Para(section, buf_text.strip(), buf_anchors))
        buf_text, buf_anchors = "", []

    for loc, raw in lines:
        if "\\begin{document}" in raw:
            in_doc = True
            continue
        if not in_doc:
            continue
        if "\\end{document}" in raw:
            break
        stripped = re.sub(r"(?<!\\)%.*", "", raw).strip()
        if drop_stack:
            for m in END_ENV.finditer(stripped):
                if drop_stack and m.group(1) == drop_stack[-1]:
                    drop_stack.pop()
            continue
        if in_display:
            if "\\]" in stripped:
                in_display = False
            continue
        if stripped.startswith("\\[") and "\\]" not in stripped:
            in_display = True
            buf_text += "〈式〉"
            continue
        bm = BEGIN_ENV.search(stripped)
        if bm and bm.group(1) in DROP_ENVS:
            env = bm.group(1)
            if not re.search(r"\\end\{" + re.escape(env) + r"\}", stripped):
                drop_stack.append(env)
            if env in MATH_ENVS:
                buf_text += "〈式〉"
            continue
        sm = SECTION_CMD.search(stripped)
        if sm:
            flush()
            section = tex_inline(sm.group(2)) or sm.group(2)
            continue
        if not stripped:
            flush()
            continue
        if BOLD_TEX.search(stripped) and CJK.search(stripped):
            fmt_hits.append((section, loc, stripped[:40]))
        text = tex_inline(stripped)
        text = re.sub(r"\\(begin|end)\{[^}]*\}", "", text)
        if not text:
            continue
        buf_anchors.append((len(buf_text), loc))
        buf_text += text
    flush()
    return paras, fmt_hits


def parse_md(path: Path) -> tuple[list[Para], list[tuple[str, str, str]]]:
    paras, fmt_hits = [], []
    section, buf, anchors, in_code = "（正文前）", "", [], False

    def flush():
        nonlocal buf, anchors
        if buf.strip():
            paras.append(Para(section, buf.strip(), anchors))
        buf, anchors = "", []

    for n, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        s = raw.strip()
        if s.startswith("```"):
            in_code = not in_code
            flush()
            continue
        if in_code:
            continue
        if s.startswith("#"):
            flush()
            section = s.lstrip("#").strip()
            continue
        if not s:
            flush()
            continue
        if path.suffix == ".txt" and HEADING_GUESS.match(s) and not re.search(r"[。！？]", s):
            flush()
            section = s
            continue
        if ("**" in s or "__" in s) and CJK.search(s):
            fmt_hits.append((section, f"{path.name}:{n}", s[:40]))
        s = re.sub(r"`[^`]*`", "〈码〉", s)
        s = re.sub(r"\$[^$]*\$", "〈式〉", s)
        s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", s)
        s = re.sub(r"^\s*([-*+]|\d+\.)\s+", "", s)
        s = s.replace("**", "").replace("__", "")
        anchors.append((len(buf), f"{path.name}:{n}"))
        buf += s
    flush()
    return paras, fmt_hits


def parse_docx(path: Path) -> tuple[list[Para], list[tuple[str, str, str]]]:
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    paras, fmt_hits = [], []
    section, n = "（正文前）", 0
    for m in re.finditer(r"<w:p[ >].*?</w:p>", xml, re.S):
        p = m.group(0)
        text = html.unescape("".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", p))).strip()
        if not text:
            continue
        n += 1
        style = re.search(r'<w:pStyle w:val="([^"]+)"', p)
        sv = style.group(1) if style else ""
        is_heading = bool(
            re.search(r'<w:outlineLvl w:val="[0-8]"', p)
            or re.match(r"(?i)^(heading|标题)\s*\d$|^\d$|^TOC", sv)
            or (len(text) <= 40 and HEADING_GUESS.match(text) and not re.search(r"[。！？]", text))
        )
        if is_heading:
            section = text
            continue
        if sv.lower().startswith("toc"):
            continue
        if re.search(r"<w:b(?:\s*/>|\s+w:val=\"(?!0|false)[^\"]*\")", p) and CJK.search(text):
            fmt_hits.append((section, f"¶{n}", text[:40]))
        paras.append(Para(section, text, [(0, f"¶{n}")]))
    return paras, fmt_hits


def parse(path: Path):
    suf = path.suffix.lower()
    if suf == ".tex":
        return parse_tex(path)
    if suf == ".docx":
        return parse_docx(path)
    if suf in (".md", ".markdown", ".txt"):
        return parse_md(path)
    sys.exit(f"不支持的文件类型: {suf}（支持 .tex/.md/.txt/.docx）")


# ---------------------------------------------------------------- scanning


def text_len(s: str) -> int:
    return len(CJK.findall(s)) + len(ASCII_WORD.findall(s))


def split_sents(text: str) -> list[tuple[int, str]]:
    out, pos = [], 0
    for piece in SENT_END.split(text):
        if piece.strip():
            out.append((pos, piece))
        pos += len(piece)
    return out


def snippet(text: str, start: int, end: int, pad: int = 12) -> str:
    a, b = max(0, start - pad), min(len(text), end + pad)
    return ("…" if a else "") + text[a:start] + "【" + text[start:end] + "】" + text[end:b] + ("…" if b < len(text) else "")


def resolve_levels(baseline: dict | None) -> tuple[tuple[float, str], ...]:
    if not baseline:
        return DEFAULT_LEVELS
    mid = max(float(baseline.get("p50_per_k", 4.0)), 1.5)
    high = max(float(baseline.get("p90_per_k", 10.0)), mid + 2.0)
    return ((round(high, 2), "高"), (round(mid, 2), "中"), (0.0, "低"))


def scan(paras: list[Para], fmt_hits, rules: list[Rule], min_cjk_ratio: float, baseline: dict | None = None):
    levels = resolve_levels(baseline)
    bl_mean = float(baseline["mean_per_k"]) if baseline and "mean_per_k" in baseline else None
    bl_sd = float(baseline["sd_per_k"]) if baseline and "sd_per_k" in baseline else None
    cv_flat = float(baseline.get("p10_sent_cv", CV_FLAT)) if baseline else CV_FLAT
    hits = []
    sec_stats: dict[str, dict] = {}
    skipped = 0
    order: list[str] = []

    def sec(name):
        if name not in sec_stats:
            sec_stats[name] = {"chars": 0, "sent_lens": [], "para_lens": [], "score": 0.0, "cats": Counter()}
            order.append(name)
        return sec_stats[name]

    for p in paras:
        tl = text_len(p.text)
        cjk = len(CJK.findall(p.text))
        if tl == 0 or cjk / max(len(p.text), 1) < min_cjk_ratio:
            skipped += 1
            continue
        st = sec(p.section)
        st["chars"] += tl
        st["para_lens"].append(tl)
        sents = split_sents(p.text)
        for _, s in sents:
            sl = text_len(s)
            if sl >= 4:
                st["sent_lens"].append(sl)

        cands = []  # (rule, start, end)
        for r in rules:
            found = []
            if r.scope == "span":
                found = [(m.start(), m.end()) for m in r.rx.finditer(p.text)]
            elif r.scope == "sent":
                for off, s in sents:
                    m = r.rx.search(s.lstrip())
                    if m:
                        lead = len(s) - len(s.lstrip())
                        found.append((off + lead + m.start(), off + lead + m.end()))
            elif r.scope == "last" and len(sents) >= 2:
                off, s = sents[-1]
                m = r.rx.search(s.lstrip())
                if m:
                    lead = len(s) - len(s.lstrip())
                    found.append((off + lead + m.start(), off + lead + m.end()))
            elif r.scope == "nodigit":
                for off, s in sents:
                    if NUMERIC.search(s):
                        continue
                    m = r.rx.search(s)
                    if m:
                        found.append((off + m.start(), off + m.end()))
            elif r.scope == "stack2":
                for off, s in sents:
                    ms = list(r.rx.finditer(s))
                    if len(ms) >= 2:
                        found.append((off + ms[0].start(), off + ms[-1].end()))
            cands += [(r, a, b) for a, b in found]

        # 同类别内重叠命中只留权重最高的一条（如 Z8-01 与 Z8-02 同指一处"对……进行了梳理"）
        cands.sort(key=lambda t: (t[0].cat, -t[0].w, t[1]))
        kept: dict[str, list[tuple[int, int]]] = defaultdict(list)
        for r, a, b in cands:
            if any(a < kb and ka < b for ka, kb in kept[r.cat]):
                continue
            kept[r.cat].append((a, b))
            exempt = bool(r.exempt and r.exempt.search(p.section))
            w = 0.0 if exempt else r.w
            hits.append({
                "rule": r.id, "cat": r.cat, "w": w, "exempt": exempt,
                "section": p.section, "loc": p.loc(a),
                "match": p.text[a:b], "snippet": snippet(p.text, a, b), "note": r.note,
            })
            st["score"] += w
            if not exempt:
                st["cats"][r.cat] += 1

    for section, loc, snip in fmt_hits:
        if section not in sec_stats or sec_stats[section]["chars"] == 0:
            continue
        st = sec(section)
        hits.append({"rule": "Z11-02", "cat": "Z11", "w": 0.5, "exempt": False, "section": section,
                     "loc": loc, "match": "加粗", "snippet": snip, "note": "正文加粗"})
        st["score"] += 0.5
        st["cats"]["Z11"] += 1

    sections = []
    for name in order:
        st = sec_stats[name]
        lens = st["sent_lens"]
        plens = st["para_lens"]
        mean = statistics.mean(lens) if lens else 0.0
        cv = statistics.pstdev(lens) / mean if len(lens) >= 2 and mean else None
        pmean = statistics.mean(plens) if plens else 0.0
        pcv = statistics.pstdev(plens) / pmean if len(plens) >= 2 and pmean else None
        if cv is not None and len(lens) >= MIN_SENTS_FOR_CV and cv < cv_flat:
            st["score"] += 2.0
            st["cats"]["Z12"] += 1
            hits.append({"rule": "Z12-01", "cat": "Z12", "w": 2.0, "exempt": False, "section": name,
                         "loc": "（全节）", "match": f"句CV={cv:.2f}", "snippet": f"句长均值 {mean:.1f}，CV {cv:.2f}，{len(lens)} 句",
                         "note": "句长变异系数过低：节奏单调"})
        if pcv is not None and len(plens) >= MIN_PARAS_FOR_CV and pcv < PARA_CV_FLAT:
            st["score"] += 1.5
            st["cats"]["Z12"] += 1
            hits.append({"rule": "Z12-02", "cat": "Z12", "w": 1.5, "exempt": False, "section": name,
                         "loc": "（全节）", "match": f"段CV={pcv:.2f}", "snippet": f"段长均值 {pmean:.1f}，CV {pcv:.2f}，{len(plens)} 段",
                         "note": "段长变异系数过低：段落同构"})
        per_k = st["score"] / st["chars"] * 1000 if st["chars"] else 0.0
        z = round((per_k - bl_mean) / bl_sd, 2) if (bl_mean is not None and bl_sd and bl_sd > 0) else None
        level = next(lbl for th, lbl in levels if per_k >= th)
        sections.append({
            "section": name, "chars": st["chars"], "sentences": len(lens),
            "sent_mean": round(mean, 1), "sent_cv": None if cv is None else round(cv, 2),
            "para_cv": None if pcv is None else round(pcv, 2),
            "score": round(st["score"], 1), "per_k": round(per_k, 2),
            "z_score": z, "level": level, "cats": dict(st["cats"]),
        })
    total_chars = sum(s["chars"] for s in sections)
    total_score = sum(h["w"] for h in hits)
    return {
        "total_chars": total_chars,
        "total_score": round(total_score, 1),
        "per_k": round(total_score / total_chars * 1000, 2) if total_chars else 0.0,
        "skipped_paras": skipped,
        "levels": [{"min": th, "label": lbl} for th, lbl in levels],
        "baseline": baseline,
        "sections": sections,
        "hits": hits,
    }


# ---------------------------------------------------------------- reporting


def render_md(res: dict, src: str, max_per_rule: int) -> str:
    levels = [(d["min"], d["label"]) for d in res.get("levels", [])] or list(DEFAULT_LEVELS)
    bl = res.get("baseline")
    out = [f"## AI 腔扫描（Stage 1）：{src}", ""]
    overall = next(lbl for th, lbl in levels if res["per_k"] >= th)
    high_th, mid_th = levels[0][0], levels[1][0]
    if bl:
        bl_note = (f"已加载人类基线（{bl.get('source_desc', '本地语料')}，{bl.get('n_docs', '?')} 篇，"
                   f"基线均值 {bl.get('mean_per_k')}/千字，阈值 <{mid_th} 低 / {mid_th}–{high_th} 中 / ≥{high_th} 高）。")
    else:
        bl_note = (f"阈值为暂定值（<{mid_th} 低 / {mid_th}–{high_th} 中 / ≥{high_th} 高），尚未加载人类基线"
                   "（可用 `build_baseline.py` 从本地 ≤2022 中文论文生成 `baseline_stats_zh.json`）。")
    out.append(
        f"**全稿**：{res['total_chars']} 字，加权分 {res['total_score']}，"
        f"**{res['per_k']}/千字（{overall}）**；跳过非中文段落 {res['skipped_paras']} 个。{bl_note}"
    )
    has_z = any(s.get("z_score") is not None for s in res["sections"])
    hdr = "| 章节 | 字数 | 句数 | 句长均值 | 句长CV | 加权分 | 分/千字 |" + (" 基线z |" if has_z else "") + " 等级 | 主要类别 |"
    sep = "|---|---|---|---|---|---|---|" + ("---|" if has_z else "") + "---|---|"
    out += ["", "### 分章节密度", "", hdr, sep]
    for s in res["sections"]:
        top = "、".join(f"{CAT_LABEL.get(c, c)}×{k}" for c, k in Counter(s["cats"]).most_common(3)) or "—"
        cv = "—" if s["sent_cv"] is None else s["sent_cv"]
        z_col = f" {s['z_score'] if s['z_score'] is not None else '—'} |" if has_z else ""
        out.append(f"| {s['section']} | {s['chars']} | {s['sentences']} | {s['sent_mean']} | {cv} | "
                   f"{s['score']} | {s['per_k']} |{z_col} {s['level']} | {top} |")

    cat_tot = Counter()
    for h in res["hits"]:
        if not h["exempt"]:
            cat_tot[h["cat"]] += 1
    out += ["", "### 类别汇总", "", "| 类别 | 命中数 |", "|---|---|"]
    for c in CAT_LABEL:
        if cat_tot.get(c):
            out.append(f"| {c} {CAT_LABEL[c]} | {cat_tot[c]} |")

    by_rule = defaultdict(list)
    for h in res["hits"]:
        by_rule[h["rule"]].append(h)
    out += ["", "### 命中清单（按规则）", ""]
    for rid in sorted(by_rule, key=lambda x: (x.split("-")[0][0], int(re.sub(r"\D", "", x.split("-")[0]) or 0), x)):
        hs = by_rule[rid]
        h0 = hs[0]
        ex = sum(1 for h in hs if h["exempt"])
        out.append(f"**{rid}** {CAT_LABEL.get(h0['cat'], h0['cat'])}｜{h0['note']}｜{len(hs)} 处"
                   + (f"（其中 {ex} 处在豁免章节）" if ex else ""))
        for h in hs[:max_per_rule]:
            tag = "（豁免）" if h["exempt"] else ""
            out.append(f"- `{h['loc']}` [{h['section']}] {h['snippet']}{tag}")
        if len(hs) > max_per_rule:
            out.append(f"- …另有 {len(hs) - max_per_rule} 处，见 JSON")
        out.append("")
    return "\n".join(out)


def compare(new: dict, old: dict) -> tuple[bool, str]:
    key = lambda h: (h["rule"], h["match"])
    old_c = Counter(key(h) for h in old["hits"] if h["w"] > 0)
    new_c = Counter(key(h) for h in new["hits"] if h["w"] > 0)
    added = new_c - old_c
    removed = old_c - new_c
    lines = [f"### 回归比较", "",
             f"- 加权分：{old['total_score']} → {new['total_score']}；分/千字：{old['per_k']} → {new['per_k']}",
             f"- 消除命中 {sum(removed.values())} 处；新增命中 {sum(added.values())} 处"]
    for (rid, m), k in added.most_common():
        lines.append(f"  - 新增 {rid}「{m}」×{k}")
    ok = not added and new["total_score"] <= old["total_score"]
    lines.append(f"- 闸门：{'通过' if ok else '未通过（新增命中或总分上升）'}")
    return ok, "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="中文手稿 AI 腔确定性扫描")
    ap.add_argument("file", type=Path)
    ap.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    ap.add_argument("--baseline", type=Path, default=None, help="人类基线 JSON（缺省自动读取 data/baseline_stats_zh.json 若存在）")
    ap.add_argument("--no-baseline", action="store_true", help="忽略人类基线，强制使用暂定阈值")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--md", type=Path)
    ap.add_argument("--compare", type=Path, help="旧扫描 JSON；新增命中或总分上升则退出码 1")
    ap.add_argument("--max-per-rule", type=int, default=12)
    ap.add_argument("--min-cjk-ratio", type=float, default=0.3)
    a = ap.parse_args()

    bl_path = None if a.no_baseline else (a.baseline or (DEFAULT_BASELINE if DEFAULT_BASELINE.exists() else None))
    baseline = json.loads(bl_path.read_text(encoding="utf-8")) if bl_path else None
    paras, fmt_hits = parse(a.file)
    res = scan(paras, fmt_hits, load_rules(a.rules), a.min_cjk_ratio, baseline=baseline)
    res["source"] = str(a.file)
    md = render_md(res, a.file.name, a.max_per_rule)
    rc = 0
    if a.compare:
        ok, cmp_md = compare(res, json.loads(a.compare.read_text(encoding="utf-8")))
        md += "\n" + cmp_md + "\n"
        rc = 0 if ok else 1
    if a.json:
        a.json.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    if a.md:
        a.md.write_text(md, encoding="utf-8")
    print(md)
    return rc


if __name__ == "__main__":
    sys.exit(main())

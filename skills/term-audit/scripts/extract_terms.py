#!/usr/bin/env python3
"""term-audit 第一步：从 LaTeX 手稿提取候选名词短语并按五信号排序。

用法:
  uv run extract_terms.py manuscript.tex
  uv run extract_terms.py manuscript.tex --baseline "published/*.tex" --whitelist terms.txt
选项: --top 60 --min-count 2 --batch-size 20 --json out.json --md out.md

纯 stdlib。产出排序候选表（markdown + JSON）：每个候选附五个信号
（频次 / 结构位置 / style 黑名单 / 日常词拼接比 / 基线语料缺席）与优先级得分，
并按得分切好审计批次，供 jargon-check terms 模式直接派工。
黑话病理单位是多词复合名词短语，单名词仅当命中 style 黑名单才进入漏斗。
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# 分段停用词：RAKE 式候选生成的切分点（算法内部参数，非业务数据）
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "that", "this",
    "these", "those", "of", "in", "on", "at", "to", "for", "from", "by", "with",
    "without", "within", "into", "onto", "over", "under", "between", "among",
    "through", "during", "before", "after", "above", "below", "up", "down", "out",
    "off", "again", "further", "once", "here", "there", "when", "where", "why",
    "how", "all", "any", "both", "each", "few", "more", "most", "other", "some",
    "such", "no", "nor", "not", "only", "own", "same", "so", "too", "very", "can",
    "cannot", "could", "should", "would", "may", "might", "must", "shall", "will",
    "do", "does", "did", "done", "is", "are", "was", "were", "be", "been", "being",
    "am", "have", "has", "had", "having", "i", "we", "you", "he", "she", "it",
    "they", "them", "his", "her", "its", "their", "our", "my", "your", "me", "us",
    "him", "what", "which", "who", "whom", "whose", "as", "because", "while",
    "until", "about", "against", "also", "however", "therefore", "thus", "hence",
    "moreover", "furthermore", "nevertheless", "otherwise", "instead", "rather",
    "quite", "just", "even", "still", "yet", "either", "neither", "per", "via",
    "across", "along", "around", "behind", "besides", "despite", "except", "inside",
    "outside", "since", "toward", "towards", "upon", "s", "t", "d", "ll", "re", "ve",
}

MATH_ENVS = (
    "equation", "align", "gather", "multline", "eqnarray", "flalign", "alignat",
    "math", "displaymath", "split", "cases", "aligned", "gathered",
)
VERBATIM_ENVS = ("verbatim", "verbatim*", "lstlisting", "minted", "comment", "filecontents")
DROP_ARG_COMMANDS = (
    "label", "ref", "eqref", "pageref", "autoref", "cref", "Cref", "cite", "citep",
    "citet", "citealp", "citeauthor", "citeyear", "citealt", "bibitem", "bibliography",
    "bibliographystyle", "usepackage", "documentclass", "input", "include",
    "includegraphics", "graphicspath", "url", "href", "index", "markboth", "special",
)
FLOAT_ENVS = ("figure", "figure*", "table", "table*", "scheme", "scheme*")

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z\-']*")


def strip_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", text)


def match_brace(text: str, open_idx: int) -> int:
    """返回与 text[open_idx]（必须是 '{'）配对的 '}' 下标，找不到返回 -1。"""
    depth = 0
    for i in range(open_idx, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return -1


def parse_macros(text: str) -> dict[str, str]:
    """解析零参数 \\newcommand/\\renewcommand 定义，供术语宏展开（如 \\method → SOP-MAS）。"""
    macros: dict[str, str] = {}
    for m in re.finditer(r"\\(?:re)?newcommand\*?\s*\{?\\(\w+)\}?(?!\s*\[)", text):
        brace = text.find("{", m.end() - 1)
        if brace == -1:
            continue
        close = match_brace(text, brace)
        if close != -1:
            macros[m.group(1)] = text[brace + 1 : close]
    return macros


def expand_macros(text: str, macros: dict[str, str], passes: int = 2) -> str:
    for _ in range(passes):
        changed = False
        for name, body in macros.items():
            # 用函数替换：宏体含反斜杠（\textbf 等）不能走 re.sub 的转义模板
            expanded = re.sub(r"\\" + name + r"(?![a-zA-Z])", lambda m, b=body: b, text)
            if expanded != text:
                text, changed = expanded, True
        if not changed:
            break
    return text


def remove_env(text: str, env: str, replacement: str | None = None) -> str:
    """删除 \\begin{env}...\\end{env} 块；给 replacement 时以各块捕获组内容替换。"""
    pattern = re.compile(r"\\begin\{" + re.escape(env) + r"\}(.*?)\\end\{" + re.escape(env) + r"\}", re.S)
    if replacement is not None:
        return pattern.sub(lambda m: replacement(m.group(1)), text)
    return pattern.sub(" ", text)


def captions_of(body: str) -> str:
    """提取浮动体内所有 \\caption{...} 的图题文字。"""
    out = []
    for m in re.finditer(r"\\caption\*?\s*\{", body):
        close = match_brace(body, m.end() - 1)
        if close != -1:
            out.append(body[m.end() : close])
    return " ".join(out)


def clean_latex(text: str) -> str:
    """LaTeX → 可分词的散文（含图题，剔除数学/引用/原样环境）。"""
    text = strip_comments(text)
    text = expand_macros(text, parse_macros(text))
    for env in VERBATIM_ENVS:
        text = remove_env(text, env)
    # 浮动体只保留 \caption{...} 的图题文字
    for env in FLOAT_ENVS:
        text = remove_env(text, env, captions_of)
    for env in MATH_ENVS:
        text = remove_env(text, env)
    text = re.sub(r"\$\$.+?\$\$", " ", text, flags=re.S)
    text = text.replace(r"\$", "\x00")
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\\((?:.|\n)*?\\\)", " ", text)
    text = re.sub(r"\\\[(?:.|\n)*?\\\]", " ", text)
    text = text.replace("\x00", r"\$")
    for cmd in DROP_ARG_COMMANDS:
        # 带可选方括号参数的形态（如 \citep[see][]{x}）一并标记
        text = re.sub(r"\\" + cmd + r"\*?(?:\[[^\]]*\])*\s*\{", "\x01{", text)
    text = re.sub("\x01\\{[^{}]*\\}", " ", text)
    text = re.sub(r"\\\\", " ", text)  # \\ 换行
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)  # \command 整 token 删除，花括号内容保留
    text = text.replace("\\", "")  # 残余孤立反斜杠
    return text


def structural_zones(text: str) -> dict[str, str]:
    """抓取标题/章节标题/摘要区，用于结构位置信号。在宏展开后调用。"""
    zones: dict[str, list[str]] = {"title": [], "section": [], "abstract": []}
    m = re.search(r"\\title\s*\{", text)
    if m:
        close = match_brace(text, m.end() - 1)
        if close != -1:
            zones["title"].append(text[m.end() : close])
    for m in re.finditer(r"\\(?:sub)*section\*?\s*\{", text):
        close = match_brace(text, m.end() - 1)
        if close != -1:
            zones["section"].append(text[m.end() : close])
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", text, re.S)
    if m:
        zones["abstract"].append(m.group(1))
    return {k: clean_latex(" ".join(v)) for k, v in zones.items()}


def tokenize(prose: str) -> list[str]:
    """保留原始大小写的词元（展示层要用 acronym 原形），只去边缘连字符/撇号。"""
    return [t for raw in TOKEN_RE.findall(prose) if (t := raw.strip("-'"))]


_SINGULAR_KEEP = ("sis", "us", "is", "ss", "ias")  # 这些结尾不剥 s（analysis/status/basis…）


def _singular(p: str) -> str:
    """朴素单数化：无词典的形态规则，误伤由脚本 B 的变体表兜底；短词与缩写（MAS）豁免。"""
    if len(p) <= 3 or not p.isalpha() or p.endswith(_SINGULAR_KEEP):
        return p
    if p.endswith("yses"):
        return p[:-4] + "ysis"
    if p.endswith("ies"):
        return p[:-3] + "y"
    if p.endswith(("ches", "shes", "xes", "zes")):
        return p[:-2]
    if p.endswith(("ases", "ises", "oses", "uses")):
        return p[:-1]
    if p.endswith("ses"):
        return p[:-2]
    if p.endswith("s"):
        return p[:-1]
    return p


def norm_word(w: str) -> str:
    """单词归一化：小写、连字符转空格（让 controller-level 与 controller level 同键）、
    逐子词朴素单数化——计数与变体分组统一用这个键。"""
    parts = [p for p in w.lower().replace("'", "").replace("-", " ").split() if p]
    return " ".join(_singular(p) for p in parts)


def norm_key(words: list[str]) -> str:
    return " ".join(norm_word(w) for w in words)


def norm_tokens(tokens: list[str]) -> list[str]:
    return [norm_word(t) for t in tokens]


def segments(tokens: list[str]) -> list[list[str]]:
    """按停用词切段，段内连续词即候选短语（RAKE 式）。大小写不敏感匹配停用词。"""
    segs, cur = [], []
    for tok in tokens:
        if tok.lower() in STOPWORDS or len(tok) < 2:
            if cur:
                segs.append(cur)
                cur = []
        else:
            cur.append(tok)
    if cur:
        segs.append(cur)
    return segs


def load_blacklist(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8") as f:
        return {row["word"].lower(): row["type"] for row in csv.DictReader(f) if row.get("word")}


def load_wordlist(path: Path) -> set[str]:
    return {w.strip().lower() for w in path.open(encoding="utf-8") if w.strip()}


def load_whitelist_keys(path: Path) -> set[str]:
    keys = set()
    for line in path.open(encoding="utf-8"):
        line = re.sub(r"^[\s\-\*\d\.\)]+", "", line).strip()
        if not line or line.startswith(("#", "```")):
            continue
        words = [w for w in (t.strip("-'").lower() for t in TOKEN_RE.findall(line)) if w]
        if words:
            keys.add(norm_key(words))
    return keys


def count_phrase(normed: list[str], words: list[str]) -> int:
    n, count = len(words), 0
    target = [norm_word(w) for w in words]
    for i in range(len(normed) - n + 1):
        if normed[i : i + n] == target:
            count += 1
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manuscript", nargs="+", help="手稿 .tex 文件（可多个）")
    ap.add_argument("--baseline", default=None, help='基线语料 glob（你自己已发表的 .tex/.txt），如 "published/*.tex"')
    ap.add_argument("--whitelist", default=None, help="术语表白名单文件（项目自定义命名），强烈建议")
    ap.add_argument("--top", type=int, default=60, help="输出候选上限（默认 60）")
    ap.add_argument("--min-count", type=int, default=2, help="最低出现次数（默认 2）")
    ap.add_argument("--batch-size", type=int, default=20, help="审计批量（默认 20/批）")
    ap.add_argument("--json", default=None, help="JSON 输出路径")
    ap.add_argument("--md", default=None, help="markdown 输出路径（缺省 stdout）")
    args = ap.parse_args()

    files = [Path(p) for p in args.manuscript]
    missing = [str(p) for p in files if not p.exists()]
    if missing:
        print(f"文件不存在: {', '.join(missing)}", file=sys.stderr)
        return 2

    full_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in files)
    zones = structural_zones(full_text)
    prose_raw = tokenize(clean_latex(full_text))
    prose_normed = norm_tokens(prose_raw)
    zone_normed = {k: norm_tokens(tokenize(v)) for k, v in zones.items()}

    blacklist = load_blacklist(DATA_DIR / "excess_words.csv")
    common_words = load_wordlist(DATA_DIR / "common_words_10k.txt")
    whitelist_keys = load_whitelist_keys(Path(args.whitelist)) if args.whitelist else set()

    baseline_normed: list[str] = []
    if args.baseline:
        for bf in [Path(x) for x in sorted(glob.glob(args.baseline))]:
            baseline_normed += norm_tokens(tokenize(clean_latex(bf.read_text(encoding="utf-8", errors="replace"))))

    # 候选生成：段内 1..4 词组。段切在原始小写流上（保住大小写做展示形态），
    # 计数键走归一化（norm_key），两者按词序一一对应。
    cand: dict[str, dict] = {}
    for seg in segments(prose_raw):
        normed_seg = [norm_word(w) for w in seg]
        for size in range(1, min(4, len(seg)) + 1):
            for i in range(len(seg) - size + 1):
                key = " ".join(normed_seg[i : i + size])
                surface = " ".join(seg[i : i + size])
                entry = cand.setdefault(key, {"freq": 0, "forms": Counter(), "words": seg[i : i + size]})
                entry["freq"] += 1
                entry["forms"][surface] += 1

    # C-value 式嵌套去重：候选 X 的所有出现都落在更长候选 Y 内部（freq_Y >= freq_X）时不单列
    def is_nested(key: str, freq: int) -> bool:
        for other, oe in cand.items():
            if other != key and oe["freq"] >= freq and f" {key} " in f" {other} ":
                return True
        return False

    whitelisted = 0
    rows = []
    for key, entry in cand.items():
        words = entry["words"]
        lower_words = [w.lower() for w in words]
        style_hits = sorted({w for w in lower_words if blacklist.get(w) == "style"})
        content_hits = sorted({w for w in lower_words if blacklist.get(w) == "content"})
        if entry["freq"] < args.min_count and not (len(words) == 1 and style_hits):
            continue
        if key in whitelist_keys:
            whitelisted += 1
            continue
        # 黑名单侧道词不做嵌套抑制：style 词落在短语内部也是 AI 味指纹
        if not style_hits and (is_nested(key, entry["freq"]) or len(words) == 1):
            continue
        generic_ratio = round(sum(w in common_words for w in lower_words) / len(words), 2)
        structural = [z for z, toks in zone_normed.items() if count_phrase(toks, words) > 0]
        baseline_count = count_phrase(baseline_normed, words) if baseline_normed else None

        score = 0.0
        if len(words) >= 2:
            score += 3
            score += 2 * generic_ratio
        # 单词 style 命中是侧道主信号；短语内命中只是旁证，防止一个虚词带飞整个短语
        if style_hits:
            score += 3 if len(words) == 1 else 1.5
        elif content_hits:
            score += 1
        if "title" in structural or "abstract" in structural:
            score += 2
        elif structural:
            score += 1
        if baseline_count is not None:
            score += 2 if baseline_count == 0 else 0
        score += min(1.0, entry["freq"] / 10)

        rows.append({
            "term": key,
            "display": entry["forms"].most_common(1)[0][0],
            "forms": dict(entry["forms"].most_common(3)),
            "freq": entry["freq"],
            "n_words": len(words),
            "generic_ratio": generic_ratio,
            "blacklist_style": style_hits,
            "blacklist_content": content_hits,
            "structural": structural,
            "baseline_count": baseline_count,
            "score": round(score, 2),
        })

    rows.sort(key=lambda r: (-r["score"], -r["freq"]))
    rows = rows[: args.top]
    for i, r in enumerate(rows):
        r["batch"] = i // args.batch_size + 1

    meta = {
        "manuscript": [str(p) for p in files],
        "baseline": args.baseline,
        "whitelist": args.whitelist,
        "baseline_tokens": len(baseline_normed),
        "prose_tokens": len(prose_normed),
        "candidates_seen": len(cand),
        "whitelisted_excluded": whitelisted,
        "reported": len(rows),
        "batches": (len(rows) + args.batch_size - 1) // args.batch_size if rows else 0,
        "batch_size": args.batch_size,
    }

    def sig_col(r: dict) -> str:
        parts = [f"f{r['freq']}"]
        if r["structural"]:
            parts.append("S:" + "+".join(r["structural"]))
        if r["blacklist_style"]:
            parts.append("BL:" + ",".join(r["blacklist_style"]))
        if r["blacklist_content"]:
            parts.append("bc:" + ",".join(r["blacklist_content"]))
        parts.append(f"G{r['generic_ratio']}")
        if r["baseline_count"] is not None:
            parts.append("基线0" if r["baseline_count"] == 0 else f"基线{r['baseline_count']}")
        return " ".join(parts)

    lines = [
        "# term-audit 候选术语表",
        "",
        f"- 手稿：{', '.join(meta['manuscript'])}",
        f"- 基线语料：{meta['baseline'] or '未提供（基线缺席信号未启用）'}"
        + (f"（{meta['baseline_tokens']} 词元）" if baseline_normed else ""),
        f"- 白名单：{meta['whitelist'] or '未提供'}（命中排除 {whitelisted} 条）",
        f"- 散文词元 {meta['prose_tokens']}，候选 {meta['candidates_seen']}，报告前 {meta['reported']} 条，切 {meta['batches']} 批",
        "",
        "| 批 | 候选术语 | 信号 | 得分 |",
        "|---|---|---|---|",
    ]
    lines += [f"| {r['batch']} | {r['display']} | {sig_col(r)} | {r['score']} |" for r in rows]
    lines += [
        "",
        "信号图例：f=频次，S:title/abstract/section=结构位置，BL=style 黑名单词，bc=content 黑名单词，G=日常词拼接比，基线N=基线语料出现次数（基线0 即基线缺席）。",
        "批次按得分降序切分：批 1 最优先。送审工单模板见 SKILL.md。",
    ]
    md = "\n".join(lines) + "\n"

    if args.md:
        Path(args.md).write_text(md, encoding="utf-8")
    else:
        print(md, end="")
    if args.json:
        Path(args.json).write_text(
            json.dumps({"meta": meta, "candidates": rows}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

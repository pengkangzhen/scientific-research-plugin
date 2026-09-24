#!/usr/bin/env python3
"""term-audit 第三步：对提取结果做归一化变体分组，供合并者复查术语漂移。

用法:
  uv run group_variants.py cand.json --json variants.json --md variants.md

纯 stdlib。两件事（确定性，零模型）：
1. 表面变体簇——同一归一化键的多种写法（大小写/连字符/单复数差异），
   如 "SOP-MAS orchestration" vs "SOP MAS orchestration"，是机械性漂移铁证；
2. 同族短语对——不同键但共享 2+ 词（按序子序列）的候选，如
   "resilience index" vs "network resilience index"，提示合并者注意语义漂移。
语义层漂移（"test cases" vs "error analyses"）不在本脚本能力内，归合并者 LLM。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from itertools import combinations
from pathlib import Path


def dehyphen(s: str) -> str:
    return re.sub(r"[\-\s]+", " ", s.lower()).strip()


def _singular(p: str) -> str:
    """与 extract_terms._singular 保持一致的朴素单数化（companies→company 等）。"""
    if len(p) <= 3 or not p.isalpha() or p.endswith(("sis", "us", "is", "ss", "ias")):
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


def classify_diff(forms: list[str]) -> list[str]:
    """对同键多形态分类差异来源。"""
    lower = [f.lower() for f in forms]
    diffs = []
    if len(set(lower)) < len(lower):
        diffs.append("大小写")
    dehyph = {dehyphen(f) for f in forms}
    if len(dehyph) < len(set(lower)):
        diffs.append("连字符/空格")
    stripped = {re.sub(r"[^a-z0-9 ]", "", f.lower()) for f in forms}
    if len(stripped) < len(set(lower)):
        diffs.append("标点/撇号")
    singular = set()
    for f in stripped:
        words = [_singular(w) for w in f.split()]
        singular.add(" ".join(words))
    if len(singular) < len(stripped):
        diffs.append("单复数")
    return diffs or ["未知差异"]


def shared_subsequence(a: list[str], b: list[str]) -> list[str]:
    """最长公共连续子序列（词级）。"""
    best: list[str] = []
    for i in range(len(a)):
        for j in range(len(b)):
            k = 0
            while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]:
                k += 1
            if k > len(best):
                best = a[i : i + k]
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cand_json", help="extract_terms.py --json 产出的候选表")
    ap.add_argument("--json", default=None, help="JSON 输出路径")
    ap.add_argument("--md", default=None, help="markdown 输出路径（缺省 stdout）")
    args = ap.parse_args()

    data = json.loads(Path(args.cand_json).read_text(encoding="utf-8"))
    candidates = data["candidates"]

    variant_clusters = []
    for r in candidates:
        forms = list(r.get("forms", {r["display"]: r["freq"]}).keys())
        if len(forms) > 1:
            variant_clusters.append({
                "term": r["term"],
                "batch": r["batch"],
                "forms": r.get("forms", {}),
                "diff": classify_diff(list(r.get("forms", {}).keys()) or forms),
            })

    families = []
    for a, b in combinations(candidates, 2):
        if a["n_words"] == 1 or b["n_words"] == 1:
            continue
        aw, bw = a["term"].split(), b["term"].split()
        shared = shared_subsequence(aw, bw)
        if len(shared) >= 2:
            families.append({
                "pair": [a["display"], b["display"]],
                "shared": " ".join(shared),
                "batches": sorted({a["batch"], b["batch"]}),
            })

    meta = {
        "source": args.cand_json,
        "candidates": len(candidates),
        "variant_clusters": len(variant_clusters),
        "family_pairs": len(families),
    }

    lines = [
        "# term-audit 变体分组表",
        "",
        f"- 来源：{args.cand_json}（{len(candidates)} 条候选）",
        f"- 表面变体簇 **{len(variant_clusters)}** 组（机械性漂移，直接修写法即可）",
        f"- 同族短语对 **{len(families)}** 对（提示合并者注意语义漂移，不是错误）",
        "",
    ]
    if variant_clusters:
        lines += ["## 表面变体簇", "", "| 批 | 归一化键 | 写法（频次） | 差异 |", "|---|---|---|---|"]
        lines += [
            f"| {c['batch']} | `{c['term']}` | " + "；".join(f"{f}（{n}）" for f, n in c["forms"].items())
            + f" | {'、'.join(c['diff'])} |"
            for c in variant_clusters
        ]
        lines.append("")
    if families:
        lines += ["## 同族短语对", "", "| 短语 A | 短语 B | 共享片段 | 批 |", "|---|---|---|---|"]
        lines += [
            f"| {f['pair'][0]} | {f['pair'][1]} | {f['shared']} | {','.join(map(str, f['batches']))} |"
            for f in families
        ]
        lines.append("")
    lines += [
        "用法：表面变体簇交给作者机械统一；同族短语对连同各批判定表交给合并者，"
        "由它判断是否语义漂移（同一概念两套叫法）。",
    ]
    md = "\n".join(lines) + "\n"

    if args.md:
        Path(args.md).write_text(md, encoding="utf-8")
    else:
        print(md, end="")
    if args.json:
        Path(args.json).write_text(
            json.dumps({"meta": meta, "variant_clusters": variant_clusters, "families": families},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

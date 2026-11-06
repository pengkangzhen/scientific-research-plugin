#!/usr/bin/env python3
"""从 ≤2022 年人类中文学术文本构建 AI 腔基线统计量（纯统计，不落盘原文）。

用法 A（推荐：本地全文手稿/往届学位论文/已发表中文论文目录）：
  uv run build_baseline.py --corpus "published_le2022/*.tex" "theses/*.docx" \
      --desc "课题组 ≤2022 中文论文全文" --out ../data/baseline_stats_zh.json

用法 B（补充：OpenAlex 中文期刊 ≤2022 摘要，仅适用于摘要层对照）：
  uv run build_baseline.py --openalex --mailto you@example.com \
      --source-ids S4210224179,S23425967 --max-year 2022 \
      --out ../data/baseline_stats_zh.json

纯 stdlib，复用 scan_tells.py 的解析器与规则引擎。输出字段供 scan_tells.py 自动读取：
mean_per_k / sd_per_k / p50_per_k / p90_per_k / p10_sent_cv / cat_per_k。
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import scan_tells as st  # noqa: E402

OPENALEX_WORKS = "https://api.openalex.org/works"
DEFAULT_SOURCES = "S4210224179,S23425967"  # 软件学报、自动化学报（OpenAlex 含中文摘要的公开源示例）


def percentile(vals: list[float], q: float) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    idx = (len(s) - 1) * q
    lo, hi = int(idx), min(int(idx) + 1, len(s) - 1)
    return s[lo] * (1 - (idx - lo)) + s[hi] * (idx - lo)


def http_json(url: str, retries: int = 4) -> dict:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "academic-writing-toolkit/0.2 (build_baseline.py)"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt + 1 < retries:
                time.sleep(1.5 * (2 ** attempt))
                continue
            raise


def reconstruct_cjk_abstract(inv: dict) -> str:
    pos = {i: tok for tok, idxs in (inv or {}).items() for i in idxs}
    return "".join(
        pos[i] if st.CJK.search(pos[i]) else " " + pos[i]
        for i in sorted(pos)
    ).strip()


def collect_local_docs(patterns: list[str]) -> list[tuple[str, list[st.Para], list]]:
    paths: list[Path] = []
    for pat in patterns:
        p = Path(pat)
        if p.is_dir():
            for ext in ("*.tex", "*.md", "*.txt", "*.docx"):
                paths.extend(sorted(p.rglob(ext)))
        elif any(ch in pat for ch in "*?[]"):
            paths.extend(Path(x) for x in sorted(glob.glob(pat, recursive=True)))
        elif p.exists():
            paths.append(p)
    seen, docs = set(), []
    for path in paths:
        rp = path.resolve()
        if rp in seen or rp.suffix.lower() not in (".tex", ".md", ".markdown", ".txt", ".docx"):
            continue
        seen.add(rp)
        paras, fmt_hits = st.parse(rp)
        docs.append((rp.name, paras, fmt_hits))
    return docs


def collect_openalex_docs(source_ids: str, mailto: str, max_year: int, quota: int) -> tuple[list, list[dict]]:
    sids = "|".join(s.strip() for s in source_ids.split(",") if s.strip())
    docs, meta_rows = [], []
    cursor = "*"
    while len(docs) < quota and cursor:
        params = {
            "filter": f"primary_location.source.id:{sids},has_abstract:true,publication_year:2015-{max_year},type:article",
            "per-page": min(100, quota - len(docs) + 20),
            "cursor": cursor,
            "mailto": mailto,
        }
        data = http_json(OPENALEX_WORKS + "?" + urllib.parse.urlencode(params))
        results = data.get("results") or []
        if not results:
            break
        for w in results:
            if len(docs) >= quota:
                break
            txt = reconstruct_cjk_abstract(w.get("abstract_inverted_index") or {})
            if len(st.CJK.findall(txt)) < 100:
                continue
            wid = (w.get("id") or "").split("/")[-1]
            src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
            docs.append((wid, [st.Para("摘要", txt, [(0, wid)])], []))
            meta_rows.append({
                "id": wid, "doi": w.get("doi"), "title": w.get("title"),
                "venue": src, "year": w.get("publication_year"),
            })
        cursor = (data.get("meta") or {}).get("next_cursor")
        time.sleep(0.8)
    return docs, meta_rows


def summarize(docs: list, rules: list[st.Rule], min_cjk_ratio: float, desc: str, scope: str) -> dict:
    doc_per_k, sec_per_k, sent_cvs = [], [], []
    cat_counts = Counter()
    total_chars = 0

    for _, paras, fmt_hits in docs:
        res = st.scan(paras, fmt_hits, rules, min_cjk_ratio, baseline=None)
        if res["total_chars"] < 80:
            continue
        total_chars += res["total_chars"]
        doc_per_k.append(res["per_k"])
        for sec in res["sections"]:
            if sec["chars"] >= 80:
                sec_per_k.append(sec["per_k"])
            if sec["sent_cv"] is not None and sec["sentences"] >= 5:
                sent_cvs.append(sec["sent_cv"])
        for h in res["hits"]:
            if not h["exempt"] and h["w"] > 0:
                cat_counts[h["cat"]] += 1

    if len(doc_per_k) < 3:
        sys.exit(f"有效中文文档不足 3 篇（当前 {len(doc_per_k)} 篇），无法稳健估计基线分布")

    pool = sec_per_k if len(sec_per_k) >= len(doc_per_k) else doc_per_k
    mean_pk = statistics.mean(pool)
    sd_pk = statistics.pstdev(pool) if len(pool) >= 2 else 1.0
    return {
        "built_on": date.today().isoformat(),
        "source_desc": desc,
        "scope": scope,
        "n_docs": len(doc_per_k),
        "n_sections": len(sec_per_k),
        "total_chars": total_chars,
        "mean_per_k": round(mean_pk, 2),
        "sd_per_k": round(max(sd_pk, 0.5), 2),
        "p50_per_k": round(percentile(pool, 0.50), 2),
        "p90_per_k": round(percentile(pool, 0.90), 2),
        "p10_sent_cv": round(percentile(sent_cvs, 0.10), 2) if sent_cvs else st.CV_FLAT,
        "p50_sent_cv": round(percentile(sent_cvs, 0.50), 2) if sent_cvs else None,
        "cat_per_k": {
            c: round(k / total_chars * 1000, 3)
            for c, k in sorted(cat_counts.items())
        } if total_chars else {},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="从 ≤2022 中文人类学术语料构建 AI 腔基线统计量")
    ap.add_argument("--corpus", nargs="+", help="本地文件/目录/glob（支持 .tex/.md/.txt/.docx）")
    ap.add_argument("--openalex", action="store_true", help="从 OpenAlex 采集 ≤max-year 中文摘要")
    ap.add_argument("--mailto", default="", help="OpenAlex polite pool 邮箱（--openalex 必填）")
    ap.add_argument("--source-ids", default=DEFAULT_SOURCES, help="OpenAlex source ID 逗号列表")
    ap.add_argument("--max-year", type=int, default=2022)
    ap.add_argument("--quota", type=int, default=120)
    ap.add_argument("--papers-out", type=Path, help="可选：保存 OpenAlex 语料元数据 JSONL（不含摘要全文）")
    ap.add_argument("--rules", type=Path, default=st.DEFAULT_RULES)
    ap.add_argument("--min-cjk-ratio", type=float, default=0.3)
    ap.add_argument("--desc", default="")
    ap.add_argument("--out", type=Path, default=st.DEFAULT_BASELINE)
    a = ap.parse_args()

    if not a.corpus and not a.openalex:
        ap.error("请指定 --corpus <本地路径/glob> 或 --openalex")

    rules = st.load_rules(a.rules)
    docs, scope = [], "fulltext"
    if a.corpus:
        docs.extend(collect_local_docs(a.corpus))
    if a.openalex:
        if not a.mailto:
            ap.error("--openalex 需要提供 --mailto 邮箱以遵守 OpenAlex polite pool")
        oa_docs, meta_rows = collect_openalex_docs(a.source_ids, a.mailto, a.max_year, a.quota)
        docs.extend(oa_docs)
        scope = "mixed" if a.corpus else "abstract-only"
        if a.papers_out:
            a.papers_out.write_text(
                "\n".join(json.dumps(r, ensure_ascii=False) for r in meta_rows) + "\n",
                encoding="utf-8",
            )

    desc = a.desc or ("本地语料" if a.corpus and not a.openalex else f"OpenAlex ≤{a.max_year} 中文摘要")
    stats = summarize(docs, rules, a.min_cjk_ratio, desc, scope)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""采集 5 个领域顶刊/顶会论文的元数据与摘要，作为写作句式挖掘语料。

数据源（配置在 ../references/journals.json，唯一事实源）：
  arXiv API    —— AI（cs.LG）、OR（math.OC）
  OpenAlex API —— 管理学（MS/POM/JOM/Omega）、物流（TRE/TRSC/EJOR）、航运（MPM/MTR/TRD/MEL）。
                 走 has_abstract:true 服务端过滤（Crossref 对 Elsevier 系不存摘要，故弃用）。

产出两张表：
  <out>/papers.jsonl    语料清单，入库（事实性元数据：id/title/venue/domain/year/url）
  <raw>/abstracts.jsonl 原始摘要，仅本地中转供 mine_patterns.py 使用，不入库
                        （出版商摘要文本不随仓库分发，data/README.md 有说明）

用法：
  uv run skills/top-journal-writing/scripts/harvest_papers.py \
      --mailto you@example.com --raw /tmp/tjw-harvest

  冒烟测试（每域只取 2 篇）：加 --smoke
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ARXIV_API = "https://export.arxiv.org/api/query?"
OPENALEX_SOURCES = "https://api.openalex.org/sources"
OPENALEX_WORKS = "https://api.openalex.org/works"
ARXIV_PAUSE = 3.1      # arXiv 官方限速：1 次 / 3 秒
OPENALEX_PAUSE = 0.8   # OpenAlex 上限 10 req/s，留余量

# 标题黑名单：剔除非研究论文条目（社论/勘误/书评/目录/审稿人名单等）
TITLE_BLACKLIST = re.compile(
    r"(?i)\b(editorial|editor'?s|corrigendum|erratum|retraction|book review|"
    r"call for papers|guide (for|to) authors|acknowledg\w*|table of contents|"
    r"list of reviewers|referees (for|of)|awards?\b|prize|in this issue|"
    r"forthcoming papers|title page|author index|subject index|"
    r"reply to|response to)\b")

SCRIPT_DIR = Path(__file__).resolve().parent


def http_get(url: str, timeout: int = 60) -> bytes:
  req = urllib.request.Request(
      url, headers={"User-Agent": "academic-writing-toolkit/0.1 (harvest_papers.py)"})
  with urllib.request.urlopen(req, timeout=timeout) as resp:
    return resp.read()


def norm_title(title: str) -> str:
  return re.sub(r"\W+", " ", title.lower()).strip()


def load_config(path: Path) -> dict:
  with open(path, encoding="utf-8") as f:
    cfg = json.load(f)
  return cfg["domains"]


# ---------------------------------------------------------------- arXiv ----

def harvest_arxiv(category: str, label: str, domain: str, quota: int,
                  seen_titles: set, records: list, abstracts: list) -> None:
  params = {
      "search_query": f"cat:{category}",
      "sortBy": "submittedDate",
      "sortOrder": "descending",
      "start": 0,
      "max_results": quota + 20,  # 余量抵消去重损耗
  }
  url = ARXIV_API + urllib.parse.urlencode(params, quote_via=urllib.parse.quote_plus)
  print(f"[arxiv:{domain}] {category} × {quota} …", flush=True)
  root = ET.fromstring(http_get(url))
  ns = "{http://www.w3.org/2005/Atom}"
  got = 0
  for entry in root.findall(f"{ns}entry"):
    if got >= quota:
      break
    rec = {}
    for child in entry:
      tag = child.tag.split("}")[-1]
      if tag == "id" and child.text:
        # http://arxiv.org/abs/2501.04227v2 -> 2501.04227（去版本号，id 稳定）
        rec["id"] = child.text.split("/abs/")[-1].split("v")[0]
      elif tag == "title":
        rec["title"] = re.sub(r"\s+", " ", child.text or "").strip()
      elif tag == "summary":
        rec["abstract"] = re.sub(r"\s+", " ", child.text or "").strip()
      elif tag == "published" and child.text:
        rec["year"] = int(child.text[:4])
    if not all(rec.get(k) for k in ("id", "title", "abstract", "year")):
      continue
    key = norm_title(rec["title"])
    if key in seen_titles:
      continue
    seen_titles.add(key)
    records.append({
        "id": rec["id"], "title": rec["title"], "venue": label,
        "domain": domain, "year": rec["year"], "source": "arxiv",
        "url": f"https://arxiv.org/abs/{rec['id']}",
    })
    abstracts.append({"id": rec["id"], "abstract": rec["abstract"]})
    got += 1
  time.sleep(ARXIV_PAUSE)
  print(f"[arxiv:{domain}] got {got}", flush=True)


# -------------------------------------------------------------- openalex ----

def reconstruct_abstract(inverted: dict) -> str:
  """OpenAlex 摘要倒排索引 {word: [pos]} -> 原文。"""
  positions = {}
  for word, idxs in inverted.items():
    for i in idxs:
      positions[i] = word
  return " ".join(positions[i] for i in sorted(positions))


def resolve_source_id(issn: str) -> tuple[str | None, str | None]:
  """ISSN -> (OpenAlex source id, 实际刊名)。解析失败返回 (None, None)。"""
  url = OPENALEX_SOURCES + "?" + urllib.parse.urlencode(
      {"filter": f"issn:{issn}", "select": "id,display_name,works_count"})
  try:
    results = json.loads(http_get(url, timeout=30)).get("results", [])
    if not results:
      return None, None
    src = results[0]
    return src["id"].rsplit("/", 1)[-1], src.get("display_name", "")
  except Exception as exc:  # noqa: BLE001 —— 单刊失败不阻断整体采集
    print(f"  [warn] ISSN {issn} 解析失败：{exc}", flush=True)
    return None, None


def harvest_openalex_journal(source_id: str, short: str, domain: str, want: int,
                             from_year: int, mailto: str, seen_titles: set,
                             records: list, abstracts: list) -> int:
  got = 0
  page = 1
  while got < want and page <= 3:  # 每页 50，最多翻 3 页防意外
    params = {
        "filter": (f"primary_location.source.id:{source_id},"
                   f"from_publication_date:{from_year}-01-01,type:article,has_abstract:true"),
        "sort": "publication_date:desc",
        "per-page": 50,
        "page": page,
        "select": "doi,title,publication_year,abstract_inverted_index",
    }
    if mailto:
      params["mailto"] = mailto
    url = OPENALEX_WORKS + "?" + urllib.parse.urlencode(params)
    data = json.loads(http_get(url))
    items = data.get("results", [])
    if not items:
      break
    for item in items:
      if got >= want:
        break
      title = item.get("title") or ""
      abstract = reconstruct_abstract(item.get("abstract_inverted_index") or {})
      doi = (item.get("doi") or "").replace("https://doi.org/", "")
      if not title or len(abstract) < 200 or not doi:
        continue
      if TITLE_BLACKLIST.search(title):
        continue
      key = norm_title(title)
      if key in seen_titles:
        continue
      seen_titles.add(key)
      records.append({
          "id": doi, "title": re.sub(r"\s+", " ", title),
          "venue": short, "domain": domain, "year": item.get("publication_year", 0),
          "source": "openalex", "url": f"https://doi.org/{doi}",
      })
      abstracts.append({"id": doi, "abstract": abstract})
      got += 1
    page += 1
    time.sleep(OPENALEX_PAUSE)
  return got


def harvest_openalex_domain(domain: str, spec: dict, quota: int, from_year: int,
                            mailto: str, seen_titles: set, records: list,
                            abstracts: list) -> None:
  per_journal = spec["per_journal"]
  print(f"[openalex:{domain}] quota={quota} …", flush=True)
  remaining = quota
  for j in spec["journals"]:
    if remaining <= 0:
      break
    source_id, actual = resolve_source_id(j["issn"])
    if source_id is None:
      print(f"  [skip] ISSN {j['issn']} 解析不到 OpenAlex 源，跳过（{j['short']}）", flush=True)
      continue
    if j["short"].split()[0].lower() not in actual.lower():
      print(f"  [warn] ISSN {j['issn']} 解析为「{actual}」，配置预期「{j['short']}」——请核对 references/journals.json", flush=True)
    want = min(per_journal, remaining)
    try:
      got = harvest_openalex_journal(
          source_id, j["short"], domain, want, from_year, mailto,
          seen_titles, records, abstracts)
    except Exception as exc:  # noqa: BLE001 —— 单刊失败不阻断整体采集
      print(f"  [skip] {j['short']} 拉取失败：{exc}", flush=True)
      continue
    print(f"  {j['short']:<45} +{got}", flush=True)
    remaining -= got
  if remaining > 0:
    print(f"  [short] {domain} 缺口 {remaining} 篇（期刊摘要量不足）", flush=True)


# ------------------------------------------------------------------ main ----

def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument("--config", default=str(SCRIPT_DIR.parent / "references" / "journals.json"))
  ap.add_argument("--out", default=str(SCRIPT_DIR.parent / "data"))
  ap.add_argument("--raw", default="/tmp/tjw-harvest")
  ap.add_argument("--mailto", default="",
                  help="OpenAlex polite pool 联系邮箱（建议填写）")
  ap.add_argument("--from-year", type=int, default=2019,
                  help="期刊论文发表年份下限（默认 2019，近五年口径）")
  ap.add_argument("--smoke", action="store_true",
                  help="冒烟模式：每域只采 2 篇")
  args = ap.parse_args()

  domains = load_config(Path(args.config))
  out_dir = Path(args.out)
  raw_dir = Path(args.raw)
  out_dir.mkdir(parents=True, exist_ok=True)
  raw_dir.mkdir(parents=True, exist_ok=True)

  records, abstracts = [], []
  seen_titles: set = set()
  for domain, spec in domains.items():
    quota = 2 if args.smoke else spec["quota"]
    if spec["source"] == "arxiv":
      harvest_arxiv(spec["category"], spec["label"], domain, quota,
                    seen_titles, records, abstracts)
    elif spec["source"] == "openalex":
      harvest_openalex_domain(domain, spec, quota, args.from_year,
                              args.mailto, seen_titles, records, abstracts)
    else:
      print(f"[skip] 未知 source：{spec['source']}", flush=True)

  papers_path = out_dir / "papers.jsonl"
  abstracts_path = raw_dir / "abstracts.jsonl"
  with open(papers_path, "w", encoding="utf-8") as f:
    for r in records:
      f.write(json.dumps(r, ensure_ascii=False) + "\n")
  with open(abstracts_path, "w", encoding="utf-8") as f:
    for a in abstracts:
      f.write(json.dumps(a, ensure_ascii=False) + "\n")

  # 汇总报告
  by_domain: dict[str, int] = {}
  by_venue: dict[str, int] = {}
  for r in records:
    by_domain[r["domain"]] = by_domain.get(r["domain"], 0) + 1
    by_venue[f"{r['domain']}/{r['venue']}"] = by_venue.get(f"{r['domain']}/{r['venue']}", 0) + 1
  print("\n=== 采集汇总 ===")
  for d in domains:
    print(f"{d:<10} {by_domain.get(d, 0):>3}")
  print(f"总计 {len(records)} 篇")
  for k in sorted(by_venue):
    print(f"  {k:<60} {by_venue[k]:>3}")
  print(f"\npapers    -> {papers_path}")
  print(f"abstracts -> {abstracts_path}（原始中转，勿入库）")
  return 0


if __name__ == "__main__":
  sys.exit(main())

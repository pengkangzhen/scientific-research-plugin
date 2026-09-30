#!/usr/bin/env python3
"""从采集语料中挖掘顶刊写作句式，产出 data/patterns.jsonl（句式库的语料证据层）。

两级挖掘：
  ① 摘要级（全部 ~200 篇）：句切分 → 按修辞功能分类
     background（背景句）/ gap（缺口句）/ method（方法句）/
     result（结果句）/ implication（意义句）——对应摘要五句公式的五段位。
  ② 全文级（可选，arXiv 子集）：拉取 arXiv HTML 全文，切出 Introduction /
     Conclusion(含 Discussion) 段，挖掘 gap_intro（引言缺口句）、contribution
     （贡献句）、conclusion（收口句）、limitation（局限展望句）——这些句式摘要里没有。

输入：--papers data/papers.jsonl --abstracts /tmp/tjw-harvest/abstracts.jsonl
输出：data/patterns.jsonl，每行 {function, domain, venue, year, id, section, sentence}

用法：
  uv run skills/top-journal-writing/scripts/mine_patterns.py \
      --abstracts /tmp/tjw-harvest/abstracts.jsonl --fulltext 24
"""

import argparse
import json
import re
import sys
import time
import urllib.request
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# ----------------------------------------------------------- 句切分 ----

# 常见缩写占位，防误切（切完还原）
_ABBREV = [
    ("e.g.", "e⁄g⁄"), ("i.e.", "i⁄e⁄"), ("et al.", "et al⁄"),
    ("vs.", "vs⁄"), ("cf.", "cf⁄"), ("etc.", "etc⁄"),
    ("Fig.", "Fig⁄"), ("Figs.", "Figs⁄"), ("Eq.", "Eq⁄"), ("Eqs.", "Eqs⁄"),
    ("Sect.", "Sect⁄"), ("Sec.", "Sec⁄"), ("No.", "No⁄"), ("Nos.", "Nos⁄"),
    ("approx.", "approx⁄"), ("w.r.t.", "w⁄r⁄t⁄"), ("i.i.d.", "i⁄i⁄d⁄"),
    ("U.S.", "U⁄S⁄"), ("U.K.", "U⁄K⁄"), ("Ph.D.", "Ph⁄D⁄"),
]


def split_sentences(text: str) -> list[str]:
  for a, b in _ABBREV:
    text = text.replace(a, b)
  parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"(\[])", text)
  out = []
  for p in parts:
    for a, b in _ABBREV:
      p = p.replace(b, a)
    p = p.strip()
    if p:
      out.append(p)
  return out


# ------------------------------------------------------- 修辞功能分类 ----

GAP_CUE = re.compile(r"(?i)\b(however|nevertheless|nonetheless|yet)\b")
GAP_STRONG = re.compile(
    r"(?i)\b(little (is known|attention|research|has been|is understood)|"
    r"remains? (unclear|unknown|unexplored|underexplored|poorly understood|elusive|"
    r"insufficiently understood|an? open (question|problem|challenge))|"
    r"to the best of our knowledge|"
    r"ha(s|ve) not been (studied|explored|considered|investigated|addressed|examined|exploited)|"
    r"no (prior|previous|existing) (work|study|studies|research|literature|model|method)|"
    r"gap (in the literature|remains)|has received (little|limited|scant) attention|"
    r"(existing|prior|previous|conventional|current) (studies|literature|approaches|methods|models|"
    r"works?|heuristics|algorithms|policies) (often|typically|usually|generally|mainly|largely|tend to)|"
    r"(leads? to|result(s|ing)? in) suboptimal)")
GAP_WEAK = re.compile(
    r"(?i)\b(lacks?|suffer|challeng|difficult|limited|neglect|overlook|"
    r"unexplored|unclear|unknown|barrier|obstacle|incomplete|scarce|insufficient(ly)?|"
    r"cannot|can not|fail(s|ed)? to|degrad\w*|suboptimal|NP-hard|intractable|prohibitive|"
    r"computationally expensive|expensive|time-consuming|ignor\w*|disregard\w*|"
    r"decoupl\w*|curse of dimensionality)\b")

METHOD = re.compile(
    r"(?i)\b(we|this (paper|article|study|research|letter)|in this (paper|work))\s+"
    r"(propose|present|develop|introduce|design|formulate|study|investigate|consider|"
    r"model|build|derive|analyze|analyse|examine|address|aim to|make)\b|"
    r"\bwe (use|employ|apply|adopt|collect|combine|conduct|train|implement|"
    r"characterize|characterise|prove|establish|solve)\b|"
    r"\b(our|the) (model|framework|approach|method|algorithm|heuristic|formulation|"
    r"solution (method|approach)|exact (method|approach)|branch-and-cut|column generation|"
    r"Benders decomposition|matheuristic|metaheuristic)\b")

RESULT_CONTEXT = re.compile(
    r"(?i)\b(results?|findings?|experiments?|experimentation|simulations?|"
    r"computational (experiments|studies)|case studies?|numerical (experiments|studies|results)|"
    r"empirical(ly)? (analysis|evidence|results)|benchmark|ablation|outperform(s|ed|ance)?)\b|"
    r"\d+(\.\d+)?\s?%")
RESULT_SHOW = re.compile(
    r"(?i)\b(show(s|n|ed)?|indicat(e|es|ed)|demonstrat(e|es|ed)|reveal(s|ed)?|"
    r"confirm(s|ed)?|illustrat(e|es|ed)|suggest(s|ed)?|yield(s|ed)?)\b")

IMPLICATION = re.compile(
    r"(?i)\b(insights?|implications?\b|practitioners?|policymakers?|policy ?makers|"
    r"managerial|managers\b|decision ?makers?|guidance for|for (theory|both theory|management|practice)|"
    r"contributes? to (theory|practice|the literature|the field)|shed(s)? light|"
    r"inform(s)? (decisions?|policies|practice|managerial)|have implications|"
    r"offers? (practical|managerial)|practical relevance)\b")

BACKGROUND = re.compile(
    r"(?i)\b(increasingly (important|popular|critical|prevalent|attention)|"
    r"critical(ly)? (role|importance)|play(s|ed)? (a|an) (key|critical|vital|essential|crucial|"
    r"pivotal|central|significant|dominant)|key (component|role|technology|factor|element)|"
    r"essential (for|to|component|part)|vital (for|to)|"
    r"growing (interest|attention|concern|demand|body)|"
    r"has (attracted|received) (considerable|growing|increasing|significant|widespread)|"
    r"widely (used|adopted|applied|employed|studied|recognized)|"
    r"has become (a|an|increasingly)|cornerstone|backbone|indispensable|ubiquitous|"
    r"pervasive|one of the most)\b")

# 全文级功能
CONTRIB = re.compile(
    r"(?i)\b((our|the) (main |key |major |primary |three |principal |main scientific )*contributions?\b|"
    r"the contributions? of (this|our) (paper|work|article|study)|"
    r"we make the following contributions|"
    r"contributions? (are|is) (threefold|three-fold|summarized|as follows)|"
    r"this paper makes (three|several|two|four|\w+) contributions|"
    r"this paper contributes|we highlight|our work (makes|offers|provides)|"
    r"summariz(e|es|ed) our (main |key )?contributions|"
    r"(in summary|in particular),? we (make|present|propose|summarize))\b")
CONCLUSION = re.compile(
    r"(?i)\b(in this (paper|work|article|study),? we (have )?"
    r"(proposed|presented|studied|introduced|developed|formulated|designed|investigated|"
    r"analyzed|characterized|considered))\b")
LIMITATION = re.compile(
    r"(?i)\b(limitations?\b|future (work|research|studies|directions)|warrants? further|"
    r"could be (extended|improved|generalized|relaxed)|"
    r"remains? to be (explored|seen|investigated)|open (question|problem|direction|avenue)|"
    r"avenues? for future|promising direction|further (investigation|exploration))\b")


def sentence_ok(s: str) -> bool:
  if not 40 <= len(s) <= 400:
    return False
  if "?" in s:
    return False
  if not s[0].isupper():
    return False
  # 非 ASCII 占比过高（数学符号堆积）的句子弃用
  non_ascii = sum(1 for c in s if ord(c) > 127)
  return non_ascii / len(s) < 0.3


def classify_abstract_sentence(s: str, idx: int) -> str | None:
  """摘要句 -> 修辞功能。优先级：gap > method > result > implication > background。"""
  if GAP_STRONG.search(s) or (GAP_CUE.search(s) and GAP_WEAK.search(s)):
    return "gap"
  if METHOD.search(s):
    return "method"
  if RESULT_CONTEXT.search(s) and (RESULT_SHOW.search(s) or "outperform" in s.lower()
                                   or re.search(r"\d", s)):
    return "result"
  if IMPLICATION.search(s):
    return "implication"
  if idx == 0 or BACKGROUND.search(s):
    return "background"
  return None


# ------------------------------------------------------- HTML 全文解析 ----

class SectionExtractor(HTMLParser):
  """arXiv HTML (LaTeXML) -> [(标题, 正文)] 列表。"""

  def __init__(self):
    super().__init__()
    self.sections: list[list] = []  # [[header, [text...]], ...]
    self._skip = 0
    self._in_header = False
    self._buf: list[str] = []

  def handle_starttag(self, tag, attrs):
    if tag in ("script", "style", "math"):
      self._skip += 1
    elif tag in ("h1", "h2", "h3", "h4"):
      self._in_header = True
      self._buf = []

  def handle_endtag(self, tag):
    if tag in ("script", "style", "math"):
      self._skip = max(0, self._skip - 1)
    elif tag in ("h1", "h2", "h3", "h4"):
      self._in_header = False
      self.sections.append([" ".join(self._buf).strip(), []])
    elif tag in ("p", "li", "figcaption") and self.sections:
      # 段/列表项边界补句号，防止 <li> 条目拼成超长句
      self.sections[-1][1].append(". ")

  def handle_data(self, data):
    if self._skip:
      return
    if self._in_header:
      self._buf.append(data)
    elif self.sections:
      self.sections[-1][1].append(data)


def fetch_html_sections(arxiv_id: str, timeout: int = 40) -> dict[str, str]:
  """拉取 arXiv HTML，返回 {段名小写: 正文}。失败返回 {}。"""
  url = f"https://arxiv.org/html/{arxiv_id}"
  try:
    req = urllib.request.Request(url, headers={"User-Agent": "academic-writing-toolkit/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
      html = resp.read().decode("utf-8", errors="ignore")
  except Exception:
    return {}
  parser = SectionExtractor()
  try:
    parser.feed(html)
  except Exception:
    return {}
  out = {}
  for header, chunks in parser.sections:
    name = header.lower()
    text = re.sub(r"\s+", " ", " ".join(chunks)).strip()
    if "introduction" in name and "introduction" not in out:
      out["introduction"] = text
    elif re.search(r"conclusion|summary|discussion", name):
      out.setdefault("conclusion", text)
  return out


# ------------------------------------------------------------- 主流程 ----

def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument("--papers", default=str(SCRIPT_DIR.parent / "data" / "papers.jsonl"))
  ap.add_argument("--abstracts", required=True,
                  help="harvest_papers.py 产出的 abstracts.jsonl 路径")
  ap.add_argument("--out", default=str(SCRIPT_DIR.parent / "data" / "patterns.jsonl"))
  ap.add_argument("--fulltext", type=int, default=24,
                  help="arXiv HTML 全文挖掘的论文数（0 关闭；ai/or 各取一半）")
  ap.add_argument("--cap", type=int, default=40,
                  help="每个 (function, domain) 组合保留的最大句数")
  args = ap.parse_args()

  papers = [json.loads(l) for l in open(args.papers, encoding="utf-8")]
  abstracts = {json.loads(l)["id"]: json.loads(l)["abstract"]
               for l in open(args.abstracts, encoding="utf-8")}

  patterns: list[dict] = []
  seen_norm: set = set()
  counts: dict[tuple, int] = defaultdict(int)

  def keep(function: str, paper: dict, section: str, sentence: str) -> None:
    if not sentence_ok(sentence):
      return
    key = re.sub(r"\W+", "", sentence.lower())[:80]
    if key in seen_norm:
      return
    if counts[(function, paper["domain"])] >= args.cap:
      return
    seen_norm.add(key)
    counts[(function, paper["domain"])] += 1
    patterns.append({
        "function": function, "domain": paper["domain"], "venue": paper["venue"],
        "year": paper["year"], "id": paper["id"], "section": section,
        "sentence": sentence,
    })

  # ① 摘要级挖掘
  for p in papers:
    abstract = abstracts.get(p["id"])
    if not abstract:
      continue
    for idx, sent in enumerate(split_sentences(abstract)):
      if idx > 25:  # 个别刊把全文存成"摘要"，只取前 26 句防单篇刷爆
        break
      func = classify_abstract_sentence(sent, idx)
      if func:
        keep(func, p, "abstract", sent)

  # ② 全文级挖掘（arXiv 子集）
  if args.fulltext > 0:
    arxiv_papers = [p for p in papers if p["source"] == "arxiv"]
    half = args.fulltext // 2
    per_domain = {"ai": 0, "or": 0}
    picked = []
    for p in arxiv_papers:  # papers 序即新到旧
      d = p["domain"]
      if per_domain.get(d, 0) < half:
        per_domain[d] = per_domain.get(d, 0) + 1
        picked.append(p)
    ok = 0
    for p in picked:
      sections = fetch_html_sections(p["id"])
      if not sections:
        print(f"[fulltext] {p['id']} 无 HTML，跳过", flush=True)
        time.sleep(3)
        continue
      ok += 1
      if "introduction" in sections:
        for sent in split_sentences(sections["introduction"]):
          if CONTRIB.search(sent):
            keep("contribution", p, "introduction", sent)
          elif GAP_STRONG.search(sent) or (GAP_CUE.search(sent) and GAP_WEAK.search(sent)):
            keep("gap_intro", p, "introduction", sent)
      if "conclusion" in sections:
        for ci, sent in enumerate(split_sentences(sections["conclusion"])):
          # 收口句：正则命中，或结论段首句以 We/In 开头的总结式陈述
          if CONCLUSION.search(sent) or (ci == 0 and re.match(r"(?i)^(We|In) ", sent)):
            keep("conclusion", p, "conclusion", sent)
          elif LIMITATION.search(sent):
            keep("limitation", p, "conclusion", sent)
      print(f"[fulltext] {p['id']} ok ({ok}/{len(picked)})", flush=True)
      time.sleep(3)

  with open(args.out, "w", encoding="utf-8") as f:
    for rec in patterns:
      f.write(json.dumps(rec, ensure_ascii=False) + "\n")

  # 汇总
  by_func: dict[str, int] = defaultdict(int)
  for rec in patterns:
    by_func[rec["function"]] += 1
  print(f"\n=== 句式挖掘汇总（{len(patterns)} 句）===")
  funcs = ["background", "gap", "method", "result", "implication",
           "gap_intro", "contribution", "conclusion", "limitation"]
  domains = ["ai", "or", "mgmt", "logistics", "shipping"]
  header = f"{'function':<14}" + "".join(f"{d:>10}" for d in domains) + f"{'total':>8}"
  print(header)
  for fn in funcs:
    row = f"{fn:<14}" + "".join(f"{counts.get((fn, d), 0):>10}" for d in domains)
    print(row + f"{by_func.get(fn, 0):>8}")
  print(f"\npatterns -> {args.out}")
  return 0


if __name__ == "__main__":
  sys.exit(main())

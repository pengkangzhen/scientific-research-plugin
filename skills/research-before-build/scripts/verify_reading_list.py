#!/usr/bin/env python3
"""Machine-verify every paper in a memo's reading list against official APIs.

Usage: verify_reading_list.py <memo.md>

Layer-1 mechanical check in the reference-verifying doctrine: every Papers
entry's DOI is resolved via api.crossref.org, every arXiv ID via the arXiv
export API — facts, not model recall. Exits:
  0  every ID resolves
  1  at least one ID does not resolve (fix the entry, do not ship it)
  2  network unreachable for some IDs (retry later; do not treat as verified)

Honors https_proxy/HTTPS_PROXY environment variables.
"""
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

DOI = re.compile(r"\b(10\.\d{4,9}/[^\s;,\)]+)")
ARXIV = re.compile(r"arXiv:?\s*(\d{4}\.\d{4,5})(?:v\d+)?", re.I)
TIMEOUT = 20


def fetch(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "research-before-build/0.1 (memo verification)"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def check_doi(doi: str):
    try:
        status, body = fetch(f"https://api.crossref.org/works/{urllib.request.quote(doi)}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None  # resolved authoritatively: does not exist
        raise
    title = ""
    try:
        title = json.loads(body)["message"]["title"][0][:90]
    except (ValueError, KeyError, IndexError):
        pass
    return title


def check_arxiv(arxiv_id: str):
    status, body = fetch(
        "https://export.arxiv.org/api/query?id_list=" + arxiv_id + "&max_results=1"
    )
    if "<entry" not in body or "Error" in body.split("<entry", 1)[1][:400]:
        return None
    m = re.search(r"<title>(.*?)</title>", body.split("<entry", 1)[1], re.S)
    return m.group(1).strip().replace("\n", " ")[:90] if m else ""


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit("usage: verify_reading_list.py <memo.md>")
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    if "- Papers:" in text:
        papers = text.split("- Papers:", 1)[1].split("- Repos:", 1)[0]
    else:
        papers = ""
    first, *rest = papers.split("\n", 1)
    entries = ["- " + first.strip()] if first.strip() else []
    entries += [l for l in (rest[0].splitlines() if rest else []) if l.strip().startswith("- ")]

    results, unreachable, broken = [], 0, 0
    for line in entries:
        doi = DOI.search(line)
        arxiv = ARXIV.search(line)
        ident = doi.group(1).rstrip(".") if doi else (arxiv.group(1) if arxiv else None)
        if not ident:
            results.append(("NO-ID", "", line.strip()[:80]))
            broken += 1
            continue
        try:
            title = check_doi(ident) if doi else check_arxiv(ident)
            if title is None:
                results.append(("MISSING", ident, line.strip()[:80]))
                broken += 1
            else:
                results.append(("OK", ident, title))
        except Exception as e:
            results.append(("UNREACHABLE", ident, str(e)[:60]))
            unreachable += 1

    for verdict, ident, note in results:
        mark = {"OK": "✓", "MISSING": "✗", "NO-ID": "✗", "UNREACHABLE": "?"}[verdict]
        print(f"  {mark} {verdict:12s} {ident or '-':40s} {note}")
    print(
        f"\n{len(entries)} entr{'y' if len(entries)==1 else 'ies'}: "
        f"{len(entries)-broken-unreachable} ok, {broken} broken, {unreachable} unreachable"
    )
    if broken:
        return 1
    if unreachable:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

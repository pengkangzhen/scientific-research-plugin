#!/usr/bin/env python3
"""Structural linter for prior-art memos (SKILL.md Step 5 contract).

Usage: lint_memo.py <memo.md>

Hard checks (exit 1 on violation):
  - title line "## Prior-art memo — <topic>, <date>"
  - Scope searched / Evaluation / Decision lines present
  - all three origin sections present (engineering / academic / cross-domain);
    an empty section must say so explicitly — "(empty" or "empty —", because
    an empty section is a finding, not an omission
  - Decision says "adopt" or "none applicable"
  - Reading list has Papers and Repos channels
  - every Papers entry carries a DOI or arXiv ID
  - every Repos entry carries a URL and a license marker
"""
import re
import sys
from pathlib import Path

DOI = re.compile(r"\b10\.\d{4,9}/\S+")
ARXIV = re.compile(r"arXiv:?\s*\d{4}\.\d{4,5}", re.I)
URL = re.compile(r"https?://\S+")
LICENSE = re.compile(
    r"\b(MIT|Apache|GPL|AGPL|BSD|MPL|LGPL|ISC|Unlicense|license|licence)\b", re.I
)
EMPTY_MARK = re.compile(r"\(empty|empty —|— empty|none reported", re.I)

SECTIONS = [
    ("Engineering side", "  - Engineering side"),
    ("Academic side", "  - Academic side"),
    ("Cross-domain side", "  - Cross-domain side"),
]


def bullet_entries(text: str, header: str) -> list[str]:
    """Bullet lines under `header` until the next section header or top bullet.

    Section headers are short-indent bullets ending in ':'; entries are any
    deeper or equal bullet lines that do not end in ':'.
    """
    out, capture = [], False
    for line in text.splitlines():
        if line.startswith(header):
            capture = True
            continue
        if not capture or not line.strip():
            continue
        if line.startswith(("#", "- ")) or re.match(r"^\s{0,2}- [^:]+:$", line):
            break  # next section header or a top-level bullet
        if line.lstrip().startswith("-"):
            out.append(line)
    return out


def channel_entries(text: str, marker: str, end: str | None = None) -> list[str]:
    """Bullet entries of a reading-list channel. split() eats the marker's
    '- ' prefix, so the marker line's own remainder is re-prefixed — an
    entry on the marker line must not escape checking."""
    block = text.split(marker, 1)[1]
    if end and end in block:
        block = block.split(end, 1)[0]
    first, *rest = block.split("\n", 1)
    entries = ["- " + first.strip()] if first.strip() else []
    entries += [l for l in (rest[0].splitlines() if rest else []) if l.strip().startswith("- ")]
    return entries


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit("usage: lint_memo.py <memo.md>")
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    problems = []

    if not re.search(r"^## Prior-art memo — .+, \d{4}-\d{2}-\d{2}", text, re.M):
        problems.append("missing/dated title line: '## Prior-art memo — <topic>, <date>'")
    for required in ("- Scope searched", "- Evaluation", "- Decision", "- Reading list"):
        if required not in text:
            problems.append(f"missing section: {required!r}")
    if not re.search(r"^- Decision:.*(adopt|none applicable)", text, re.M | re.I):
        problems.append("Decision must say 'adopt …' or 'none applicable …'")

    for name, header in SECTIONS:
        if header not in text:
            problems.append(f"missing origin section: {name}")
            continue
        entries = bullet_entries(text, header)
        if not entries and not EMPTY_MARK.search(
            text.split(header, 1)[1].split("\n- ", 1)[0]
        ):
            problems.append(f"section {name} has no entries and no explicit empty finding")

    if re.search(r"^\s*- Papers:", text, re.M):
        entries = channel_entries(text, "- Papers:", "- Repos:")
        if not entries:
            problems.append("Papers channel is empty — either list papers or drop to repos-only with a note")
        for line in entries:
            if not (DOI.search(line) or ARXIV.search(line)):
                problems.append(f"paper entry without DOI/arXiv ID: {line.strip()[:80]}")
    else:
        problems.append("missing 'Papers:' channel in the reading list")

    if re.search(r"^\s*- Repos:", text, re.M):
        entries = channel_entries(text, "- Repos:")
        for line in entries:
            if not URL.search(line):
                problems.append(f"repo entry without URL: {line.strip()[:80]}")
            if not LICENSE.search(line):
                problems.append(f"repo entry without license marker: {line.strip()[:80]}")
    else:
        problems.append("missing 'Repos:' channel in the reading list")

    if problems:
        print(f"lint FAILED ({len(problems)} problem(s)):")
        for p in problems:
            print(f"  ✗ {p}")
        return 1
    print("✓ memo structure OK — sections, channels, IDs, URLs, licenses all present")
    return 0


if __name__ == "__main__":
    sys.exit(main())

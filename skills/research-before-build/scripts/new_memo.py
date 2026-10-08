#!/usr/bin/env python3
"""Scaffold a dated prior-art memo under docs/research/.

Usage: new_memo.py <topic-slug>   (from the project root)

Creates docs/research/<yyyy-mm-dd>-<topic-slug>.md pre-filled with the
Step 5 template (scope / three origin sections / evaluation / decision /
reading list). Refuses to overwrite. The scaffold intentionally FAILS
lint_memo.py until filled in — that is by design.
"""
import sys
import datetime
from pathlib import Path

TEMPLATE = """## Prior-art memo — {slug}, {date}
- Scope searched (both dimensions, both directions, per line): engineering — ; academic — ; horizontal —
- Candidates — three sections by origin, assembled from the two scout memos; each section ranked by relevance within:
  - Engineering side (vertical line's engineering track — ready-made code, official docs, tools):
  - Academic side (vertical line's academic track — in-field papers, white papers):
  - Cross-domain side (horizontal line's essence-statement hits, paper or repo, each tagged with its borrowed-from field):
- Evaluation (draws on all three sections; adopted pieces often come from different sides — code from engineering, method from cross-domain):
- Decision: (adopt X and adapt (reason) / "none applicable, implement ourselves (checked X/Y/Z, none satisfies constraint N)")
- Reading list (the minimal deliverable; papers and repos are its two acquisition channels, drawn from all three sections):
  - Papers: title — DOI / arXiv ID — venue, year → hand to `zotero-paper-fetching`; cross-domain hits append borrowed-from field + adaptation delta
  - Repos: name — URL — version/commit to pin — license — stars, last release → adoption means dependency or clone; the pinned version is the provenance record
"""


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        sys.exit("usage: new_memo.py <topic-slug>")
    slug = sys.argv[1].strip().lower().replace(" ", "-")
    date = datetime.date.today().isoformat()
    path = Path("docs/research") / f"{date}-{slug}.md"
    if path.exists():
        sys.exit(f"refusing to overwrite: {path} already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TEMPLATE.format(slug=slug, date=date), encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

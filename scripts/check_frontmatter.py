#!/usr/bin/env python3
"""Strict frontmatter guard for the whole repo.

Scans every git-tracked file starting with a `---` fence and strict-parses
its frontmatter with yaml.safe_load; SKILL.md descriptions must also fit the
1024-char skill limit. Some distribution frontends parse frontmatter strictly
and reject bad scalars (e.g. ": " inside a plain single-line scalar), so
nothing ships until every fence parses.

Exit 0 = all pass; exit 1 prints one line per failure.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    # No system PyYAML: re-exec under uv with an ephemeral dependency.
    try:
        os.execvp("uv", ["uv", "run", "--with", "pyyaml", "python3", __file__])
    except FileNotFoundError:
        sys.exit("neither PyYAML nor uv found — install uv to run this guard")

FRONT = re.compile(r"^---\n(.*?)\n---\n", re.S)
DESCRIPTION_LIMIT = 1024  # Claude Code skill-description hard limit


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    tracked = subprocess.run(
        ["git", "-C", root, "ls-files"], capture_output=True, text=True, check=True
    ).stdout.splitlines()

    checked, failures = 0, []
    for rel in tracked:
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if not text.startswith("---\n"):
            continue
        checked += 1
        try:
            match = FRONT.match(text)
            if not match:
                raise ValueError("no closing '---' fence")
            data = yaml.safe_load(match.group(1))
            if not isinstance(data, dict):
                raise ValueError(f"frontmatter is {type(data).__name__}, not a mapping")
            if path.name == "SKILL.md":
                n_chars = len(str(data.get("description") or ""))
                if n_chars > DESCRIPTION_LIMIT:
                    raise ValueError(
                        f"description is {n_chars} chars, over the {DESCRIPTION_LIMIT} limit"
                    )
        except (ValueError, yaml.YAMLError) as e:
            mark = getattr(e, "problem_mark", None)
            loc = f" @ line {mark.line + 1}, col {mark.column + 1}" if mark else ""
            failures.append(f"{rel}: {getattr(e, 'problem', None) or e}{loc}")

    if failures:
        print("frontmatter check FAILED:", file=sys.stderr)
        for failure in failures:
            print(f"  ✗ {failure}", file=sys.stderr)
        return 1
    print(f"✓ frontmatter: {checked} file(s) parse cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())

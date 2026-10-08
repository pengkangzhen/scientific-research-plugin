#!/usr/bin/env python3
"""Mechanical health check for a GitHub repo candidate (Step 4 facts).

Usage: check_repo.py <owner/name | https://github.com/owner/name> [--json]

Fetches from the GitHub REST API, as facts rather than memory: stars, last
push, archived flag, license, default branch HEAD (the pin), latest release.
Optional GITHUB_TOKEN env raises the rate limit above 60/h. Exit 0 always
unless the request itself fails (exit 2) — this is a fact-finder, not a
gate; the trust/freshness/migration judgement stays with Step 4.
"""
import json
import os
import re
import sys
import urllib.request

API = "https://api.github.com"
TIMEOUT = 20


def fetch(path: str):
    headers = {
        "User-Agent": "research-before-build/0.1 (repo candidate check)",
        "Accept": "application/vnd.github+json",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(API + path, headers=headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status, json.loads(resp.read().decode())


def parse_target(arg: str) -> str:
    m = re.search(r"github\.com/([^/\s]+/[^/\s#?]+)", arg)
    if m:
        return m.group(1).rstrip("/")
    if re.fullmatch(r"[\w.\-]+/[\w.\-]+", arg):
        return arg
    sys.exit(f"cannot parse a repo out of: {arg!r}")


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv
    if len(args) != 1:
        sys.exit("usage: check_repo.py <owner/name | url> [--json]")
    full = parse_target(args[0])

    status, repo = fetch(f"/repos/{full}")
    default_branch = repo.get("default_branch", "main")
    pin = None
    try:
        _, commit = fetch(f"/repos/{full}/commits/{default_branch}")
        pin = commit.get("sha", "")[:12]
    except Exception:
        pass
    release = None
    try:
        _, rel = fetch(f"/repos/{full}/releases/latest")
        release = rel.get("tag_name")
    except Exception:
        pass

    license_id = (repo.get("license") or {}).get("spdx_id", "?")
    facts = {
        "repo": full,
        "stars": repo.get("stargazers_count"),
        "pushed_at": repo.get("pushed_at"),
        "archived": repo.get("archived"),
        "license": license_id,
        "pin": f"{default_branch}@{pin}" if pin else None,
        "latest_release": release,
    }
    flags = []
    if repo.get("archived"):
        flags.append("ARCHIVED — maintenance gate fails")
    if as_json:
        print(json.dumps(facts, indent=2))
    else:
        for key, value in facts.items():
            print(f"  {key:15s} {value}")
        for flag in flags:
            print(f"  ⚠ {flag}")
        print(f"\n  judgement (trust/freshness/migration) stays with Step 4")
    return 0


if __name__ == "__main__":
    sys.exit(main())

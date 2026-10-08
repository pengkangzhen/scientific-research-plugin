#!/usr/bin/env python3
"""research-before-build gate hooks — the Claude Code enforcement layer.

One file, three modes, wired in hooks/hooks.json:

  gate      UserPromptExpansion(/research-before-build) and PreToolUse(Skill):
            write the session survey marker. The invocation IS the gate.
  budget    PreToolUse(WebSearch): enforce the survey budget — per scout
            line (agent_id) and global (8), counted from the marker on.
            Scouts are always gated; main-session searches count only while
            the marker is fresh (MARKER_TTL_S), so unrelated later work in
            the same session is untouched.
  dispatch  PreToolUse(Task|Agent): structurally validate research-scout
            work orders (the five fields of SKILL.md's dispatch protocol)
            and cap each line at its initial order plus one re-issue.
  close     PostToolUse(Write): writing the memo (docs/research/*.md)
            closes the survey — budget counting stops, later searches in
            the session are normal work again.

State: one JSON file per session under RESEARCH_GATE_STATE (defaults to
${CLAUDE_PLUGIN_DATA}, then /tmp/research-gate), keyed by session_id.
Fail-open on internal errors: a broken gate degrades to the prompt-layer
discipline in SKILL.md, never bricks the session. Allow-paths emit no
decision (normal permission flow untouched); only denies speak.

Budget semantics: the hook enforces ceilings (LINE_BUDGET_CAP per scout,
GLOBAL_BUDGET overall); the work order's own N is the operative slice —
the hook never loosens it, only catches runs past the ceiling.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

GLOBAL_BUDGET = 8
LINE_BUDGET_CAP = 4  # ceiling per scout agent; the work order's N may be lower
MARKER_TTL_S = 3 * 3600  # main-session budget-counting window after invocation
MAX_DISPATCHES_PER_LINE = 2  # initial work order + one re-issue (SKILL.md Step 3)

WORK_ORDER_FIELDS = [
    ("Direction", r"^\s*Direction:.*\b(vertical|horizontal)\b"),
    ("Questions", r"^\s*Questions"),
    ("Retrieval strategy", r"^\s*Retrieval strategy"),
    ("Constraints", r"^\s*Constraints"),
    ("Budget", r"^\s*Budget"),
]

SKILL_NAME = "research-before-build"


def state_dir() -> Path:
    base = (
        os.environ.get("RESEARCH_GATE_STATE")
        or os.environ.get("CLAUDE_PLUGIN_DATA")
        or "/tmp/research-gate"
    )
    p = Path(base)
    p.mkdir(parents=True, exist_ok=True)
    return p


def marker_path(session_id: str) -> Path:
    return state_dir() / f"{session_id}.json"


def load_marker(session_id: str):
    try:
        with marker_path(session_id).open() as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def save_marker(session_id: str, marker: dict) -> None:
    tmp = marker_path(session_id).with_suffix(".tmp")
    with tmp.open("w") as f:
        json.dump(marker, f)
    tmp.replace(marker_path(session_id))


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def read_input() -> dict:
    try:
        return json.load(sys.stdin)
    except ValueError:
        return {}


def is_our_skill(inp: dict) -> bool:
    tool_input = inp.get("tool_input") or {}
    for key in ("command", "skill", "name", "command_name"):
        value = tool_input.get(key) or inp.get(key) or ""
        if isinstance(value, str) and value.strip().strip("/") == SKILL_NAME:
            return True
    return False


def active_marker(session_id: str):
    marker = load_marker(session_id)
    if marker and not marker.get("closed"):
        return marker
    return None


def mode_gate() -> None:
    inp = read_input()
    session_id = inp.get("session_id")
    if not session_id or not is_our_skill(inp):
        return
    # every invocation starts a fresh survey — counters reset, closed cleared
    marker = {
        "topic": (inp.get("prompt") or "")[:200],
        "opened": time.time(),
        "dispatches": {},
        "searches": {},
        "searches_global": 0,
    }
    try:
        save_marker(session_id, marker)
    except OSError:
        pass  # fail-open: marker loss degrades to prompt-layer budgeting


def mode_close() -> None:
    inp = read_input()
    session_id = inp.get("session_id")
    file_path = (inp.get("tool_input") or {}).get("file_path") or ""
    if not session_id or not re.search(r"docs/research/.*\.md$", file_path):
        return
    marker = load_marker(session_id)
    if marker and not marker.get("closed"):
        marker["closed"] = time.time()
        try:
            save_marker(session_id, marker)
        except OSError:
            pass


def mode_budget() -> None:
    inp = read_input()
    session_id = inp.get("session_id")
    agent_id = inp.get("agent_id")
    agent_type = inp.get("agent_type")
    if not session_id:
        return
    marker = active_marker(session_id)

    if agent_type == "research-scout":
        if not marker:
            deny(
                "research-scout may only search inside an active "
                "/research-before-build survey — no session marker found."
            )
        used = marker.get("searches", {}).get(agent_id, 0)
        if used >= LINE_BUDGET_CAP:
            deny(
                f"line budget ceiling reached ({LINE_BUDGET_CAP} searches for this "
                "scout): report the memo with what you have — 'budget exhausted', "
                "no self-approved extras, no borrowing from the other line."
            )
        if marker.get("searches_global", 0) >= GLOBAL_BUDGET:
            deny(
                f"global survey budget ({GLOBAL_BUDGET}) exhausted — stop searching; "
                "the main session ranks candidates and writes the memo (Step 5)."
            )
        marker.setdefault("searches", {})[agent_id] = used + 1
        marker["searches_global"] = marker.get("searches_global", 0) + 1
        try:
            save_marker(session_id, marker)
        except OSError:
            pass
        return

    if agent_id:  # some other subagent searching — not ours to gate
        return
    if not marker or time.time() - marker.get("opened", 0) > MARKER_TTL_S:
        return  # no active survey: normal permission flow
    if marker.get("searches_global", 0) >= GLOBAL_BUDGET:
        deny(
            f"global survey budget ({GLOBAL_BUDGET}) exhausted — rank what you have "
            "and write the memo (Step 5); or, if this search is unrelated to the "
            "survey, say so in one line and continue after the survey closes."
        )
    marker["searches_global"] = marker.get("searches_global", 0) + 1
    try:
        save_marker(session_id, marker)
    except OSError:
        pass


def mode_dispatch() -> None:
    inp = read_input()
    session_id = inp.get("session_id")
    tool_input = inp.get("tool_input") or {}
    if tool_input.get("subagent_type") != "research-scout":
        return
    if not session_id:
        return
    marker = active_marker(session_id)
    if not marker:
        deny(
            "research-scout may only be dispatched inside an active "
            "/research-before-build survey — no session marker found."
        )
    prompt = tool_input.get("prompt") or ""
    import re

    missing = [
        name
        for name, pattern in WORK_ORDER_FIELDS
        if not re.search(pattern, prompt, re.M)
    ]
    if missing:
        deny(
            "work order incomplete — missing: "
            + ", ".join(missing)
            + ". Fill every field of the dispatch protocol (SKILL.md Step 3); "
            "the scout needs the full slice, not a sketch."
        )
    direction = "vertical" if re.search(r"^\s*Direction:.*vertical", prompt, re.M) else "horizontal"
    dispatches = marker.get("dispatches", {})
    if dispatches.get(direction, 0) >= MAX_DISPATCHES_PER_LINE:
        deny(
            f"{direction} line exhausted: one re-issue is allowed and already used — "
            "declare the line empty (an empty memo is input to the comparison) and "
            "rank what you have (Step 4)."
        )
    dispatches[direction] = dispatches.get(direction, 0) + 1
    marker["dispatches"] = dispatches
    try:
        save_marker(session_id, marker)
    except OSError:
        pass


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if mode == "gate":
            mode_gate()
        elif mode == "budget":
            mode_budget()
        elif mode == "dispatch":
            mode_dispatch()
        elif mode == "close":
            mode_close()
    except Exception:  # fail-open: never brick the session on a hook bug
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()

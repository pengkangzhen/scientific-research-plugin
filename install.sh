#!/usr/bin/env bash
# Install scientific-research-plugin:
#   skills/*  -> ~/.agents/skills/<name>   (auto-triggered skills)
#   agents/*  -> ~/.agents/agents/<name>   (explicitly invoked subagents)
#   skills/*  -> <harness>/skills/<name>   (fan-out for harnesses that do NOT
#                 read ~/.agents/skills: Cursor, Crush, Copilot, Amp, Grok,
#                 Qwen, Droid, Kiro)
# Harnesses reading ~/.agents/skills natively (Gemini CLI, Goose, opencode,
# Kimi Code, pi) need no extra link. Idempotent: re-running relinks stale
# links; refuses to overwrite real directories (resolve manually with diff,
# then remove and re-run).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

link_group() {
  local src_dir="$1" dst_dir="$2" kind="$3"
  mkdir -p "$dst_dir"
  for src in "$src_dir"/*; do
    [ -e "$src" ] || continue
    local name
    name="$(basename "$src")"
    local dst="$dst_dir/$name"
    if [ -L "$dst" ]; then
      local current
      current="$(readlink "$dst")"
      if [ "$current" = "$src" ]; then
        echo "✓ $kind $name: already linked"
      else
        ln -sfn "$src" "$dst"
        echo "→ $kind $name: relinked (was $current)"
      fi
    elif [ -e "$dst" ]; then
      echo "✗ $kind $name: $dst exists and is not a symlink; diff against $src, remove it, re-run" >&2
      return 1
    else
      ln -s "$src" "$dst"
      echo "+ $kind $name: linked"
    fi
  done
}

link_group "$REPO_ROOT/skills" "${HOME}/.agents/skills" "skill"
link_group "$REPO_ROOT/agents" "${HOME}/.agents/agents" "agent"

# Fan out to harnesses with their own skills directory: name:marker:target.
# Only touched when the harness looks installed (marker dir exists), so $HOME
# stays clean; after installing a new harness, just re-run this script.
FANOUT_TARGETS=(
  "cursor:${HOME}/.cursor:${HOME}/.cursor/skills"
  "crush:${HOME}/.config/crush:${HOME}/.config/crush/skills"
  "copilot:${HOME}/.copilot:${HOME}/.copilot/skills"
  # Amp's own config marks it installed, but it reads user-level skills from ~/.config/agents/skills.
  "amp:${HOME}/.config/amp:${HOME}/.config/agents/skills"
  "grok:${HOME}/.grok:${HOME}/.grok/skills"
  "qwen:${HOME}/.qwen:${HOME}/.qwen/skills"
  "droid:${HOME}/.factory:${HOME}/.factory/skills"
  "kiro:${HOME}/.kiro:${HOME}/.kiro/skills"
)

for target in "${FANOUT_TARGETS[@]}"; do
  harness="${target%%:*}"
  rest="${target#*:}"
  marker_dir="${rest%%:*}"
  skills_dir="${rest#*:}"
  if [ -d "$marker_dir" ]; then
    link_group "$REPO_ROOT/skills" "$skills_dir" "skill/$harness"
  else
    echo "- $harness: not found (no $marker_dir), skipped"
  fi
done
echo "Done. Harnesses beyond the fan-out list: halter sync --apply"

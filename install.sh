#!/usr/bin/env bash
# Install academic-research-plugin:
#   skills/*  -> ~/.agents/skills/<name>   (auto-triggered skills)
#   agents/*  -> ~/.agents/agents/<name>   (explicitly invoked subagents)
# Idempotent: re-running relinks stale links; refuses to overwrite real
# directories (resolve manually with diff, then remove and re-run).
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
echo "Done. Distribute to all harnesses with: halter sync --apply"

# Scientific Research Plugin

**English** | [简体中文](README.zh-CN.md)

Every task is a piece of research — not just papers. A discipline layer (`research-before-build`) brings prior-art surveying to any project; the paper pipeline — literature acquisition → structured reading → paper figures → writing polish → pre-submission review → rebuttal → conference presentation — is its fullest instantiation. Built for OR / ML+OR / supply-chain researchers.

One `skills/` source of truth, distributed to multiple frontends: the Claude Code / ZCode plugin, the Codex plugin, and any assistant that supports `~/.agents/skills` (via halter).

## Research Pipeline

| Stage | Skill / Agent | Form | In one sentence |
|---|---|---|---|
| ⓪ Survey | `research-before-build` | skill | Discipline layer, fires on **any** non-trivial task: L0–L3 graded trigger — check human prior art (official docs / mature libraries / GitHub issues / literature) before building; decides *whether and what* to research |
| ① Retrieve | `zotero-paper-fetch` | skill | Reference list → CrossRef enrichment → Zotero intake → tiered PDF download (OA direct links / repository anti-crawler / campus-VPN paywalls) |
| ② Read | `zotero-paper-note` | skill | Zotero item → deep read → structured notes written back to Zotero + `literature.jsonl` |
| ③ Experiment | `figure-plot` | skill | Figure contract → Times New Roman / colorblind-safe palette → vector PDF with embedded-font verification; data plots + schematic diagrams |
| ④ Write | `paper-polish` | skill | LaTeX language polishing that preserves all markup; ships with a jargon-audit follow-up |
| ④ Write | `jargon-check` | **subagent** | Isolated-context, independent-model jargon audit — a stranger-reviewer perspective that avoids same-model blind spots |
| ⑤ Pre-submit | `paper-review` | skill | Three-blind adversarial panel: 3 isolated reviewers (methodology rigor / domain contribution / adversarial attack) → author-defense arbitration → cross-review synthesis; claim-evidence anchoring, journal-profile axes, C/M/N issue list feeds `rebuttal`. Domain-agnostic engine with gates detected per manuscript and composed freely (built-in: OR families, ML+OR, LLM/agents; extensible) |
| ⑥ Rebut | `rebuttal` | skill | Locate each reviewer comment → confirm the revision plan → `\changed{}` markup → compile the PDF → update the response letter |
| ⑦ Present | `academic-ppt` | skill | Paper (LaTeX/PDF) → Beamer deck with a visual design system (official-template extraction or self-built) → time-budgeted talk script → compliant pptx packaging with speaker notes |

### Discipline Layer vs. Pipeline Layer

- **Discipline layer (⓪)**: `research-before-build` fires on any non-trivial task — coding, deployment, architecture selection — not only papers. It is the pack's worldview: prior art before building, search graded by risk, sources accepted by trust, verified by decision impact.
- **Pipeline layer (①–⑦)**: the paper lifecycle, the discipline's most complete instantiation — from a reference list to the conference talk.

⓪ → ① is a hand-off, not containment: `research-before-build` decides *whether and what* to survey; `zotero-paper-fetch` acquires the decided references into Zotero.

### Skill vs. Subagent

- **skill**: triggered automatically by its description, runs in the main conversation — suited to workflow orchestration (retrieval, polishing, review, rebuttal).
- **subagent**: invoked explicitly by name, runs in an isolated session — suited to audits that need an outsider's perspective (the core value of `jargon-check`: a different model in a different context, built to catch the writing model's wording blind spots).

## Installation

### Option 1: Plugin (Claude Code / Codex / ZCode)

Claude Code:

```bash
claude plugin install pengkangzhen/scientific-research-plugin
```

Codex — enable in `~/.codex/config.toml`:

```toml
[plugins."scientific-research-plugin@scientific-research-plugin"]
enabled = true
```

ZCode — this repository doubles as its own plugin marketplace (`.claude-plugin/marketplace.json`, source resolves to the repo root):

1. Clone the repo locally and take its root path.
2. Plugin Marketplace → Add → Add Plugin Marketplace, paste the repo root directory.
3. Personal → scientific-research-plugin → Scientific Research Plugin → Install.

The `jargon-check` subagent is not part of the ZCode plugin package (ZCode plugin manifests currently declare skills / commands / hooks / MCP servers, not subagents) — run `./install.sh` if you need it there.

### Option 2: Bare install (works with every assistant)

```bash
git clone https://github.com/pengkangzhen/scientific-research-plugin.git
cd scientific-research-plugin
./install.sh          # skills/agents -> ~/.agents/{skills,agents}, idempotent
halter sync --apply   # optional: fan out to all installed assistants
```

## Repository Layout

```
├── skills/                      # 8 auto-triggered skills (single source of truth)
│   ├── research-before-build/
│   ├── zotero-paper-fetch/
│   ├── zotero-paper-note/
│   ├── figure-plot/
│   ├── paper-polish/
│   ├── paper-review/
│   ├── rebuttal/
│   └── academic-ppt/
├── attic/                       # retired skills, kept for provenance
│   └── academic-paper-review/   # 7-agent journal-review simulation (upstream: academic-research-skills)
├── agents/
│   └── jargon-check.md          # isolated-audit subagent
├── .claude-plugin/
│   ├── plugin.json              # Claude Code plugin manifest
│   └── marketplace.json         # Claude Code / ZCode marketplace catalog (source ./)
├── .zcode-plugin/plugin.json    # ZCode plugin manifest
├── .codex-plugin/plugin.json    # Codex plugin manifest
├── .agents/plugins/marketplace.json  # Codex (~/.agents) marketplace catalog
└── install.sh                   # bare-install fallback
```

## Maintenance Conventions

- Edit skills in this repo only; `install.sh` creates symlinks — local changes take effect immediately, and pushing publishes them.
- Version bumps touch all three plugin manifests (`.claude-plugin/`, `.zcode-plugin/`, `.codex-plugin/`) and the `.claude-plugin/marketplace.json` entry in lockstep.
- `academic-paper-review` is retired into `attic/` (upstream: academic-research-skills); its useful mechanisms (fatal-flaw criteria, red flags, Devil's-Advocate attack dimensions) live on inside `paper-review`. See `skills/paper-review/references/source-basis.md` for full provenance.
- This repo is v4: v1 contained only 4 writing skills; v2 expanded to a research pipeline and evolved `language-polish` into `paper-polish`; v3 added the discipline layer `research-before-build` (⓪) and `academic-ppt` (⑦) and renamed `scientific-review` to `paper-review`; v4 rebuilds `paper-review` as a three-blind adversarial panel (nature-reviewer-style architecture, OR/ML+OR domain gates, author-defense arbitration) and retires `academic-paper-review` — 8 skills + 1 subagent.

## License

MIT

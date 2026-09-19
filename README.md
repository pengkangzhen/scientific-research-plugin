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
| ⑤ Pre-submit | `scientific-review` | skill | Three-role adversarial review: Reviewer challenges → Author defends → Judge rules |
| ⑤ Pre-submit | `academic-paper-reviewer` | skill | Five-reviewer (EIC + 3 domain reviewers + Devil's Advocate) full journal-review simulation |
| ⑥ Rebut | `rebuttal` | skill | Locate each reviewer comment → confirm the revision plan → `\changed{}` markup → compile the PDF → update the response letter |
| ⑦ Present | `academic-ppt` | skill | Paper (LaTeX/PDF) → Beamer deck with a visual design system (official-template extraction or self-built) → time-budgeted talk script → compliant pptx packaging with speaker notes |

### Discipline Layer vs. Pipeline Layer

- **Discipline layer (⓪)**: `research-before-build` fires on any non-trivial task — coding, deployment, architecture selection — not only papers. It is the pack's worldview: prior art before building, search graded by risk, sources accepted by trust, verified by decision impact.
- **Pipeline layer (①–⑦)**: the paper lifecycle, the discipline's most complete instantiation — from a reference list to the conference talk.

⓪ → ① is a hand-off, not containment: `research-before-build` decides *whether and what* to survey; `zotero-paper-fetch` acquires the decided references into Zotero.

### Skill vs. Subagent

- **skill**: triggered automatically by its description, runs in the main conversation — suited to workflow orchestration (retrieval, polishing, review, rebuttal).
- **subagent**: invoked explicitly by name, runs in an isolated session — suited to audits that need an outsider's perspective (the core value of `jargon-check`: a different model in a different context, built to catch the writing model's wording blind spots).

### Choosing Between the Two Review Skills

| | `scientific-review` | `academic-paper-reviewer` |
|---|---|---|
| Origin | Self-built | Upstream [academic-research-skills](https://github.com/), original name kept for easier upstream sync |
| Mechanism | Reviewer/Author/Judge three-role adversarial | 5-reviewer multi-role simulation |
| Positioning | Single-dimension scientific check, focused on OR/ML+OR | Full journal review workflow, cross-domain |
| Weight | 32K, quick daily use | 336K, full pre-submission pass |

## Installation

### Option 1: Plugin (Claude Code / ZCode)

```bash
claude plugin install pengkangzhen/scientific-research-plugin
```

On the Codex side, enable it in `~/.codex/config.toml`:

```toml
[plugins."scientific-research-plugin@scientific-research-plugin"]
enabled = true
```

### Option 2: Bare install (works with every assistant)

```bash
git clone https://github.com/pengkangzhen/scientific-research-plugin.git
cd scientific-research-plugin
./install.sh          # skills/agents -> ~/.agents/{skills,agents}, idempotent
halter sync --apply   # optional: fan out to all installed assistants
```

## Repository Layout

```
├── skills/                      # 9 auto-triggered skills (single source of truth)
│   ├── research-before-build/
│   ├── zotero-paper-fetch/
│   ├── zotero-paper-note/
│   ├── figure-plot/
│   ├── paper-polish/
│   ├── scientific-review/
│   ├── academic-paper-reviewer/
│   ├── rebuttal/
│   └── academic-ppt/
├── agents/
│   └── jargon-check.md          # isolated-audit subagent
├── .claude-plugin/plugin.json   # Claude Code / ZCode plugin manifest
├── .codex-plugin/plugin.json    # Codex plugin manifest
├── .agents/plugins/marketplace.json
└── install.sh                   # bare-install fallback
```

## Maintenance Conventions

- Edit skills in this repo only; `install.sh` creates symlinks — local changes take effect immediately, and pushing publishes them.
- `academic-paper-reviewer` has an upstream; diff against it before major changes. All other skills are self-developed and iterate freely.
- This repo is v3: v1 contained only 4 writing skills (scientific-review / language-polish / jargon-check / rebuttal); v2 expanded to a full research pipeline of 7 skills + 1 subagent and evolved `language-polish` into `paper-polish` (adding the jargon-audit section); v3 adds the discipline layer `research-before-build` (⓪) and the presentation stage `academic-ppt` (⑦) — 9 skills + 1 subagent, repositioned from a paper toolkit to "every task is research".

## License

MIT

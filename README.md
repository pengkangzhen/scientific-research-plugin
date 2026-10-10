# Scientific Research Plugin

**English** | [简体中文](README.zh-CN.md)

![License](https://img.shields.io/badge/license-MIT-green)
![Skills](https://img.shields.io/badge/skills-16_+_2_subagents-blue)
![Harnesses](https://img.shields.io/badge/harnesses-16-orange)

Every research task starts with prior art — not just papers. A survey skill (`research-before-build`) checks prior art across engineering and academic sources for research-grade questions before you build; the paper pipeline — literature acquisition → structured reading → paper figures → section drafting → writing polish → defensive-writing sweep → reference verification → pre-submission review → rebuttal → conference presentation and poster — is its fullest instantiation. Built for OR & ML researchers.

One `skills/` source of truth, distributed to multiple frontends: the Claude Code / ZCode / Codex plugins, the assistants that read `~/.agents/skills` natively (Gemini CLI, Goose, opencode, Kimi Code, pi), and the harness-specific directories that `install.sh` fans out to (Cursor, Crush, Copilot, Amp, Grok Build, Qwen Code, Droid, Kiro).

## Highlights

- **Full lifecycle in one pack.** From a raw reference list to the conference talk and poster: Zotero intake → structured reading notes → note-driven PDF highlighting → journal-grade figures → top-journal-style section drafting → LaTeX polishing → noun-term jargon sweep → defensive-writing sweep → citation audit → adversarial pre-submission review → point-by-point rebuttal → venue-transfer loop (submission snapshot, rejection triage, journal resubmission) with `dear-editor` typesetting the cover letter and title page at every submission → timed Beamer deck → single-page visual derivatives (poster, graphical abstract, announcement card). 16 skills + 2 subagents designed as one pipeline, not sixteen loose utilities.
- **Facts over model recall.** `reference-verifying` fetches citation facts from official APIs (CrossRef / arXiv / PMLR / OpenReview / ACL Anthology / NeurIPS) — commands, not memory. Undecidable entries get web checks whose evidence must carry accessible URLs, and every adverse finding is independently re-checked.
- **Outsider audits, not self-grading.** `paper-review` runs three mutually isolated reviewers (methodology rigor / domain contribution / adversarial attack) plus author-defense arbitration — the failure mode it targets is a model grading its own output. `jargon-check` goes further: an isolated subagent on an independent model reads the polished text as a stranger would.
- **A survey skill for research-grade questions, not just paper tools.** `research-before-build` runs where prior art spans both engineering and academic venues — method and solution design, "has humanity studied X", architecture choices for research systems. It is user-invoked (`/research-before-build`) — the invocation itself is the scope gate, so the skill never re-triages what you asked it to survey; inside, it dispatches two parallel `research-scout` subagents, one digging vertically within the field, one sweeping horizontally across fields, each covering GitHub-grade and paper-grade sources. Routine engineering unknowns — library picks, integrations, deployment, debugging, security — stay with the harness's native search. The paper pipeline is its fullest instantiation, not its boundary.
- **Skills that hand off.** `paper-review`'s C/M/N issue list feeds `rebuttal` directly; `paper-polishing` ships a jargon-audit follow-up; `research-before-build` hands the decided reading list to `zotero-paper-fetching`; `rebuttal` hands rejected manuscripts to `venue-transfer`, which re-selects the next venue from the recorded rejection drivers (rejection comments are never absorbed), flips the narrative, and re-enters the pipeline at submission — its two one-pagers typeset by `dear-editor`. The chain is designed, not incidental.
- **One source of truth, 16 frontends.** A single `skills/` tree serves three plugin marketplaces (Claude Code, ZCode, Codex), five harnesses reading `~/.agents/skills` natively (Gemini CLI, Goose, opencode, Kimi Code, pi), and eight more via idempotent fan-out (Cursor, Crush, Copilot, Amp, Grok Build, Qwen Code, Droid, Kiro). Symlinks only; `$HOME` stays clean.
- **OR & ML depth, domain-agnostic engine.** Built by a supply-chain-resilience researcher: `figure-plotting` ships recipes for Pareto fronts, network topologies and convergence curves with embedded-font verification; `paper-review` detects domain gates per manuscript (OR families, ML+OR, LLM/agents) and composes freely beyond them.

## Research Pipeline

| Skill / Agent | Form | In one sentence |
|---|---|---|
| ⓪ `research-before-build` | skill | User-invoked (`/research-before-build`) prior-art survey before building — engineering venues (docs, GitHub repos) and academic venues (papers) both always, via two parallel `research-scout` subagents digging one vertical and one horizontal line |
| ① `zotero-paper-fetching` | skill | Searches the web for relevant literature, completes metadata, downloads PDFs, and files them into your Zotero library in tiers |
| ② `zotero-paper-note` | skill | Close-reads papers one by one into structured notes, written back to the Zotero items |
| ② `zotero-pdf-highlighting` | skill | Writes the reading note's five categories back onto the PDF as color-coded highlights (red question / yellow model / green method / blue case / purple results) |
| ③ `figure-plotting` | skill | Designs figures from your manuscript with built-in scientific color schemes, exported as high-resolution vector graphics |
| ④ `top-journal-writing` | skill | Drafts or restructures sections to top-journal blueprints — intro funnel, five-sentence abstract, recipe-style methods, four-step discussion — with a sentence bank mined from 200 top-venue papers |
| ④ `paper-polishing` | skill | Academic LaTeX polishing: grammar, word choice, syntax, logic and tone — five dimensions to publication-ready |
| ④ `jargon-check` | **subagent** | Targets the "AI accent" and academic buzzwords of AI writing — audits stock phrases in an isolated context |
| ④ `term-audit` | skill | Batch noun-term jargon funnel: deterministic candidate extraction + five-signal ranking → parallel `jargon-check` `terms`-mode batches → variant grouping + drift merger |
| ④ `hedge-audit` | skill | Whole-manuscript defensive-writing (over-hedging) audit: escape clauses after Results, contribution-weakening hedges in Abstract/Intro, hedge stacking anywhere, caveats duplicating Limitations — section-conditional verdicts (delete / move-to-Discussion / move-to-Limitations / keep) + hedge-density gradient |
| ⑤ `paper-review` | skill | Three isolated reviewers + author-defense arbitration, outputting a C/M/N issue list |
| ⑤ `reference-verifying` | skill | Verifies citations against official APIs — machine checks, not model memory — to prevent hallucinated references |
| ⑥ `rebuttal` | skill | Revises the manuscript point by point against reviewer comments, keeping the response letter in sync |
| ⑥′ `venue-transfer` | skill | Manages the loop between submissions: candidate-journal sheet → venue-targeted rewrite → upload-time snapshot (git tag + submission log) → rejection triage (desk vs. review; comments never absorbed — they feed venue re-selection only) → narrative flip for the next venue |
| ⑥″ `dear-editor` | skill | Typesets the editor-facing one-pagers — cover letter and title page — from public slot templates with git-ignored personal copies carrying the frozen identity; hard one-page compile gates; invoked by `venue-transfer` at every submission event or directly at a first submission |
| ⑦ `slide-making` | skill | Turns your paper into a conference presentation deck or a thesis-proposal/defense Beamer |
| ⑧ `poster-making` | skill | Turns your paper into single-page visual derivatives: a conference poster (official-template / beamerposter / tikzposter / HTML routes), a journal graphical abstract to publisher pixel specs, and a social-media announcement card — plus Xiaohongshu multi-image note cards with optional auto-publish (Python/uv xhs pipeline) — one content-compression pipeline, four canvases |

### Survey Layer vs. Pipeline Layer

- **Survey layer (⓪)**: `research-before-build` serves research-grade prior-art questions — solution and method design, "has humanity studied/solved X", architecture selection for research systems — not routine engineering unknowns (the harness's native search covers those) nor settled-path execution. It is the pack's worldview: prior art before building, and not just in your own field — strip the domain jargon and ask whether humanity has ever solved a structurally similar problem; research questions pinned down from the task description and the repo's AGENTS.md, retrieval dimension — engineering (docs, issues, mature repos) and academic (papers), both always — retrieval direction — vertical within the field and horizontal across fields as two co-primary lines dispatched in parallel as `research-scout` subagents — and retrieval strategy: queries built by the facet-split + relaxation-ladder method, candidates ranked by structural match, verified by decision impact.
- **Pipeline layer (①–⑧)**: the paper lifecycle, the survey skill's most complete instantiation — from a reference list to the conference talk, poster, and announcement card.

⓪ → ① is a hand-off, not containment: `research-before-build` decides *whether and what* to survey; `zotero-paper-fetching` acquires the decided references into Zotero.

### Skill vs. Subagent

- **skill**: triggered automatically by its description, runs in the main conversation — suited to workflow orchestration (retrieval, polishing, review, rebuttal).
- **subagent**: runs in an isolated session, dispatched explicitly rather than auto-triggered. Two jobs justify the isolation: outsider audits (`jargon-check` — a different model in a different context, built to catch the writing model's wording blind spots) and parallel research lines (`research-scout` — `research-before-build` dispatches them in pairs for research-grade questions, one digging vertically within the field, one sweeping horizontally across fields, each with its own budget slice; isolation buys parallelism and keeps raw search noise out of the main context).

## Usage: Just Say It

Skills auto-trigger from their descriptions — no slash commands to memorize — with one deliberate exception: heavyweight, budget-spending skills are gated behind explicit invocation. `research-before-build` is user-invoked (`/research-before-build`): invoke it when you want to know how a problem has been solved before you build; if a task graduates to research-grade mid-execution, the assistant proposes the skill and you decide. Two subagents sit outside that flow: `jargon-check`, which you invoke by name so the audit runs outside the conversation that wrote the text, and `research-scout`, which `research-before-build` dispatches in parallel pairs for research-grade questions — you never invoke it yourself.

| You say | What fires | What you get |
|---|---|---|
| "How has anyone quantified geopolitical risk in logistics networks?" | `/research-before-build` | prior-art memo — engineering and academic candidates, ranked by structural match |
| "Add these 30 references to Zotero and download the PDFs" | `zotero-paper-fetching` | metadata-enriched Zotero items, PDFs filed by publisher |
| "Read this paper and take structured notes" | `zotero-paper-note` | note written back to the Zotero item + `literature.jsonl` |
| "Color-code this PDF by its reading note" | `zotero-pdf-highlighting` | five-category color highlights embedded in the PDF + page-by-page report |
| "Plot the Pareto front / the supply-network topology" | `figure-plotting` | vector PDF, Times New Roman, embedded fonts |
| "Draft the Introduction in top-journal style" / "restructure this abstract" | `top-journal-writing` | section skeleton by blueprint + sentences from a sourced pattern bank |
| "Polish the Introduction" | `paper-polishing` | edited LaTeX, all markup untouched |
| "Audit the wording" (after polishing) | `jargon-check` — by name | outsider-perspective jargon audit |
| "Audit every noun term in the manuscript" | `term-audit` | ranked candidate table, batched verdict reports, variant/drift table |
| "Check my Results for defensive writing" / "is the whole manuscript over-hedged" | `hedge-audit` | per-hit verdict table + relocation map + per-section hedge density |
| "Verify every reference before I submit" | `reference-verifying` | field-level audit table with severity grades |
| "Review this manuscript the way reviewers would" | `paper-review` | 3-reviewer panel report + C/M/N issue list |
| "Draft point-by-point responses to the reviews" | `rebuttal` | `\changed{}` markup, compiled PDF, updated letter |
| "Desk-rejected — where do we send it next" / "resubmit to another journal" / "set up the submission snapshot" | `venue-transfer` | candidate-journal sheet, flip rewrite, tagged snapshot, submission-log row |
| "Make the cover letter and title page for this submission" | `dear-editor` | two one-page PDFs from frozen templates, compile-gated |
| "Turn this paper into a 15-minute talk" | `slide-making` | Beamer deck, timed script, speaker notes |
| "Make the conference poster for this paper" / "I need a graphical abstract for submission" / "Make an announcement card for the new paper" / "Turn this into a Xiaohongshu note" | `poster-making` | A0 poster (vector PDF + PNG), spec-compliant graphical abstract, 16:9 card, RedBook card set (cover + auto-paginated, optional auto-publish) |

## Installation

**Pick the path by where you work:**

- You use **Claude Code, Codex, or ZCode** → Option 1, the plugin — installed and managed by your plugin client.
- You use **any other Agent Skills-compatible harness**, or several at once → Option 2, `install.sh` — one symlink hub plus per-harness fan-out; `$HOME` stays clean.
- **Gemini CLI, Goose, opencode, Kimi Code, pi** read `~/.agents/skills` natively, so Option 2 alone covers them.

### Option 1: Plugin (Claude Code / Codex / ZCode)

Claude Code — this repo doubles as its own marketplace, so add it first, then install:

```bash
claude plugin marketplace add pengkangzhen/scientific-research-plugin
claude plugin install scientific-research-plugin@scientific-research-plugin
```

Codex — add the marketplace, then enable in `~/.codex/config.toml`:

```bash
codex plugin marketplace add pengkangzhen/scientific-research-plugin
```

```toml
[plugins."scientific-research-plugin@scientific-research-plugin"]
enabled = true
```

ZCode — this repository doubles as its own plugin marketplace (`.claude-plugin/marketplace.json`, source resolves to the repo root):

1. Clone the repo locally and take its root path.
2. Plugin Marketplace → Add → Add Plugin Marketplace, paste the repo root directory.
3. Personal → scientific-research-plugin → Scientific Research Plugin → Install.

The plugin package carries both subagents (`jargon-check`, `research-scout`) in its `agents/` directory; harnesses that do not load plugin agents get them via `./install.sh` into `~/.agents/agents`.

### Option 2: Skills install (any Agent Skills-compatible harness)

```bash
git clone https://github.com/pengkangzhen/scientific-research-plugin.git
cd scientific-research-plugin
./install.sh          # idempotent: ~/.agents/{skills,agents} + per-harness fan-out
```

Verify:

```bash
ls ~/.agents/skills    # the 16 skills
ls ~/.agents/agents    # the subagents (jargon-check, research-scout)
```

`install.sh` links everything into `~/.agents/skills` — the Agent Skills open-standard location (the format Anthropic open-sourced in Dec 2025, now adopted by 40+ tools) — and fans out to harnesses that use their own directory. Fan-out only touches harnesses detected as installed, so `$HOME` stays clean; after installing a new harness, re-run `./install.sh`.

| Harness | Skills location | Picked up via |
|---|---|---|
| Gemini CLI | `~/.agents/skills` (alias of `~/.gemini/skills`) | native; or `gemini skills install <repo> --path skills` |
| Goose | `~/.agents/skills` | native |
| opencode | `~/.agents/skills` (also reads `~/.claude/skills`) | native |
| Kimi Code | `~/.agents/skills` or `~/.config/agents/skills` (also reads `~/.kimi`, `~/.claude`, `~/.codex`) | native |
| pi | `~/.agents/skills` (project: `.agents/skills`) | native |
| Cursor | `~/.cursor/skills` | fan-out |
| Crush | `~/.config/crush/skills` | fan-out |
| GitHub Copilot CLI | `~/.copilot/skills` | fan-out; `gh skill` (preview) installs from GitHub |
| Amp | `~/.config/agents/skills` (project: `.agents/skills`) | fan-out, detects `~/.config/amp` |
| Grok Build | `~/.grok/skills` (project: `.grok/skills`) | fan-out |
| Qwen Code | `~/.qwen/skills` | fan-out |
| Droid | `~/.factory/skills` (project: `.factory/skills`) | fan-out |
| Kiro | `~/.kiro/skills` (workspace: `.kiro/skills`) | fan-out |

Not covered: iFlow CLI (project-scoped `.iflow/` layout with its own skill marketplace — no user-level skills directory to fan out to).

`halter sync --apply` remains available for assistants outside this list. The subagents have no equivalent in the fan-out targets (they have no subagent mechanism) — they reach Claude-ecosystem harnesses via `~/.agents/agents`.

## Repository Layout

```
├── skills/                      # 16 auto-triggered skills (single source of truth)
│   ├── research-before-build/
│   ├── zotero-paper-fetching/
│   ├── zotero-paper-note/
│   ├── zotero-pdf-highlighting/
│   ├── figure-plotting/
│   ├── top-journal-writing/
│   ├── paper-polishing/
│   ├── term-audit/
│   ├── hedge-audit/
│   ├── paper-review/
│   ├── reference-verifying/
│   ├── rebuttal/
│   ├── venue-transfer/
│   ├── dear-editor/
│   ├── slide-making/
│   └── poster-making/
├── attic/                       # retired skills, kept for provenance
│   └── academic-paper-review/   # 7-agent journal-review simulation (upstream: academic-research-skills)
├── agents/
│   ├── jargon-check.md          # isolated-audit subagent
│   └── research-scout.md        # parallel prior-art research subagent (L2 vertical/horizontal lines)
├── .claude-plugin/
│   ├── plugin.json              # Claude Code plugin manifest
│   └── marketplace.json         # Claude Code / ZCode marketplace catalog (source ./)
├── .zcode-plugin/plugin.json    # ZCode plugin manifest
├── .codex-plugin/plugin.json    # Codex plugin manifest
├── .agents/plugins/marketplace.json  # Codex (~/.agents) marketplace catalog
├── scripts/
│   └── check_frontmatter.py     # strict-YAML frontmatter guard (pre-commit + install.sh gate)
├── .githooks/
│   └── pre-commit               # runs scripts/check_frontmatter.py (activated via core.hooksPath)
└── install.sh                   # bare install: ~/.agents hub + per-harness fan-out
```

## Maintenance Conventions

- Frontmatter of every tracked markdown file is strict-YAML-validated by `scripts/check_frontmatter.py`, gated twice: at commit time (`.githooks/pre-commit`, activated by `install.sh` via `core.hooksPath`) and before `install.sh` fans out — strict parsers in fan-out harnesses reject bad scalars (e.g. `": "` inside a plain single-line scalar).
- Edit skills in this repo only; `install.sh` creates symlinks — local changes take effect immediately, and pushing publishes them.
- Version bumps touch all three plugin manifests (`.claude-plugin/`, `.zcode-plugin/`, `.codex-plugin/`) and the `.claude-plugin/marketplace.json` entry in lockstep.
- The official ZCode marketplace channel (zai-org/zcode-plugins, `plugins/scientific-research-plugin/`) is **paused as of 2026-09-24** — no fork syncs or PRs until resumed. If resumed: sync every release via PR, keeping `version` and `description_i18n` identical (their `validate.py` enforces it), and confirm their `marketplace.json` actually lists the new version before announcing.
- `academic-paper-review` is retired into `attic/` (upstream: academic-research-skills); its useful mechanisms (fatal-flaw criteria, red flags, Devil's-Advocate attack dimensions) live on inside `paper-review`. See `skills/paper-review/references/source-basis.md` for full provenance.
- This repo is v20: v1 contained only 4 writing skills; v2 expanded to a research pipeline and evolved `language-polish` into `paper-polish`; v3 added the discipline layer `research-before-build` (⓪) and `academic-ppt` (⑦) and renamed `scientific-review` to `paper-review`; v4 rebuilds `paper-review` as a three-blind adversarial panel (nature-reviewer-style architecture, OR/ML+OR domain gates, author-defense arbitration) and retires `academic-paper-review`; v5 adds `reference-verify` (⑤ pre-submission reference audit, three-layer verification distilled from a full-manuscript citation check); v6 adds `term-audit` (batch noun-term jargon audit: extraction → five-signal ranking → parallel `jargon-check` terms-mode batches → variant/drift merger, seeded by Kobak et al. 2025 excess vocabulary) and the matching `terms` mode on `jargon-check`; v7 renames five skills to gerund forms per Anthropic's skill-naming best practice (`figure-plot` → `figure-plotting`, `paper-polish` → `paper-polishing`, `reference-verify` → `reference-verifying`, `zotero-paper-fetch` → `zotero-paper-fetching`, `academic-ppt` → `slide-making`) — 10 skills + 1 subagent; v8 adds `zotero-pdf-highlighting` (note-driven PDF category highlighting: PyMuPDF embedded-annotation route, strict five categories on the Zotero palette, idempotent re-runs); v9 adds `top-journal-writing` (④ section drafting/restructuring to top-journal blueprints — intro funnel, five-sentence abstract, recipe-style methods, four-step discussion — backed by a sentence bank mined from 200 top-venue papers across AI/OR/management/logistics/shipping via arXiv + OpenAlex harvesting) — 12 skills + 1 subagent; v10 makes `research-before-build`'s L2 truly parallel — the vertical and horizontal lines are dispatched simultaneously as `research-scout` subagents (one per line, own budget slice, per-line stop rules, degradation path for harnesses without subagents), bringing the pack to 12 skills + 2 subagents. v11 refocuses `research-before-build` on research-grade prior-art questions — L1/L2 tiering removed, engineering and academic dimensions both always searched, routine engineering unknowns (library/framework picks, integration, deployment, migration, cloud config, debugging, performance, security) delegated to the harness's native search — and adds question decomposition: PICO-style facet split (OR within facet, AND across) plus a relaxation ladder (full conjunction → drop the domain-binding facet as an evaluation-time filter → step the concept up), synthesized from Cochrane building-block searches, Motro's cooperative query answering, and step-back prompting — with every survey persisted as a dated reading list under `docs/research/` (papers with DOIs/arXiv IDs for `zotero-paper-fetching`, repos with versions to pin); v12 adds `poster-making` (⑧ single-page visual derivatives of a paper: conference poster across official-template / beamerposter / tikzposter / HTML render routes, journal graphical abstract to publisher pixel specs — INFORMS journals and AGU have no GA channel, so the announcement card is the visual abstract there — and social-media announcement cards; canvas specs live in `assets/specs.json` as the single source of truth with sources and verified dates; a render-and-verify loop ships vector PDF + 2× PNG via `scripts/render.mjs`, all four HTML templates render-verified 2026-10-06); v13 folds the standalone `redbook-publish` skill (upstream: comeonzhj/Auto-Redbook-Skills) into `poster-making` as its xhs pipeline (§4.5): Xiaohongshu multi-image note cards — cover + auto-paginated content at 1080×1440 (3:4), `default`/`ranking` layouts, theme registry `assets/themes/themes.yaml`, copy contract as the single source in `references/xhs-playbook.md` — plus cookie-based auto-publish behind a dry-run → private → public gate; v14 adds `hedge-audit` (④ whole-manuscript defensive-writing / over-hedging audit — escape clauses after Results, null-result self-explanation, contribution-weakening hedges in Abstract/Introduction, hedge stacking anywhere, scattered caveats duplicating Limitations; five pathology classes with section-conditional delete / move-to-Discussion / move-to-Limitations / keep dispositions, relocation-integrity check, per-section hedge-density gradient, keep-list protecting legitimate statistical precision); v15 switches `research-before-build` to human-gated invocation (`/research-before-build`, frontmatter `disable-model-invocation: true`): the invocation itself is the scope gate — Step 1's three-bin triage collapses to a downshift valve, and the assistant may only propose the skill when a task graduates to research-grade mid-execution; local artifacts are demoted from terminal prior-art hits to inputs (an in-repo implementation may be exactly what is wrong — it enters Step 4 as the zero-migration-cost candidate instead of ending the search); the memo template is re-sectioned by retrieval origin (engineering side / academic side / cross-domain side, membership decided by which line and track retrieved the candidate, an empty section printed as a finding); v16 adds `research-before-build`'s tool layer: a plugin hooks gate (`hooks/research_gate.py` — invocation marker on /research-before-build, WebSearch budget enforced per scout line and globally with fail-open semantics, work-order field validation with a one-re-issue cap, memo write closing the survey) plus four skill-dir scripts that travel with every fan-out harness (`new_memo.py` scaffold, `lint_memo.py` structural contract, `verify_reading_list.py` CrossRef/arXiv machine-verification of every reading-list ID, `check_repo.py` GitHub facts for repo candidates) — judgment stays with the model, enforcement and bookkeeping move to tools; v17 adds `venue-transfer` (⑥′ submission-lifecycle manager: candidate-journal sheet → venue-targeted rewrite → upload-time snapshot via git tag + submission log, with a frozen-archive fallback when the PDF is untracked → rejection triage with verbatim review archiving → venue re-selection (rejection comments — desk or post-review — never absorbed into the manuscript, they feed venue selection only) → narrative flip for the next venue, same-venue revisions handed to `rebuttal`) — 15 skills + 2 subagents; v18 splits the submission one-pagers out of `venue-transfer` into `dear-editor` (⑥″ cover letter + title page, typeset from public slot templates with git-ignored personal copies carrying the frozen identity — sender block, signature image, author blocks, standing grants — under hard one-page compile gates; `venue-transfer` keeps the venue argument and the lifecycle, and invokes it at every submission event) — 16 skills + 2 subagents; v19 moves the submission-lifecycle tree to the project root (`paper/` — formerly `docs/paper/`) and closes the staging blind spot behind stray `submission/` folders: Stage 1 assembles the upload package directly into the round folder `paper/submissions/<venue>/vN/` (cover letter, title page, highlights when the venue asks — source in `manuscript/` — and the PDF when untracked), which Stage 2 then seals against what was actually uploaded; `dear-editor` gains a no-staging-dir rule (never create `submission*/`/`upload*/` at the LaTeX root) and both skills end on a layout gate with exactly two homes for uploadables — `manuscript/` for sources, the round folder for package copies — 16 skills + 2 subagents; v20 restructures `figure-plotting` for progressive disclosure — SKILL.md shrinks to the routing layer (figure contract, chapter-based tool routing, shared hard rules on font/size/palette, execution conventions, delivery checklist), while the drawio workflow and the matplotlib data-chart spec sink into `references/drawio-workflow.md` and `references/data-charts.md`, read on demand after routing; the previously unreferenced `references/sea-routes.md` (land-avoiding shipping routes) is wired back into the routing — trigger surface (frontmatter description) unchanged, per-invocation context roughly halved.

## License

MIT

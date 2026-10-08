---
name: research-before-build
description: "Prior-art survey before building — has humanity already solved this problem? Surveys engineering venues (official docs, GitHub issues, mature open-source repos) AND academic venues (papers, white papers), vertically within the field and horizontally across fields, via two parallel research-scout lines; candidates ranked by trust and structural match; output is a persisted memo with a reading list. User-invoked: type /research-before-build when you want to know how a problem has been solved before designing or building; the assistant may propose this skill when a task graduates to research-grade mid-execution, but only the user invokes it. NOT for routine engineering unknowns — library/framework selection, cross-system integration, deployment, migration, cloud config, obscure errors, performance puzzles, security — the harness's native search handles those; not for execution with a settled path."
metadata:
  short-description: Research before building — user-invoked survey of engineering and academic prior art, in and across fields
license: MIT
disable-model-invocation: true
---

# Research Before Build

Purpose: before building, answer one question — **has humanity already solved this problem?** Reinventing the wheel is the biggest waste; community solutions are battle-tested compressed experience. This skill serves **research-grade prior-art questions** — the ones whose prior art lives in two worlds that rarely cite each other: engineering (repos, tools, docs) and academic (papers). Ask "quantify geopolitical risk in a logistics network" and the answer splits across GitHub simulation projects and OR journals; covering one world is half an answer. The usual limitation is not that the problem is unsolvable, but that the question is boxed in by your own field's vocabulary — everyone's knowledge is local, the answer often lies outside your field, and searching with only your domain's jargon is hunting for a door in a blank wall; hence the horizontal line is co-primary, never a fallback. What this skill is **not**: a wrapper over search. Routine engineering unknowns — library/framework picks, cross-system integration, deployment, migration, cloud config, obscure errors, performance puzzles, security — are handled by the AI harness's native exploration; this skill does not intercept them, and neither does it gate execution work whose path is settled. In scope: pin down what to research from the task description and repo conventions, decide each question's retrieval strategy (facet split + relaxation ladder), then search by dimension (engineering AND academic, both always) and direction (vertical within the field, horizontal across fields — in parallel); rank candidates by relevance, accept by decision impact.

## Step 1: Invocation is the gate

Being invoked — the user typed `/research-before-build`, or accepted the assistant's proposal to run it — **is** the scope decision: the question is research-grade; there is no in-skill re-triage into settled-path or routine-engineering bins. What remains at runtime is a single **downshift valve**: if reading the task shows the path is already settled or one targeted lookup answers it, say so in one line (Step 5's no-decision-impact clause) and stop — no scouts, no file.

## Step 2: Pin down what to research (mandatory before searching)

Distill from two inputs the question list this research must answer, ranked by relevance — the most decision-changing first:

1. **The user's task description**: verbatim requirements, any settled roadmap, unknowns left over from the last round
2. **The repo's AGENTS.md** (or CLAUDE.md and similar convention files): stack conventions, toolchain, no-go zones

Write each question twice: first as a **domain statement** — the symptom in this field's own terms, used for vertical queries; then as an **essence statement** — strip the domain jargon and write the problem's structure, plus background and the sticking point (why you are stuck, what you tried), so anyone in any field can understand what is being asked; this feeds the horizontal line. Example:

> Domain statement: LLM leaderboards are all over the place with inconsistent methodologies — how do we aggregate a fair capability score?
> Essence statement: we hold only pairwise comparison records from multiple sources (two models sharing a leaderboard is one match, higher rank wins); how do we infer each model's latent ability — the hard parts being overlapping sources, opponents that never met directly (connectivity via common opponents), and small samples producing extremes

**Retrieval strategy** — the query-construction layer beneath Step 3's dimension and direction: split each question into **facets** and write its **relaxation ladder**. Compound questions rarely retrieve as written: the full conjunction (problem AND context AND constraint) is sparse while each component alone is dense, so plan the broadening before searching, not after missing:

- **Facet split** (2–4 facets, ordered by how domain-binding they are): the **method facet** — what is being done, the densest-evidence core; the **context facet** — where it is done, usually the sparsest, intersection-killing one; the **constraint facet** — under what limits. Give each facet 2–3 synonyms (OR within a facet, AND across facets).
- **Relaxation ladder**: rung 0 — the full conjunction, all facets AND-ed; rung 1 — drop the most domain-binding facet (almost always the context) and search the denser remainder, re-applying the dropped facet at evaluation time (Step 4) as a filter, not as a search key; rung 2 — step the remaining facet one level up to its broader concept, or split a compound concept. Not every facet belongs in the search string — that is the point of rungs.

> "Quantify geopolitical risk in a logistics network": method facet {geopolitical risk quantification, GPR index, country risk} × context facet {logistics network, supply chain}. Rung 0 ANDs them; rung 1 searches the method facet alone — dense — and filters for logistics at evaluation; rung 2 steps up to political / country risk quantification.

(Provenance: Cochrane Handbook ch. 2 §2.3 / ch. 4 §4.4 — PICO facets, building-block Boolean, "not all facets in the search string"; Motro 1992, cooperative query answering — controlled relaxation on empty/sparse results; step-back prompting, arXiv:2310.06117 — abstraction to the superordinate concept; facet analysis, ISKO encyclopedia.)

For each question, state how the answer would change what you do; questions where you cannot write this do not get searched. All later searching and ranking follow this list — no wandering.

## Step 3: Search by dimension and direction, in parallel

Two independent choices define the search space — the retrieval strategy from Step 2 decides how queries are built and broadened inside it:

**Dimension — which sources to search: engineering AND academic, both always.** A research question's prior art usually lives in both worlds and the two rarely cite each other. Engineering: official docs, GitHub issues/discussions, mature open-source repos — "does ready-made code exist and does it really do this". Academic: papers and industry white papers — "how has this been approached, which methods are cited and replicated". Problem nature decides which leads each query, never which is skipped.

**Direction — where to search: vertical and horizontal, co-primary and simultaneous**, dispatched as parallel `research-scout` subagents: the vertical line digs within the field with domain-statement queries; the horizontal line sweeps across fields with essence-statement queries (different query vocabularies, so they never duplicate work), neither waiting on the other. A vertical hit does not call off the horizontal line: Step 4 ranks by structural match, and a structurally isomorphic cross-field answer is often worth more than a superficially similar in-field one — until both lines have reported, there is nothing to compare.

**Local artifacts are inputs, never terminal hits**: invoking this skill is a mandate to survey the world's prior art, and an in-repo implementation may be exactly what is wrong — nothing local ends the search. What local context still does: failed attempts in commit history feed Step 2's sticking point; lockfiles and README/AGENTS.md pin versions and no-go zones for Step 4's gates; an existing in-project implementation may enter Step 4 as one more candidate — the zero-migration-cost baseline to beat — not as a pre-search terminator.

Query discipline (for the in-session degraded run; the scouts carry their own copy): engineering queries as **stack + version + symptom + constraint**, academic queries as **problem structure + method family + constraint**; no open-ended searching. Trust ladder, high to low: official docs / official SDKs / vendor best practices > GitHub issues/discussions with maintainer replies > high-vote Stack Overflow (always check freshness and version match) > personal blogs / AI-generated content (leads only, never evidence). For repo candidates, verify the README and core code actually do the thing; record stars, maintenance activity, license, reusable parts — `scripts/check_repo.py <owner/name>` fetches stars, last push, archived flag, license, and the pin commit from the GitHub API as facts, not memory (the trust/freshness/migration judgement itself stays here in Step 4).

### Dispatch protocol — two parallel `research-scout` subagents

The scout definition carries the line discipline (query construction, trust ladder, per-line stop rules, anti-hallucination, memo format); the work order carries only the task slice, one per line:

```
Direction: vertical | horizontal
Questions (this line's slice): … each with its domain statement (vertical) / essence statement (horizontal)
Retrieval strategy: per question from Step 2 — facet split with synonyms + relaxation rungs (rung 0 conjunction → rung 1 drop the domain-binding facet → rung 2 step-up / split)
Constraints: stack + versions + repo no-go zones (from AGENTS.md)
Sources: [vertical] engineering and academic tracks, both in scope (problem nature picks the lead); [horizontal] cross-field sweep, white papers, internal knowledge bases (local paths if any)
Budget: N of the global 8 (typically 3–4); a scout stops at its slice and never borrows across lines
```

When both memos are in, rank and evaluate in the main session (Step 4) — an empty line memo is input to that comparison, not a failure; the main session may re-issue at most one re-phrased work order per line before declaring it exhausted. (In Claude Code with the plugin enabled, this is hook-enforced: work orders missing any of the five fields are denied with the missing list, and a third dispatch of the same line is refused — fix the order, not the hook.)

### The horizontal line

1. **Ask with the essence statement**: put the sticking point + the problem + the background fully into the query (same for search engines, communities, and models) and ask "has humanity ever solved something like this" — queries built only from domain jargon can only recall answers you already know
2. **Sweep horizontally**: other tech stacks, other industries, other eras all count — mature methodologies are mostly borrowed (evolution → genetic algorithms, supermarket restocking → Toyota lean, ant foraging → routing optimization); if nothing hits, re-search with 2–3 sets of synonyms from different fields
3. **Expand sources**: industry white papers, internal knowledge bases (Zotero/notes/wiki), cross-checking multiple independent sources

Worked example: sent out with the essence statement above, the leaderboard-aggregation question hit two unfamiliar fields — educational measurement (students taking exams of different difficulty, latent ability estimated from responses) and esports (Elo / TrueSkill rating ability from win-loss records) — and both tracks answered at once: Elo is engineering practice, TrueSkill and Bradley-Terry are papers. The Bradley-Terry pairwise comparison model was adopted and adapted to the constraints (priors for small samples, evidence budgets for overlapping sources, anchor models fixing the scale). Cross-domain prior art is adopted by problem structure and then adapted — not copied.

**Degradation path**: where no subagent mechanism exists (or `research-scout` is not installed), run both lines in the main session yourself — batch the two lines' search calls in the same message so they still proceed in parallel, keep the same budget split and per-line stop rules, and note in the memo that the lines ran non-isolated.

## Step 4: Rank by relevance, then evaluate

Rank candidates by **relevance** first — the criterion is **match on problem structure** (does it directly answer a question from the Step 2 list), not domain or vocabulary similarity: a structurally isomorphic solution found in another field is often worth more than a superficially similar one from your own. Then run each candidate, high to low, through three gates:

- **Trust**: which tier is the source? Battle-tested?
- **Freshness**: compatible with the current version/environment? Still maintained?
- **Migration cost**: how much rework to fit the current constraints? Any license/security issues? For candidates retrieved from a relaxed rung, the dropped facet re-enters here — score transferability to the dropped context (a structurally isomorphic answer from another setting transfers; a superficially similar one does not).

## Step 5: Output a prior-art memo, persisted as a reading list (mandatory)

The memo lands in two places: the conversation, for the immediate decision, and a file — `docs/research/<yyyy-mm-dd>-<topic-slug>.md` in the project — so the survey survives the session (re-asking the same question re-burns budget; related-work writing wants the trail; a deleted or relicensed repo stays traceable). Scaffold with `scripts/new_memo.py <topic-slug>`; before closing, `scripts/lint_memo.py` must pass (sections, channels, IDs, URLs, licenses); before the papers reach `zotero-paper-fetching`, `scripts/verify_reading_list.py` machine-resolves every DOI/arXiv ID against CrossRef/arXiv — facts over model recall. The scripts travel with the skill directory; where the harness has no shell, keep the manual discipline. The file is also the pipeline's hand-off artifact:

```
## Prior-art memo — <topic>, <date>
- Scope searched (both dimensions, both directions, per line): engineering — official docs X, repos Y, issues Z; academic — arXiv, Scholar, OpenAlex; horizontal — fields swept, synonym sets used
- Candidates — three sections by origin, assembled from the two scout memos; each section ranked by relevance within (a flat priority list hides which side a candidate came from — the memo is a reading artifact, and zone-reading beats re-decoding every entry; intra-section order keeps Step 4's structural-match ranking doing the work):
  - Engineering side (vertical line's engineering track — ready-made code, official docs, tools): A / B / C
  - Academic side (vertical line's academic track — in-field papers, white papers): D / E
  - Cross-domain side (horizontal line's essence-statement hits, paper or repo, each tagged with its borrowed-from field): F [← psychometrics] / G [← esports]
- Evaluation (draws on all three sections; adopted pieces often come from different sides — code from engineering, method from cross-domain): A compatible with current version ✓; B abandoned ✗; F from another field, adaptation scoped ✓
- Decision: adopt A and adapt (reason);
  or "none applicable, implement ourselves (checked X/Y/Z, none satisfies constraint N)"
- Reading list (the minimal deliverable; papers and repos are its two acquisition channels, drawn from all three sections):
  - Papers: title — DOI / arXiv ID — venue, year → hand to `zotero-paper-fetching` for acquisition into Zotero (official-API metadata verification, PDF, tiered filing); cross-domain hits append borrowed-from field + adaptation delta (what was changed to fit) — that note is the related-work trail
  - Repos: name — URL — version/commit to pin — license — stars, last release → adoption means dependency or clone; the pinned version is the provenance record
```

Section membership is decided by **origin** (which line and track retrieved the candidate), never by artifact type — a cross-domain repo stays in the cross-domain section and enters the reading list's repo channel; the section answers "where was this found", the reading-list channel answers "how is it acquired", and the two never collide. An empty section is itself a finding, printed as such (not omitted): the horizontal line coming back empty triggers Step 3's re-issue decision; an empty engineering side against a dense academic side says the answer lives in papers, and the reading effort should follow. The cross-section comparison is not lost to sectioning — Evaluation and Decision draw on all three sections, and the borrowed-field + adaptation note on cross-domain candidates is what related-work writing will quote later.

**Research with no decision impact is pure overhead.** When the results change nothing, one sentence in the conversation suffices — and no file either; the reading list exists only when the memo does.

## Stopping Rules and Safeguards

- Per-line stopping happens inside each `research-scout`: 2 consecutive fruitless rounds of its own (a round = one group of targeted searches around the same phrasing) retire the line; the main session may re-issue at most one re-phrased work order per line before declaring it exhausted
- Total external-search budget: at most 8 searches overall, split across the two parallel lines from the first round (typically 3–4 each, roughly even until hits start concentrating on one line); scouts stop at their slice and never borrow across lines — only the main session re-issues. In Claude Code (plugin enabled) the ceilings are hook-enforced — per-scout line cap and a global counter keyed to the invocation marker; the counter is the truth, not memory, and writing the memo closes the survey
- No searching for searching's sake: before every search, state how the result would change your approach
- **Not found ≠ does not exist**: any claim of "no prior art" must list the places actually checked
- After adopting a community solution, verify: version compatibility, tests pass, license check, security scan when warranted

---
name: research-before-build
description: "Research before building. Fires only on exploratory tasks — undecided approaches, unfamiliar territory, library/stack selection, integrations, debugging — and requires searching human prior art and community solutions (official docs, mature open-source libraries, GitHub issues, high-vote Q&A, papers, internal knowledge bases) before implementation or conclusions; sources ranked by trust, results accepted by decision impact. Not for execution work with a settled path — typo fixes, formatting, renames, tasks where the user has already specified the approach, routine in-project development following established patterns. English triggers: \"check prior art\", \"research before implementing\", \"find an existing library\", \"don't reinvent the wheel\", \"which library should I use\"."
metadata:
  short-description: Research before building — check prior art and community solutions before exploratory work, not just in your own field
license: MIT
---

# Research Before Build

Purpose: before building, answer one question — **has humanity already solved this problem?** Reinventing the wheel is the biggest waste; community solutions are battle-tested compressed experience. And the usual limitation is not that the problem is unsolvable, but that the question is boxed in by your own field's vocabulary — everyone's knowledge is local, the answer often lies outside your field, and searching with only your domain's jargon is hunting for a door in a blank wall. This skill therefore serves exploratory tasks only (undecided approach, unfamiliar territory, selection/integration/debugging): first pin down what to research from the task description and repo conventions, then pick dimension and direction — dimension by problem nature (engineering track for implementations, academic track for methods), direction by depth of the unknown (dig vertically within the field, borrow horizontally across fields; the deeper the unknown, the more you must strip the domain jargon and distill the problem into its domain-agnostic essence); rank candidates by relevance, accept by decision impact.

## Step 1: Triage (mandatory, cheapest)

This skill serves exploratory tasks only. On load, run the gate check first, then set research depth:

**Gate**: execution work with a settled path (user-specified approach, in-project patterns that apply directly, modifications locatable locally) is out of scope — just execute, no searching. Only tasks with an undecided approach, unfamiliar territory, or selection/integration/debugging unknowns proceed.

| Level | Exploratory signature | Search scope |
|---|---|---|
| **L1** | Unfamiliar or high-risk: library/framework selection, cross-system integration, deployment, migration, cloud config, obscure errors, performance puzzles, security | **Mandatory external search**: targeted and vertical, engineering vs academic track by problem nature; once a trusted source is hit, move on to evaluation |
| **L2** | Research-grade: literature reviews, solution design, architecture selection, research proposals (upgrade here when L1 comes up empty — trigger conditions under "Stopping Rules and Safeguards") | Prior-art research **is the task itself**: vertical + horizontal, engineering + academic, multi-source; the breakthrough is often outside the field |

When unsure, treat as L2. If the user explicitly asks to skip research, obey.

## Step 2: Pin down what to research (mandatory before searching)

Distill from two inputs the question list this research must answer, ranked by relevance — the most decision-changing first:

1. **The user's task description**: verbatim requirements, any settled roadmap, unknowns left over from the last round
2. **The repo's AGENTS.md** (or CLAUDE.md and similar convention files): stack conventions, toolchain, no-go zones

Write each question first as a **domain statement**: state the symptom in this field's own terms — L1 targeted searches use it directly. Add an **essence statement** by level — write it from the start at L2, and at L1 only when the stopping rules force a re-phrase: strip the domain jargon and write the problem's structure, plus background and the sticking point (why you are stuck, what you tried), so anyone in any field can understand what is being asked. Example:

> Domain statement: LLM leaderboards are all over the place with inconsistent methodologies — how do we aggregate a fair capability score?
> Essence statement: we hold only pairwise comparison records from multiple sources (two models sharing a leaderboard is one match, higher rank wins); how do we infer each model's latent ability — the hard parts being overlapping sources, opponents that never met directly (connectivity via common opponents), and small samples producing extremes

For each question, state how the answer would change what you do; questions where you cannot write this do not get searched. All later searching and ranking follow this list — no wandering.

## Step 3: Search by level

Dimension and direction are independent choices: **dimension** is which sources to search, set by problem nature — implementation, configuration, and troubleshooting questions go to the engineering track first, method, algorithm, and modeling questions to the academic track, and if one track comes up empty switch to the other; **direction** is where to search, set by depth of the unknown — dig vertically within the field first, and only borrow horizontally across fields when that fails. L1 is vertical; L2 adds horizontal.

### L1 — Targeted vertical search (engineering or academic track, by problem nature)

**Local prior art** (zero cost, before any external search): in-project implementations, commit history, installed skills, installed dependencies — whatever already does the job, use it and stop looking; other local files (lockfiles, README/AGENTS.md) are not prior-art evidence, only inputs for pinning versions and constraints.

**Engineering track** (how others built or solved it), two source lines as needed.

Knowledge line (know-how: how others solved it), by trust from high to low:

1. **Official docs / official SDKs / vendor best practices** — highest trust
2. **GitHub issues / discussions** (prefer ones with maintainer replies)
3. **High-vote Stack Overflow** (always check freshness and version match)
4. **Personal blogs / AI-generated content** — lowest trust; leads only, never evidence

Code line (implementation: does ready-made code exist):

Search for mature open-source repos that "do exactly this thing"; verify the README and core code of each to confirm it really does; record stars, maintenance activity (recent releases), license, and reusable parts.

**Academic track** (how researchers approached it): take this line when the problem is essentially about methods, algorithms, modeling, or theory — search papers and industry white papers by topic, preferring mature methods that are repeatedly cited and replicated; papers cited by engineering solutions are also worth tracing back.

After pinning versions and constraints, construct the queries: engineering queries as **stack + version + symptom + constraint**, academic queries as **problem structure + method family + constraint**; no open-ended searching. The number of search rounds follows decision impact: for most questions, 1–2 targeted searches that hit a trusted source suffice to move on to evaluation — no need to walk every source line.

### L2 — Systematic research (horizontal on top of vertical)

Searching vertically with domain terms at L1 is right — you know which field the answer lives in. L2's premise is precisely that you do not; domain vocabulary is the wall, so turn horizontal. On top of L1's two tracks:

1. **Ask with the essence statement**: put the sticking point + the problem + the background fully into the query (same for search engines, communities, and models) and ask "has humanity ever solved something like this" — queries built only from domain jargon can only recall answers you already know
2. **Sweep horizontally**: other tech stacks, other industries, other eras all count — mature methodologies are mostly borrowed (evolution → genetic algorithms, supermarket restocking → Toyota lean, ant foraging → routing optimization); if nothing hits, re-search with 2–3 sets of synonyms from different fields
3. **Expand sources**: industry white papers, internal knowledge bases (Zotero/notes/wiki), cross-checking multiple independent sources

Worked example: sent out with the essence statement above, the leaderboard-aggregation question hit two unfamiliar fields — educational measurement (students taking exams of different difficulty, latent ability estimated from responses) and esports (Elo / TrueSkill rating ability from win-loss records) — and both tracks answered at once: Elo is engineering practice, TrueSkill and Bradley-Terry are papers. The Bradley-Terry pairwise comparison model was adopted and adapted to the constraints (priors for small samples, evidence budgets for overlapping sources, anchor models fixing the scale). Cross-domain prior art is adopted by problem structure and then adapted — not copied.

## Step 4: Rank by relevance, then evaluate

Rank candidates by **relevance** first — the criterion is **match on problem structure** (does it directly answer a question from the Step 2 list), not domain or vocabulary similarity: a structurally isomorphic solution found in another field is often worth more than a superficially similar one from your own. Then run each candidate, high to low, through three gates:

- **Trust**: which tier is the source? Battle-tested?
- **Freshness**: compatible with the current version/environment? Still maintained?
- **Migration cost**: how much rework to fit the current constraints? Any license/security issues?

## Step 5: Output a prior-art memo (mandatory at L2, light at L1)

```
## Prior-art memo
- Scope searched: official docs X, repo Y, issue Z (list the sources actually checked)
- Candidates (by relevance, high to low): A / B / C
- Evaluation: A compatible with current version ✓; B abandoned ✗; C license conflict ✗
- Decision: adopt A and adapt (reason);
  or "none applicable, implement ourselves (checked X/Y/Z, none satisfies constraint N)"
```

**Research with no decision impact is pure overhead.** When the results change nothing, one sentence suffices; when L1 hits a trusted solution, one line — "adopt X (source Y)" — suffices; no full template needed.

## Stopping Rules and Safeguards

- Stop in a fixed order, each step triggered by 2 consecutive fruitless rounds (a round = one group of targeted searches around the same phrasing): if only one track has been tried, switch to the other (engineering ↔ academic) first; if both tracks come up empty, escalate to L2, write the essence statement, and search horizontally; only after horizontal searching also fails, stop searching and proceed to implementation, noting "searched, no prior art found"
- Total external-search budget: at most 8 searches overall; when exhausted, stop — same treatment as stopping on no results
- No searching for searching's sake: before every search, state how the result would change your approach
- **Not found ≠ does not exist**: any claim of "no prior art" must list the places actually checked
- After adopting a community solution, verify: version compatibility, tests pass, license check, security scan when warranted

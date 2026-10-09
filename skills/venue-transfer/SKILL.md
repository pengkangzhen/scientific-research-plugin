---
name: venue-transfer
description: >
  Venue transfer — journal-submission lifecycle manager: build the candidate-journal
  sheet, apply venue-targeted rewrites (title lens, abstract opening, keywords,
  intro framing, contribution order, highlights, cover letter), snapshot every
  submitted state at upload time (git tag + submission log, or a frozen archive
  when the PDF is not tracked), triage rejections (desk vs. review; rejection
  comments — desk or post-review — are never absorbed into the manuscript, they
  feed venue re-selection only), and execute the narrative-flip rewrite loop
  between venues. Triggers: "venue transfer",
  "desk rejection", "rejected, where next", "resubmit to another journal",
  "submission snapshot", "submission log", "candidate journals", "换刊", "转投".
  Same-venue major/minor revision belongs to `rebuttal`; this skill owns
  everything between two submissions.
license: MIT
---

# Venue-Transfer Skill — Submission Lifecycle Manager

You are a journal-submission strategist. Follow the workflow below strictly. Your job is not to polish prose — it is to manage the loop *between* submissions: pick the venue, aim the manuscript at it, freeze the exact submitted state, triage the outcome, re-select the next venue from the recorded rejection drivers (rejection comments themselves are never absorbed), and flip the narrative when the venue changes.

## Project Files (Auto-locate on Launch)

One home for the whole submission lifecycle, organized by event — the writing layer, then one folder per venue-round holding that round's full exchange:

```text
docs/paper/
├── manuscript/                  # WRITING: the LaTeX project (main .tex, sections, .bib, figures/,
│                                #   cover letter & title page sources) — working copy, git-managed
├── candidate_journals.csv       # Stage-0 sheet, one row per venue
├── submission_log.md            # one row per upload event, all venues — the cross-venue index
└── submissions/<venue>/vN/      # one round's full exchange (upload + verdict in one place):
    ├── manuscript.pdf           #   frozen when the PDF is not git-tracked
    ├── cover_letter.pdf         #   uploaded this round
    ├── title_page.pdf           #   uploaded this round
    ├── response_letter.pdf      #   point-by-point reply to the previous round's reviews — v2 on
    ├── decision_letter.md       #   this round's verdict — a desk-reject letter included
    └── reviewer1.md, ...        #   verbatim reviews, if any
```

- `manuscript/` is the writing layer's home: the LaTeX project proper plus its `cover_letter.tex` / `title_page.tex` sources. Writing-time materials (outline, figure plan, section notes) live inside it too. Git tags snapshot this tree; each round folder freezes what left it and what came back.
- `<venue>` is a short stable id (e.g. `EJOR`); the same id keys the git tag `submission/<VENUE>-vN`.
- `vN` is the upload counter *within one venue*: `v1` first submission, `v2` first revision, `v3` second revision; a new venue restarts at `v1`. A revision round answers the comments sitting in `submissions/<venue>/v1/`; its own upload and later verdict land in `submissions/<venue>/v2/`.
- A desk rejection is still a round: its folder simply holds the decision letter and no reviewer files.

Create missing pieces from the templates below when their stage first runs. Locate the inputs:

1. **Manuscript**: the `.tex` containing `\begin{document}` under `docs/paper/manuscript/`; for projects predating this layout, search the whole project instead (if several, the longest)
2. **Cover letter / title page sources**: `docs/paper/manuscript/` first; else search `submission*/`, `paper*/`, `**/cover_letter*.tex`, `**/title_page*.tex`

## Non-Negotiable Red Lines

- **One manuscript, one venue at a time.** Never prepare a second submission while the first is formally open; wait for the rejection or withdrawal to register in the editorial system.
- **Snapshot at upload, not at rejection.** The tag/archive must capture the exact state the editor and reviewers saw. Anything committed after upload pollutes the snapshot irreversibly.
- **Journal facts from sources, not memory.** Impact factors, quartiles, and review speeds change every June and vary by database. Verify via web search, note the value *and* the retrieval date in the sheet, and flag third-party numbers that conflict.
- **No proactive disclosure of rejection history** — there is no ethical obligation to mention prior rejections in a cover letter. But if a submission system *explicitly asks*, answer truthfully. The rule is "don't volunteer, don't lie".
- **Rejection comments are never absorbed — desk or post-review.** A desk rejection is one editor's 30-second scope/novelty scan, and its verdict is venue-specific (one journal's "too domain-specific" is another's "not methods-focused enough"). A post-review rejection is that panel's verdict justification, not a work order: the next venue fields a fresh panel, and a criticism that decided one rejection is not binding on the next submission. Rejection drivers — from either path — are recorded in the log in the editor's/reviewers' own terms and consumed by *venue selection* only; they never trigger manuscript changes. Substantive content-level remarks are surfaced to the user as advisory input, still not as revision mandates. Comments become revision mandates only when a venue says yes — a major/minor revision — and that is `rebuttal`'s jurisdiction.

## Stage 0 — Candidate Journal Sheet (On-Ramp)

Run when no sheet exists or the user opens the topic with "where should this go".

1. Read the manuscript's abstract and contributions; extract the **claim type** (method novelty / domain application / decision support / computational study) and the **evaluation shape** (single-case depth vs. multi-instance breadth; any known structural gaps).
2. Draft 8–15 candidates spanning at least three archetypes: home-domain journals (application is the norm), methods journals (mechanism story must lead), and adjacent interdisciplinary journals.
3. For each candidate, verify by web search: current IF/JCR quartile (note conflicting sources), median time to first decision, desk-rejection reputation, template family, open-access cost. Fill the sheet:

```csv
journal,category (IF/JCR/local tier),review speed,scope fit,framing required,risks
```

4. For each candidate write one **framing note** — which lens the manuscript must wear there (see Stage 5) — and one **risk note** — which known weakness that venue's editors probe first (evaluation breadth? scale? managerial insight?).
5. Present the sheet; the user (and their advisor) pick the target. Never pick for them.

## Stage 1 — Venue-Targeted Rewrite (Pre-Submission)

Apply the chosen venue's lens **before** first submission — the same checklist as a transfer flip (Stage 5), run once:

1. Rewrite the **cover letter**: first paragraph names the venue and answers "why this journal" concretely (scope keywords from the journal's own aims-and-scope page); pre-empt the one misfit an editor will notice ("the application domain is X, the contribution is Y").
2. Adjust the **title skeleton, abstract opening (first 1–2 sentences), keywords, intro ¶1–2, contribution ordering, highlights** to lead with what that venue's editors scan for.
3. **Keep venue-specific text localized.** Anything venue-aimed belongs in title / abstract / intro / contribution list / highlights / cover letter — never welded into deep method or results prose. This is what makes later flips cheap.
4. Figures, tables, methods, and experiments do **not** change for venue fit — only for content reasons.
5. Compile, verify, and confirm with the user before anything is uploaded.

## Stage 2 — Submission Snapshot (At Upload Time)

Immediately after the user uploads to the editorial system:

1. Confirm the working tree is committed and clean for the paper directory.
2. Tag the exact commit:

   ```bash
   git tag -a submission/<VENUE>-v<N> -m "<VENUE> submission <vN>, YYYY-MM-DD"
   ```

   Tag naming: `submission/<VENUE>-vN` — `v1` first submission, `v2` first revision, `v3` second revision; a new venue restarts at `v1` under its own name.
3. Push the tag **to the private remote only**. If the repository has a public mirror (e.g. a code-release repo separate from the private working repo), never push submission tags there.
4. **Upload folder**: freeze that round's submitted materials into `docs/paper/submissions/<venue>/vN/` — cover letter and title page on `v1`; the response letter answering the previous round's reviews from `v2` on; plus, when the compiled PDF is *not* tracked (ignored by `.gitignore`), a copy of `manuscript.pdf` too, since a tag alone cannot reproduce what was submitted. When the PDF *is* tracked, the tag carries the manuscript and the folder carries the rest. The round's verdict and reviews join the same folder when they arrive (Stage 3). Dates live in the log, not in folder files.
5. When the editorial manuscript number (MS # / EM ID) arrives, record it in the log.
6. Append one row to `docs/paper/submission_log.md`:

   ```markdown
   | Date | Venue | MS # | Tag | Commit | Status | Outcome | Key notes |
   |------|-------|------|-----|--------|--------|---------|-----------|
   | YYYY-MM-DD | <Venue> | <MS#> | `submission/<VENUE>-v1` | <sha> | submitted | — | <pre-submission baseline: what was aimed at this venue> |
   ```

## Stage 3 — Outcome Triage (Any Decision Arrives)

For **every** status change (under review → revision → rejected / accepted):

1. Archive the letter and, if any, **all reviewer comments verbatim** into the same round folder — `docs/paper/submissions/<venue>/vN/` — that this decision answers. The verbatim text is the record of what this venue actually said — the source for the log's driver notes and for any future response letter — do not summarize and discard.
2. Backfill the log row: Status → new state; Outcome → decision + date; Key notes → **the rejection drivers in the editor's own terms** (scope mismatch? evaluation breadth? novelty bar? missing comparison?).
3. Distinguish the paths — both rejection paths converge on the same next move (venue re-selection, Stage 4, then flip):
   - **Desk rejection** (usually ≤ 2 weeks, no or one-line reviews): the manuscript never met the editor's 30-second scan. No content signal — scope/novelty *presentation* signal only. Archive the letter, backfill the log; the recorded drivers feed venue re-selection (Stage 0 sheet risk notes). If the letter contains substantive content-level remarks despite being a desk decision, surface them to the user as advisory input to venue choice — still not as revision mandates.
   - **Post-review rejection**: same convergence. Archive the reviews verbatim, backfill the log with their drivers, and re-select the venue — but nothing from the reviews enters the manuscript. Individual comments that carry substance worth acting on someday are surfaced as advisory input to venue choice (or to a deliberate, user-initiated revision); they are never revision mandates.
   - **Major/minor revision at the same venue**: STOP — hand off to the `rebuttal` skill. Venue-transfer re-enters only if the revision is ultimately rejected.

## Stage 4 — Venue Re-selection (Decision Gate)

Runs after every rejection, desk or post-review. Nothing from the reviews enters the manuscript here — this stage only picks the next target.

1. **Update the sheet's risk notes** with the recorded rejection drivers (both desk and post-review): which known weaknesses did this venue's editors/reviewers probe? Mark the sheet's venues that are sensitive to the same weakness.
2. **Venue sensitivity check**: if the leading next venue is known to probe a weakness the manuscript still carries, prefer a venue that tolerates it. Closing the gap (a deferred experiment, an ablation) is a deliberate user decision made explicitly — never an automatic consequence of a rejection; if the user makes it, the transfer loop resumes only after the gap is closed.
3. **Publisher transfer-service check**: many publishers auto-offer a transfer (e.g. Elsevier's Article Transfer Service) to sister journals with format reuse. It may be declined — the suggested venue is publisher-optimal, not author-optimal. Compare against the sheet before accepting.
4. Select the next venue from the sheet (the user and their advisor decide) and proceed to Stage 5.

## Stage 5 — Narrative Flip (Transfer Rewrite)

Re-aim the manuscript at the new venue. The core move is a **lens flip** — what leads changes, what is proven does not.

| Next venue archetype | What must lead | Title skeleton |
|---|---|---|
| Home-domain journal | The domain problem; the method is the means | "<Domain problem> via <method>" |
| Methods/AI journal | The mechanism and its evidence | "<Method/mechanism> with <key mechanisms> for <domain>" |
| Decision-support / IS journal | The decision process and human–AI collaboration | "<Decision process> support through <method>" |
| Computational journal | The computational question (reliability, reproducibility) | "<Computational property> of <artifact>" |

1. Rewrite in this order (each feeds the next): **title skeleton → abstract first 1–2 sentences → keywords → intro ¶1–2 → contribution ordering → highlights → cover letter** (rewritten from scratch per venue — keep the skeleton, change the "why this journal" core).
2. Keep the claim–evidence calibration intact: a lens flip changes *what leads*, never *what is claimed*. Since rejection comments are never absorbed, a weakness that stayed open through a transfer stays open — no rewrite may quietly upgrade the corresponding claim.
3. **Template check** before formatting: same-publisher family (e.g. Elsevier `cas-*`) usually means zero re-layout; cross-publisher moves (Springer `sn-article`, T&F, IEEE) cost a class swap — the `.bib` carries over, the `.bst` changes.
4. Compile, verify, confirm — then Stage 2 for the new submission (`v1` under the new venue's tag name).
5. After tagging, record what changed for the transfer:

   ```bash
   git diff submission/<OLD>-v<N>..submission/<NEW>-v1 -- <paper-dir>/
   ```

## Hand-offs

- **→ `rebuttal`**: outcome is major/minor revision at the same venue. This skill resumes only on rejection after revision.
- **← `paper-review`**: its C/M/N issue list can seed the candidate sheet's risk notes before the *first* submission (pre-empting the desk scan).
- **→ `figure-plotting` / `top-journal-writing` / `paper-polishing`**: when a Stage 1/5 rewrite needs figure or prose work beyond this skill's scope.

## When NOT to Use This Skill

- Same-venue revision workflows (→ `rebuttal`).
- Choosing between conference and journal routes (out of scope; advise, don't automate).
- Any situation where the user asks you to submit on their behalf — uploading is always a human action; this skill prepares everything up to the upload button.

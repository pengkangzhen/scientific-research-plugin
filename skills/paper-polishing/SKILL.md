---
name: paper-polishing
description: >
  Language polishing — Academic English paper polishing for LaTeX manuscripts.
  Polishes grammar, word choice, sentence structure, logic flow, and academic tone while
  preserving all LaTeX markup (verified by a placeholder round-trip protocol); does NOT judge
  scientific content (use paper-review for that).
  Use this skill whenever the user asks to polish, refine, improve, or proofread a paper,
  manuscript, or LaTeX file, or mentions language editing, writing quality, or English
  improvement for academic writing. Also trigger on phrases like "check my English",
  "improve the writing", "make it more academic", "fix the language", "polish this section".
license: MIT
---

# Paper Polish Skill

You are an expert academic English editor specializing in Operations Research and Machine Learning papers. Your job is to polish LaTeX manuscripts to publication-ready quality.

## Input

The primary input is **selected/pasted text** — a paragraph, a few sentences, or a section the user highlights and sends for polishing. This is the most common use case.

Supported input forms (in order of expected frequency):
1. **Directly pasted text** — user selects and pastes a snippet: "polish this: ..."
2. **File path + line range** — user specifies a file and optionally lines: "polish manuscript.tex L100-L130"
3. **File path + section name** — "polish the abstract in manuscript.tex"
4. **Entire file** — "polish manuscript.tex" (least common; warn user this is a lot of changes and suggest going section by section instead)

If given a file path, read it. If a line range or section name is specified, extract only that portion.

## Polishing Dimensions

Apply all five dimensions to every passage you edit. They are listed in priority order — dimension 1 has the strongest signal, dimension 5 the weakest. When two dimensions conflict (e.g., a concise rewrite might lose precision), prefer the higher-priority dimension.

### 1. Grammar & Correctness
Fix errors in grammar, tense, agreement, articles, prepositions, and punctuation. This is non-negotiable — every sentence must be grammatically sound.

Common patterns to watch for:
- Missing articles: "proposed method" → "the proposed method" (when referring back to something specific)
- Subject-verb disagreement with compound subjects
- Tense shifts: stick to **present tense** for describing what the paper does ("This paper proposes..."), **past tense** for experimental results ("MAKO achieved...")

### 2. Precision & Accuracy
Replace vague or imprecise language with precise academic alternatives. The goal is that every claim can be parsed unambiguously by an expert reader.

| Vague | Precise |
|-------|---------|
| good / bad results | accuracy / error rate |
| a lot of | a significant proportion of |
| works well | achieves competitive performance |
| better than | outperforms ... by X% |
| very big | substantially larger |
| can solve | is capable of solving |
| some experiments | experiments on X benchmark instances |

Do NOT inflate claims. If the original says "improves accuracy," do not upgrade it to "significantly improves accuracy" unless the data supports it.

### 3. Academic Tone
Transform casual or overly verbose phrasing into concise, formal academic English. The reader is a peer reviewer in OR/ML — write for them.

| Casual/Verbose | Academic |
|----------------|----------|
| In order to | To |
| It is worth noting that | (delete — just state the fact) |
| As we all know | (delete — assumed knowledge) |
| We can see that | (delete — let the data speak) |
| In this paper, we try to | We |
| Due to the fact that | Because |
| has the ability to | can |
| is able to | can |
| On the other hand | Conversely / Alternatively |
| So, | Thus, / Therefore, |

Eliminate hedging filler: "basically," "actually," "essentially," "really," "quite," "rather." These weaken the writing without adding information.

### 4. Cohesion & Flow
Ensure logical connections between sentences. Each sentence should flow naturally from the previous one. Use appropriate transition words, but do not force them — not every sentence needs a connector.

Check for:
- **Orphan sentences**: sentences that introduce a new topic without transition
- **Redundant pairs**: consecutive sentences that say the same thing in different words — merge them
- **Dangling references**: "this method" or "this approach" without a clear antecedent
- **Broken parallelism**: "We propose X, analyze Y, and Z is validated" → "We propose X, analyze Y, and validate Z"

### 5. Conciseness
Remove unnecessary words without losing meaning. Shorter is stronger — review every sentence and ask "could I remove words and keep the same information?"

- "It should be noted that X" → "X"
- "There are several factors that affect" → "Several factors affect"
- "The results show that there is a significant improvement" → "The results show significant improvement"
- "We conducted experiments on a number of different datasets" → "We evaluated on multiple datasets"

But do NOT sacrifice clarity for brevity. If a longer sentence is clearer, keep it.

## Punctuation Rules (user-specific)

- **Avoid em-dashes** (`---` / `—`) in paper text, response letters, and all academic writing. Replace with a colon `:` to introduce a list or elaboration, parentheses `(...)` for parentheticals, or restructure the sentence. Verified by the em-dash check in the post-edit verification.

## LaTeX Handling Rules

These rules protect the compilability of the manuscript.

1. **Never break LaTeX commands**: `\cite{}`, `\ref{}`, `\label{}`, `\begin{}`, `\end{}`, `\textbf{}`, `\textit{}`, `\emph{}`, equations (`$...$`, `\[...\]`, `\begin{equation}`), tables, and figures must remain syntactically intact.

2. **Do not edit math content**: You may improve the text *around* equations, but do not change the mathematical notation or equation logic itself. Flag any suspected math errors for the user instead.

3. **Preserve structure**: Do not reorder sections, merge paragraphs, or change heading levels. Polish within the existing structure.

4. **Preserve whitespace conventions**: Keep existing blank lines between paragraphs. Do not add or remove line breaks within sentences unless the user's LaTeX style uses sentence-per-line (in which case, follow that convention).

5. **Bibliography references**: Do not change `\cite{key}` commands. If the citation text around a reference is awkward, improve the surrounding prose, not the cite command.

## Markup Extraction & Return Verification

Intending not to break markup is not protection; a verified round-trip is. Apply this protocol to every passage you polish, regardless of input type:

1. **Extract before rewriting**: enumerate every markup island in the passage — `\cite{}`, `\ref{}`, `\label{}`, inline and display math (`$...$`, `\[...\]`, equation/table/figure environments), and any command carrying arguments — and assign each a numbered placeholder `⟨1⟩`, `⟨2⟩`, … This is a scope partition: polishing rules act on prose only; islands are out of scope.
2. **Verify before returning**: every placeholder must come back verbatim — same token, same position relative to its sentence; braces and environment delimiters must balance. For pasted text, check against your own extraction list and report the check. A failed check blocks the output: fix and re-verify; never hand back an unverified passage.

After applying edits to a `.tex` file, run the post-edit verification on the changed regions and report the results:

1. **Em-dash check**: `grep -n '\-\-\-' <file>` — no em-dash may remain (house rule).
2. **Round-trip check**: the markup islands present after editing equal the set extracted before rewriting — nothing lost, mutated, or newly introduced.
3. **Delimiter check**: `$` / `\[` / `\]` counts are even on the changed lines, and every `\begin{X}` has its matching `\end{X}`.

## Output Format

The output format depends on the input type.

Every change is reported as a **numbered hunk**: `# [severity|dimension] "before" → "after" — one-line rationale`. Severity is determined by the triggering dimension: `critical` = grammar & correctness (dimension 1) plus any markup-safety violation; `major` = precision, academic tone, cohesion (dimensions 2–4); `minor` = conciseness and punctuation/style preferences (dimension 5). Group hunks by severity, critical first.

### Case 1: Pasted text (most common)

Output the severity-grouped hunk list, the round-trip check line, then the clean polished version:

```
## Changes

Critical:
1. [critical|grammar] "shows" → "show" — subject-verb agreement, plural subject "results"
2. [critical|markup] inline math returned as $\pi*$ instead of $\pi^*$ — caught by the round-trip check, reverted verbatim

Major:
3. [major|tone] "In order to" → "To" — verbose opener
4. [major|precision] "better than other methods" → "outperforms all baselines by 3.2%" — vague comparison replaced by the measured number

Minor:
5. [minor|concision] "It can be seen that" → deleted — let the data speak

## Round-trip check

⟨1⟩ \cite{chen2023repositioning} ✓  ⟨2⟩ $\pi^*$ ✓ — all placeholders returned verbatim, delimiters balanced

## Polished

To solve the empty container repositioning problem, we propose a method that effectively reduces transportation cost. Experimental results show that our method outperforms all baselines by 3.2%. The proposed approach achieves competitive accuracy across all test instances.
```

Do NOT use the Edit tool for pasted text — the user will copy the polished version themselves.

### Case 2: File path with line range or section

Present the Changes Summary first (same hunk format with line numbers), then apply edits one by one using the Edit tool so the user can review and approve/reject each one. After the last accepted edit, run the post-edit verification and report all three results.

Changes Summary format:

```
Critical:
- L67: [critical|grammar] "achieves" → "achieved" — past tense for experimental results

Major:
- L23: [major|precision] "good results" → "competitive accuracy" — vague claim made precise
- L45: [major|cohesion] "This method" → "The decomposition method" — dangling reference resolved

Minor:
- L12: [minor|concision] "due to the fact that" → "because" — filler removed
```

## Workflow

1. Determine input type (pasted text, file+lines, file+section, or entire file)
2. If entire file: warn user and suggest section-by-section instead
3. Extract markup islands into numbered placeholders (see "Markup Extraction & Return Verification")
4. Analyze the text against all five polishing dimensions
5. For pasted text: output Changes + round-trip check + Polished version directly
6. For file edits: present Changes Summary first, then apply edits one by one via Edit tool, then run the post-edit verification and report its results
7. Paragraph scale or larger: dispatch the jargon-check follow-up audit automatically (see "Follow-up" below)

## Follow-up: Terminology Audit

Polishing is a high-risk moment for introducing fresh shorthand: rewording a sentence often swaps in a new label for an existing concept. After completing a polish of paragraph scale or larger, **automatically dispatch** the **jargon-check** subagent (independent buzzword/terminology auditor) on the polished passage — do not ask the user first: the audit is read-only, and only applying its suggested revisions needs the author's confirmation. Skip the dispatch for `phrase`-scale polish and "light polish" requests. The dispatch brief must include: the file path or pasted text, audit mode (`phrase`/`passage`/`full`), and the project's terminology whitelist (method/agent/step names). Do not perform this audit yourself in the main session: the independence is the point. If the jargon-check subagent is unavailable in the current environment, say so and skip the audit — a same-context self-audit defeats the independence and must not be faked.

## Edge Cases

- **User asks to polish only grammar**: Still apply dimension 1, but skip 2-5. Ask the user if they want full polish instead.
- **User asks for "light polish"**: Prioritize dimensions 1-2, apply 3-5 only when the improvement is very clear.
- **User pastes non-LaTeX text**: Apply the same polishing principles but skip all LaTeX-specific rules.
- **Non-English text**: Inform the user this skill is designed for English academic writing. Offer to help if it's a translation or bilingual abstract.

---
name: slide-making
description: >
  Academic presentation slides — the full pipeline from a paper (LaTeX/PDF) to a
  talk-ready deck: LaTeX Beamer route + visual design system (extract the official
  template if provided, else build palette/layout from scratch) + math & figure
  reuse + time-budgeted talk script + packaging the slide PDF back into the
  official pptx with speaker notes.
  Two bundled templates: conference-beamer (conference talks) and defense-beamer
  (thesis proposal / defense / group meetings).
  Use this skill whenever the user wants to turn a paper/manuscript into
  conference or seminar presentation slides, build a Beamer deck, fit slides into
  the official template, write a time-budgeted talk script, or package a slide
  PDF back into a pptx with speaker notes — also for thesis proposal/defense/
  group-meeting decks — even if they never say "PPT" (e.g. "I'm giving a talk on
  this paper next week", "how do I prepare a 15-minute talk").
  中文触发词："会议PPT"、"演讲PPT"、"做幻灯片"、"把论文做成PPT"、"Beamer"、
  "会议模板"、"讲稿"、"演讲稿"、"演讲者备注"、"贴回模板"、"开题报告"、"答辩PPT"、
  "组会汇报"、"组会pre"、"开题Beamer"。
---

# Slide-Making Skill (paper → academic talk)

Produce academic presentation material from a paper (conference talks, thesis
proposal/defense/group meetings). This skill is distilled from one complete
conference-talk engagement (2026-08: two weeks, 14 sessions, multiple revision
rounds) and one university thesis-proposal Beamer theme replication (2026-09).
Its core value: the route is verified and the pitfalls have numeric-level fixes —
do not re-derive them by trial and error.

## 0. Typical workflow

1. Gather inputs: paper source (`manuscript.tex`), official conference template
   (if any), time slot, language (usually English).
2. Pick the route via §1 (conclusions first — do not re-survey tools).
3. Beamer route: §2 establish the visual design system — **copy the matching §8
   template in full, then edit content** (conference talk →
   conference-beamer/conference.tex; proposal/defense/group meeting →
   defense-beamer/defense.tex; if an official pptx template exists, extract
   backgrounds and wire them in) → write tex → §4 verification loop → consult
   §3 layout fixes as you go.
4. Talk script: §5 write/trim against the time budget; keep terminology
   consistent across paper, slides, and script.
5. Delivery: §6 package per conference requirements (compliant pptx / notes
   pane / contingencies).

Follow the §7 collaboration red lines throughout.

## 1. Route decision tree (verified conclusions)

Hard-constraint ordering: **official-template compliance (if the conference
provides one) > math/figure fidelity > editability > production speed**.
Before starting, confirm whether the conference provides an official template —
if yes, extract and reuse it (§2.1); if not, stand up a self-built design
system (§2.2).

| Route | Verdict | Why |
|-------|---------|-----|
| python-pptx from scratch | ❌ rejected | Element-by-element layout is code-heavy; template default fonts (e.g. Aptos) missing locally, so rendering diverges from real PowerPoint |
| officecli pptx generation | ❌ rejected | QA runs through an HTML renderer that diverges from real PowerPoint; font substitution makes wrapping/overflow uncontrollable |
| Consumer AI slide generators (chat-app PPT agents) | ❌ unsuitable for academic talks | Cannot embed paper figures; math gets mangled; the tested agent exported PDF only; usable at most for style-reference drafts |
| **LaTeX Beamer (xelatex) + design system (extracted or self-built)** | ✅ primary route | Native math, vector embedding of paper PDF figures, precise control |
| **Final PDF→images→official pptx packaging** | ✅ delivery route | The compliant form when the conference mandates its template / speaker notes are needed |

- Do not maintain dual formats in parallel: Beamer-only until the very end,
  then package back to pptx.
- If native pptx is mandatory and you need faithful render verification: drive
  real PowerPoint via AppleScript (osascript) to export PDF/PNG for checking;
  never trust HTML renderers.
- Thesis proposal / defense / group meeting: use the bundled defense-beamer
  theme (§2.4) directly; skip pptx extraction.

## 2. Visual design system: establish it before writing content frames

Background, palette, and title layout must be settled before writing content.
Two sources; the layout base is shared.

### 2.1 Official pptx template exists → extract and reuse

- A pptx is a zip: unzip and take the full-page background images from
  `ppt/media/` — usually three (cover `bg_cover` / content `bg_content` /
  closing `bg_closing`).
  - ⚠️ Logos and the real footer live in the slide master, **not** in the
    background images; extracted images may carry meaningless pale artifact
    strips.
- Calibrate the safe area with image inspection (e.g. view the extracted
  backgrounds directly with your image-reading capability; or eyeball): the
  usable body area, and the band height as a percentage of page height.
- Hanging backgrounds in Beamer:
  ```latex
  \documentclass[aspectratio=169,11pt]{beamer}   % pptx 13.33″×7.5″ = 16:9 = aspectratio=169; both sides match, no distortion
  \usebackgroundtemplate{\includegraphics[width=\paperwidth,height=\paperheight]{figs/beamer_bg/bg_content}}
  ```
  Cover/closing/divider pages override with their own backgrounds inside
  `{ ... }` groups.
- ⚠️ **`\usebackgroundtemplate` overrides `\setbeamercolor{background canvas}`**
  — this is why white text "vanished" on a navy divider page.
- ⚠️ **Unit-conversion trap**: pptx physical height is 19.05 cm, but Beamer
  `aspectratio=169` paper height is only **9 cm**. Band heights inside the
  background must be converted as percentages (a bottom 9.76% band ≈
  **8.8 mm**); never reserve pptx absolute dimensions directly (reserving
  21 mm this way once squeezed the body area and caused massive overflow).
- Final band-avoidance fix: the footline reserves exactly the band height so
  body content never enters the band; do not delete the background.
- When reusing the bg_cover photo on divider pages, adapt text colors to photo
  brightness (on a bright photo: title white → navy).
- Extract the palette from the template theme colors into `\definecolor`
  (battle-tested example): navy `0E2841`, orange `E97132`, teal `156082`,
  gray `5A6B7B`, light `F2F6F9`.
- The official-template extraction procedure, the three-line wiring, and the
  band-avoidance parameters are codified in `assets/conference-beamer/` (§8);
  conference brand assets (backgrounds) stay out of the repo — supply your own
  per its README.

### 2.2 No official template → build the design system yourself

- Principle: restraint for academic settings. White background with black body
  text as the base; **one primary color (deep blue/navy family) + one accent
  (orange/teal family) + gray support**, all landed as `\definecolor` before
  writing any frame.
- Palette sources: university visual identity, the paper's existing figure
  colors, or classic high-contrast combos; the five colors above are
  battle-tested — reuse them and swap the values.
- Keep luminance contrast globally consistent: reversed-out color blocks only
  for sparse, systematic emphasis; do not mix them at scale with
  white-background body pages (readability conflict, flagged by the user in
  real use).
- Optional starting points: a mature Beamer theme (e.g. metropolis; guard
  every optional font with `\IfFontExistsTF` with automatic fallback), or copy
  `assets/conference-beamer/conference.tex` in full — preamble and 17 frame
  archetypes fully verified; change five color values to restyle.
- With no background image, do **not** set `\usebackgroundtemplate`: white is
  Beamer's default, which sidesteps the §2.1 priority and unit-conversion
  traps; divider pages use a solid primary-color fill.

### 2.3 Layout base (shared by both routes)

- Remove nav symbols `\setbeamertemplate{navigation symbols}{}`,
  `\usefonttheme{professionalfonts}`; amsmath + unicode-math, with the math
  font (e.g. Fira Math) guarded by `\IfFontExistsTF`.
- Custom frametitle template: primary-color bold title + thin accent rule
  (e.g. 13mm × 1.1pt); section eyebrows see §3.
- `\divider` (divider page: big number + title) and `\callout` (emphasis card)
  are built-in template macros (conference-beamer/conference.tex); width rules
  in §3.

### 2.4 Bundled ready-made theme: defense-beamer (proposal / defense / group meetings)

- `assets/defense-beamer/`: `beamerthemeDefense.sty` (generic defense theme:
  top banner with optional university emblem + university/college wordmark
  macros + bottom section progress bar + TOC/divider/cover) +
  `defense.tex`/`defense.pdf` (sanitized proposal-defense skeleton, 25 pages
  covering all archetypes; placeholder text doubles as filling instructions;
  archetype cheat sheet in its README) + `README.md`.
- Usage: put the sty next to your deck file, `\usetheme{Defense}`,
  `\renewcommand` the four banner macros; supply your own emblem:
  `campus-emblem.png` in the same directory joins the banner automatically,
  otherwise you get a pure-text wordmark.
  Four content components cover the high-frequency layouts — `point` (orange
  left-bar bullet grouping), `warn` (limitation/risk strip), `card`
  (multi-column side-by-side cards), `band` (navy reversed-out conclusion
  banner).
- Fonts keep the source proposal deck's original setup (all guarded by
  `\IfFontExistsTF`): macOS renders the original look (HarmonyOS Sans body +
  XingKai brush-script wordmark + Zapfino flourishes); platforms missing them
  (Windows/WSL/Overleaf) fall back and still compile. The conference package
  uses the conference deck's fonts (Latin: Helvetica Neue, math: Fira Math,
  same guarding) — each package keeps its source deck's fonts; do not mix.

## 3. Beamer layout pitfalls and fixes (all actually happened)

- **\includegraphics size changes do nothing**: under `keepaspectratio`, first
  diagnose whether width or height is the binding constraint — check the
  figure's own whitespace with `pdfcrop`; if the column width is binding,
  raising `height` does nothing — widen the `column` instead (real case:
  0.46→0.54\textwidth grew the figure 37%).
- **Callout overflow / edge-hugging**: callout text width + 2× inner padding
  must be < the containing column width (real case: a 78mm block in a 68mm
  column, flush against the page edge).
- **No color blocks on text-only pages**: use plain paragraphs with small
  orange subheads; a callout overpowers the figure beside it.
- **Text+figure page convention**: text left, figure right (natural reading
  order); elements follow semantics (a process strip goes on the page that
  discusses that process).
- **Multi-column long text**: four side-by-side columns of long text → switch
  to a full-width vertical list (each row = big number + bold head + gray
  subnote).
- **Drive overfull hboxes to zero**: overfull pt ≈ overflow mm × 2.85 —
  measure exactly how much to trim; after narrowing one side, check the other
  for new vertical overflow (font \small→\footnotesize, leading 1mm→0.6mm).
- **Check math pages against the paper item by item**: once caught a dangling
  cost term (`+ c^fold/unfold` with no summation — mathematically invalid);
  added integrality constraints x,w,r,y∈Z₊; added a gray legend line on
  symbol-dense pages; tagged constraint blocks with small labels (demand-side /
  capacity-side coupling, boundary condition).
- **"Changed it, nothing happened" — two causes**: ① the edit never landed or
  never recompiled — before saying "fixed", confirm the PDF mtime advanced;
  ② PDF viewer cache — ask the user to reopen the file.
- Section eyebrow: above the content-page title, add a small orange eyebrow
  `SECTION N: <divider title>` — good wayfinding.

## 4. Visual verification loop (standard practice after every revision)

1. `latexmk -pdfxe presentation_beamer.tex` (or xelatex ×3) — compile to
   0 errors.
2. `pdftoppm -png -r 120` render all pages; run `scripts/contact_sheet.py` to
   build a contact sheet.
3. Inspect with your image-reading capability (e.g. the Read tool directly on
   PNGs): scan the contact sheet first (report only problems: overflow /
   truncation / band collisions / blank pages), then re-check the densest
   pages (math, tables, figures) at full resolution, page by page.
   - If reading an image errors right after a script refreshed that PNG = the
     file was mid-rewrite; wait for the write to finish and read again.
4. Quantify conclusions (pixel measurements, MSE against the background for
   consistency); never declare "it's fine" from impression.

## 5. Talk-script methodology (matched to speaking time)

- **User's standing rule: slides show more, the script says less** — when
  trimming the script, never touch the slides.
- Time budget: a 15-minute slot ≈ **1900 spoken words ≈ 13.25 min** (leaves a
  1.75 min buffer); embed cumulative time checkpoints in the script (e.g.
  [04:00] [07:00] [09:30] [12:00] [13:15]) and verify section by section.
- Trimming principles:
  - Don't read details already shown on the slide (say "about a quarter of the
    slots — exact values in the table");
  - Keep Q&A defense points in the spoken script (e.g. "leases are uncapped ⇒
    the model always has a feasible solution" pre-blocks feasibility attacks);
  - Don't re-list what the previous slide just said;
  - Give dashes a spoken reading ("— includes …"); write numbers as spoken
    ("62 percent").
- Script structure: per-page `[Slide: title]` markers + a global pacing table
  at the top + a key-numbers table + Q&A prep; skeleton in
  `assets/speech-template.md` — copy in full and fill.
- **Three-way terminology consistency** (paper / slides / script changed in one
  global pass); while the paper is under review you cannot unilaterally reword
  — log it as a revision to-do and sync the replacement later.
- Narrative polish: a negation-contrast opening ("not computation, but
  cognitive") is too abrupt — switch to progressive foreshadowing that lands
  the point at the end; change deck and script together (one pass touched
  3 + 5 spots).

## 6. Delivery packaging and contingencies

First decide whether packaging is needed at all: **no official template and no
speaker notes needed → presenting the Beamer PDF is the delivery**. The
packaging below runs only when "official template mandated / pptx notes pane
needed".

### 6.1 Compliant pptx packaging (PDF→images→official template)

```bash
pdftoppm -png -r 300 presentation.pdf /tmp/slide-png       # 300 dpi, 1890×1063
python scripts/package_pptx.py official-template.pptx /tmp/slide-png -o packaged.pptx
```
The script codifies the full procedure and the red lines: `~$` lock-file check
(refuses to write while PowerPoint has the file open) → automatic backup of the
template → delete the template's sample slides → pick the layout with the
fewest placeholders → paste each full-page image at (0,0) full-bleed → save →
reopen and verify page count and full-bleed placement; a render directory
contaminated with non-page images (e.g. the contact sheet) is rejected on size
mismatch.
- Both sides must be 16:9 or the pasted images distort (the script checks).
- In this form text is no longer editable — final delivery only; content
  changes go back to the Beamer source.

### 6.2 Notes

- Split the script on `[Slide: ]` and paste page by page into the pptx notes
  pane; Presenter View shows notes + timer, one page per screen.
- Presenter View needs an **extended display** (not mirrored);
  mirrored-only contingency: turn off "Use Presenter View" + print the
  "Notes Pages" layout as paper prompts + a vibrating phone alarm aligned to
  the script checkpoints.
- Shared-computer mirror risk: notes exist only in Presenter View; with the
  option off, the audience cannot see them.
- **Never present from the PDF** — PDF has no notes; that is exactly why the
  final packaging goes back to pptx.
- Printing handouts for the audience: the "Slides" layout — don't let staff
  pick "Notes Pages" (it would print your script).

## 7. Collaboration red lines

- **Never unilaterally delete a constraint the user named**: to fix an
  overlap, the template background was once replaced with plain white; the
  user was furious ("You deleted the template background???"). The correct
  move: locate the conflicting height precisely and reserve it, or ask first.
- Before saying "fixed": edit landed + recompiled + output mtime confirmed +
  render verified — all four, no exceptions.
- Parallel dual formats are a time sink: cut them mid-project, merge at the
  end.

## 8. Reusable assets (bundled under assets/, load on demand)

Two templates for two routes; when starting a deck, **copy the matching files
in full** and edit content — never write from scratch:

- **Conference route** `assets/conference-beamer/`: conference.tex (complete
  skeleton generalized from the battle-tested deck) + figs/beamer_bg/
  background drop-in point + README —
  preamble design system (five color values, frametitle eyebrow, footline band
  avoidance, `\divider`/`\callout` macros)
  + 17 frame archetypes across 18 pages (the math archetype spans two pages:
  cover / TOC / divider / bullets / three cards / full-width vertical list /
  text+figure / diagram / table / math×2 / overview / routing table /
  big-number results / comparative results / takeaways / conclusions /
  closing), placeholder content doubles as filling instructions;
  self-built mode compiles with zero external assets; official-template mode
  swaps the three macros `\BgCover`/`\BgContent`/`\BgClosing`.
- **Proposal/defense/group-meeting route** `assets/defense-beamer/`:
  beamerthemeDefense.sty + defense.tex/.pdf (sanitized skeleton) + README
  (details in §2.4).
- Official-template extraction procedure, three-line wiring, band-avoidance
  parameters, and the closing-page printed-text trap: see the
  conference-beamer README (backgrounds and the official pptx are the
  conference's copyrighted material — keep them out of the repo, supply your
  own).
- **Talk-script skeleton** `assets/speech-template.md`: pacing table +
  key-numbers table + `[Slide:]` per-page markers + cumulative checkpoints +
  Q&A prep bank; use with §5.
- **Verification & delivery scripts** `scripts/`: `contact_sheet.py` (§4 step
  2, contact sheet) and `package_pptx.py` (§6.1 full flow: lock-file check →
  backup → delete samples → blank layout → full-bleed paste → verify);
  depend on Pillow / python-pptx — run ad hoc via `uv run --with`.
- Filled-in decks (the templates' sources and reference instances) stay in
  their source projects, off-repo; recovery pointers in each asset pack
  README's "Provenance" section.
- Fastest reuse path: official template → follow the conference-beamer README
  (extract three backgrounds + three-line wiring + five color values);
  no template → self-built mode, start writing directly; proposal/defense/
  group meeting → copy defense-beamer, set the banner macros, fill in content.
  Then rewrite frame content → verify via the §4 loop → deliver via §6.

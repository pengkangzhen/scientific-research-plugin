# Conference-Talk Beamer Wiring Pack (conference-beamer)

The wiring template and parameter tables for the "official conference template
extraction & reuse" route (the reference implementation of SKILL §2.1).
Conference brand assets (background images, the official pptx) are the
conference's copyrighted material and **stay out of the repo** — supply your
own from the official template you receive, following the procedure below.
The wiring method, band-avoidance parameters, and the closing-page
printed-text trap are codified in this pack and in
`conference.tex` (the academic conference Beamer template; fonts follow the
battle-tested deck: Latin Helvetica Neue / math Fira Math, both guarded with
fallback).

## Files

| File | Purpose |
|------|---------|
| `conference.tex` | Academic conference Beamer template (self-built mode compiles with zero assets; official-template mode wires in per below) |
| `conference.pdf` | Compiled preview of the above (18 pages, all archetypes) |
| `figs/beamer_bg/` | Background drop-in point: put the three extracted full-page backgrounds here — `bg_cover.jpg` / `bg_content.jpg` / `bg_closing.jpg` |
| `README.md` | This file: extraction procedure, wiring, parameter tables |

## Step 1: Extract three backgrounds from the official pptx

A pptx is a zip: unzip and take the full-page background images from
`ppt/media/` — usually three (cover `bg_cover` / content `bg_content` /
closing `bg_closing`), and put them into `figs/beamer_bg/`.

- ⚠️ Logos and the real footer live in the slide master, **not** in the
  background images; extracted images may carry meaningless pale artifact
  strips.
- ⚠️ The brand band at the bottom of the content background is a real footer
  area — **do not delete it** (deleting the background is a collaboration
  red line).

## Step 2: Wiring (pairs with the bundled conference.tex)

Copy the whole `figs/` directory to your deck project root (next to
`presentation.tex`), then the three wiring lines:

```latex
\graphicspath{{figs/}}   % uncomment

\newcommand{\BgCover}{\includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio=false]{beamer_bg/bg_cover}}
\newcommand{\BgContent}{\includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio=false]{beamer_bg/bg_content}}
\newcommand{\BgClosing}{\includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio=false]{beamer_bg/bg_closing}}
```

Extract the palette from the template theme colors into the five `\definecolor`
lines in the [Palette] block of `conference.tex`.
Band avoidance is pre-built into the template footline (bottom band converted
by percentage: Beamer 16:9 paper height is only 9 cm, a 9.76% band ≈ 8.8 mm;
footline ht+dp = 11 mm, body stops ~2 mm above the band, page number sits
inside the band). If your band height differs, redo the same conversion and
reset — never reserve pptx absolute dimensions directly.

## Closing-page trap

Official closing backgrounds usually **come with printed text** (a real-world
`bg_closing` carried "Thank you for your attention!" spanning 30–46% of page
height) — overlaying text on it is guaranteed garbling. The closing frame in
`conference.tex` adapts to the mode: in official-background mode it keeps only
a single contact line. When switching to a new conference background, re-tune
the yshift against its whitespace (method: convert the background to PPM with
mutool and measure empty bands line by line in pixels) — never trust default
centering.

## pptx delivery packaging (SKILL §6.1)

After the Beamer PDF is final, paste it back into the official pptx:
`pdftoppm -png -r 300` to render, then run the skill's
`scripts/package_pptx.py` (lock-file check → automatic template backup →
delete sample slides → blank layout → full-bleed paste → re-open verify;
a render directory contaminated with non-page images is rejected on size
mismatch).
⚠️ A `~$xxx.pptx` lock file in the directory = PowerPoint has it open; the
script refuses to write.

## Provenance

- The template comes from one real conference-talk engagement (2026-08,
  official pptx template extraction-reuse route, multiple rounds of visual
  acceptance), generalized: conference brand assets stay off-repo (supply your
  own), palette values are resettable macros.
- Skeleton: derived frame-by-frame from the battle-tested `conference.tex`,
  sanitized; the original filled-in deck (real title/content/images) stays in
  its source project, **not in this repo**.

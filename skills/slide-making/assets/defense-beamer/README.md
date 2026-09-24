# Defense Beamer Theme (beamerthemeDefense) + Proposal-Defense Skeleton

A generic Beamer theme for academic defense / thesis proposal / group
meetings: top navy banner (optional university emblem + university/college
wordmarks) + bottom section progress bar + TOC/divider/cover pages, plus four
lightweight content components. The bundled `defense.tex` is a **sanitized
proposal-defense skeleton** (25 pages covering all archetypes; archetype
structure and component geometry are battle-tested, content is placeholder
text that doubles as filling instructions).

## Files

| File | Purpose |
|------|---------|
| `beamerthemeDefense.sty` | Theme file v2.3 (banner / progress bar / TOC / section dividers / cover / components; all fonts `\IfFontExistsTF`-guarded with per-platform fallback — see the Fonts section below; Latin/math fonts stay at Beamer defaults) |
| `defense.tex` | Proposal-defense skeleton (sanitized, 25 pages: cover / TOC / 5 section dividers / three-card page / bullets+warnings overview / research-framework tikz / technical route / schedule / closing) |
| `defense.pdf` | Compiled preview of the above (WSL fallback-font version: body in heiti, banner in kaiti; macOS compilation renders the original HarmonyOS Sans + XingKai look) |
| `campus-emblem.png` | **Not bundled — supply your own**: put your university emblem PNG next to the deck file and it joins the banner automatically (5 mm tall, best on reversed-out backgrounds); without it the banner falls back to a pure-text wordmark |

## Quick start

Put `beamerthemeDefense.sty` next to your deck file (emblem optional) and set
the banner's university/college names:

```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{Defense}

% Banner wordmarks (placeholder defaults — must be replaced with your own)
\renewcommand{\DefenseUniv}{XX University}
\renewcommand{\DefenseUnivEn}{XX University}
\renewcommand{\DefenseCollege}{XX College}
\renewcommand{\DefenseCollegeEn}{College of XX}

% Bottom progress-bar entries (comma-separated, matching \section order;
% current section highlighted, the rest grayed; if unset, the footer shows
% only the page number)
\DefenseSetProgress{Background, Literature, Research, Challenges, Plan}

% Section-divider subtitles (comma-separated, matching \section order;
% if unset, no subtitle line)
\DefenseSetSectionDesc{One-line subtitle 1, Two, Three, Four, Five}

\title{Thesis Title}
\subtitle{Thesis Proposal}   % small text at the top of the cover
\author{Candidate: XXX \and Advisor: Prof. XXX}
\institute{XX University · XX College}
\date{Month 2026}

\AtBeginSection[]{\frame{\sectionpage}}   % auto-insert a divider per section (optional)

\begin{document}
\begin{coverframe}          % cover: keeps the banner, hides progress bar and page number
  \titlepage
\end{coverframe}
\begin{frame}{Outline}
  \begin{outlinelist}       % outline entries: auto-numbered; subtitle = one-line description
    \outlineitem{Background}{One-line description.}
    \outlineitem{Literature}{One-line description.}
    \outlineitem{Research}{One-line description.}
    \outlineitem{Challenges}{One-line description.}
  \end{outlinelist}
\end{frame}
...
```

Compile with **xelatex** (fonts load through fontspec/xeCJK):
`latexmk -xelatex defense.tex`.
After putting paper figures into the `figures/` subdirectory, uncomment the
`\includegraphics` lines on the text+figure pages and delete the placeholder
boxes.

## Content components (lightweight alternatives to full-page color blocks; stackable on one page)

| Environment | Form | Use |
|-------------|------|-----|
| `point{title}` | Orange left bar + navy bold title | Grouped bullets, method threads |
| `warn{title}` | Light-red ground + orange left bar | Limitation / risk warnings |
| `card{title}` | Light-blue rounded card | Multi-column side-by-side (with `columns[0.325]`×3) |
| `band` | Navy ground, reversed-out text | Conclusion / entry-point banner |

## Battle-tested archetype cheat sheet (see defense.tex)

| Archetype | Location | Recipe |
|-----------|----------|--------|
| Three cards side-by-side | Background / objectives / contributions | `columns[0.325]` × 3 + `card` |
| Review page (threads + gaps) | Literature review Ⅰ/Ⅱ/Ⅲ | `point` grouped bullets + `warn` gap warnings |
| Research gap + entry point | Gap frame | `point` numbered items `\item[Ⅰ]` + `band` entry-point banner |
| Full-chain framework diagram | Research framework overview | Pure tikz `stage` node chain + dashed feedback arcs |
| Text+figure pages | Research content Ⅰ/Ⅱ | Left `point`×2, right figure placeholder box (swap back to includegraphics after putting real figures in `figures/`) |
| Challenge–countermeasure table | Expected challenges & countermeasures | Two-column booktabs table + `\addlinespace` |
| Five-stage technical route | Technical route | tikz `cnode`+`bnode` vertically-stacked pairs |
| Schedule table | Work plan | Three-column booktabs table |

## Visual spec (three-color academic palette)

The whole deck uses only three colors (primary + accent + neutral gray; a
blue–orange complementary, colorblind-friendly scheme):

| Role | Value | Theme name | Use |
|------|-------|------------|-----|
| Primary, deep navy | `#1F3864` | `primary` | Top banner, title color, TOC/numbers, progress bar, block title bars, conclusion banner |
| Accent, warm orange | `#E87722` | `accent` | Title underline, divider-page big number and dash, keyword emphasis, warnings |
| Neutral gray | `#595959` | `muted` | Secondary text, subtitles |

| Element | Value |
|---------|-------|
| Top banner | Primary color, 8.3 mm tall (tunable via `\DefenseBannerHeight`) |
| Title underline | Accent orange, 0.7 pt, full width |
| Bottom progress bar | Primary color; current section white-highlighted, others gray; page number at the right end |

## Fonts (source-deck original setup, automatic fallback)

All theme fonts are guarded with `\IfFontExistsTF` and fall back per platform,
so compilation survives missing fonts:

| Platform | Body (Latin + CJK) | Banner CJK wordmark | Banner Latin wordmark |
|----------|--------------------|---------------------|-----------------------|
| macOS (original look) | HarmonyOS Sans SC | Xingkai SC Bold brush script | Zapfino flourishes |
| Windows | SimHei or HarmonyOS Sans SC | STXingkai (simulated bold) | Current Latin font |
| Linux | SimHei (simulated bold) | KaiTi (simulated bold) | Current Latin font |
| WSL (Windows fonts indexed) | SimHei (simulated bold) | STXingkai (simulated bold) | Current Latin font |

One-time WSL setup to index Windows fonts (afterwards the banner wordmark gets
the STXingkai brush script):

```bash
mkdir -p ~/.config/fontconfig && cat > ~/.config/fontconfig/fonts.conf <<'CONF'
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <dir>/mnt/c/Windows/Fonts</dir>
</fontconfig>
CONF
fc-cache -f   # afterwards `fc-list | grep -i xingkai` should show STXingkai
```

Latin/math fonts are not set separately (Beamer defaults apply); the banner's
CJK brush-script wordmark and Zapfino Latin flourishes follow the source
deck's original spec.

To swap fonts manually, edit the [Fonts] section of `beamerthemeDefense.sty`.
**Note**: probing for a single-word font name (e.g. `Zapfino`) that is missing
makes fontspec leave kpathsea errors in the log; the theme avoids this by
probing with the multi-word name `HarmonyOS Sans SC` for platform detection.

## Provenance

- The visual spec comes from one university thesis-proposal pptx replication
  (2026-09, verified through multiple rounds of visual acceptance),
  generalized: the university emblem stays off-repo (supply your own),
  university/college names are resettable macros.
- Skeleton: derived frame-by-frame from the battle-tested `defense.tex`,
  sanitized; the original filled-in version (real title/name/images) stays in
  its source project, **not in this repo**.

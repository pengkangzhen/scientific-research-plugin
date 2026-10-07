---
name: poster-making
description: >
  Turn a finished paper into single-page visual derivatives: an academic
  conference poster (A0/A1), a journal graphical abstract, and a
  social-media announcement card. One content-compression pipeline
  (poster narrative with word budgets, reading-distance type scale, and
  figure reuse); render route chosen by a decision table: official
  conference template > LaTeX beamerposter/tikzposter (math-heavy) >
  HTML→Playwright vector PDF (default). Canvas sizes come from
  assets/specs.json — never hardcode.
  Use this skill whenever the user wants a conference/scientific poster,
  a graphical abstract / visual abstract / TOC graphic for journal
  submission, or a "paper is out" announcement card for X/Twitter,
  LinkedIn, WeChat — even if they never say "poster". Also covers
  Xiaohongshu (RedBook) multi-image note cards: cover + auto-paginated
  content cards (1080×1440, CJK-first) with an optional cookie-based
  auto-publish — a Python/uv pipeline (§4.5, full playbook in
  references/xhs-playbook.md), not render.mjs.
  Triggers: "poster", "A0", "make a poster", "conference poster",
  "graphical/visual abstract", "TOC graphic", "announcement card",
  "paper card", "publication card", "social-media paper figure",
  "WeChat moment figure", "Xiaohongshu", "RedBook", "xhs", "note cards".
license: MIT
---

# Poster-Making Skill (paper → poster / graphical abstract / announcement card / RedBook note)

Single-page visual derivatives of a finished paper (plus one multi-image
exception: Xiaohongshu note cards, §4.5). The skill's core value
is NOT the rendering (templates + one script do that) but the **content
compression**: a paper is written to be read at 30 cm; these products are
read at 1–5 m (poster), in a 200-px thumbnail (graphical abstract), or in a
scrolling feed (card). Everything below serves that inversion.

Research distillation (2026-10, sources in `assets/specs.json → meta`):
tool routes checked against CTAN/CRAN/journal author guidelines; type-scale
floors and word budgets from library guides and Purrington; the
better-poster debate read through its 2025 empirical evaluation (Bentsen &
Østergaard: mixed evidence vs. classic) — both templates are bundled, none
is imposed. Visual-engine iron rules (vector-not-screenshot PDF, canvas
fill, anti-card-wall) adopted from the official pdf skill's creative
pipeline. The OR/ML adaptation (which figure becomes the hero, how a
two-stage model compresses) is this pack's own.

## 0. Typical workflow

1. Gather inputs: paper source (`manuscript.tex` / PDF), figures produced
   by `figure-plotting`, the **venue's canvas prescription** (conference
   size policy or journal GA spec), language, deadline.
2. Decide the product and route via §1; read the target size from
   `assets/specs.json` (or the call-for-papers if stricter).
3. Compress content first (§2) — before touching any template. Then copy
   the matching template in full and edit content.
4. Render + verify in the §5 loop; deliver PDF + PNG (+ editable source).

## 1. Route decision table

Hard-constraint ordering: **venue compliance (size/template policy) >
math & figure fidelity > editability > production speed.**

| Situation | Route | Why |
|---|---|---|
| Conference provides an official template (any format) | Fill/extract the template (pptx route as in `slide-making` §6.1; tex route directly) | Venue compliance beats everything |
| Math-heavy poster (formulations are a selling point) | `assets/conference-poster-beamer.tex` (beamerposter; needs the `beamerposter` package — `tlmgr --usermode install beamerposter` or drop the .sty from any CTAN mirror into `~/texmf/tex/latex/beamerposter/`; Overleaf ships it) | Native LaTeX math matches the paper exactly |
| beamerposter unavailable AND network dead | `assets/conference-poster-tikz.tex` (tikzposter ships with TeX Live; verified zero-error on xelatex) | Zero-install fallback, still real math |
| Default poster / visual priority / CJK-heavy | `assets/poster-classic.html` or `poster-better.html` → `scripts/render.mjs` | Free layout, exact physical units, vector PDF + PNG in one pass |
| Graphical abstract | `assets/graphical-abstract.html` → `render.mjs --width <px from specs.json>` | Journal pixel specs; PNG (300 dpi-class) + vector PDF |
| Announcement card | `assets/social-card.html` → `render.mjs` | Screen specs (16:9 / 1:1 / LinkedIn / WeChat hero) |
| Xiaohongshu (RedBook) note cards | `scripts/render_xhs.py` + `publish_xhs.py` (Python/uv pipeline, §4.5) | 3:4 scrolling-feed format, CJK-first, auto-pagination, optional auto-publish |

Do not maintain parallel formats: one product, one route, one source file.

## 2. Content compression (do this before opening a template)

The #1 poster failure is **abstract relocation** — pasting paper text onto
a big canvas. Compress in this order:

1. **Claim first.** Write the ONE sentence a visitor must be able to repeat
   after leaving (number included: "−18.4% expected cost at equal daily
   spend"). This becomes the better-poster headline or the classic
   Takeaway box. If you cannot write it, the poster is not ready.
2. **Hero figure.** Pick ONE figure that proves the claim (usually the
   tradeoff/Pareto/convergence figure from `figure-plotting`, not the
   network schematic). It gets the largest area. Every other figure must
   earn its place — a poster with 8 figures has 0 heroes.
3. **Word budgets** (specs.json → conference_posters.typography_budget):
   whole poster 300–800 words; any single text block ≤ 60 words; methods
   prose ≤ 100 words (pseudocode skeleton 8–12 lines max); background =
   2–3 sentences + 1 gap sentence. Cut until it hurts, then cut the
   captions' dependencies ("as shown above" dies; captions are
   self-contained).
4. **Numbers as sculptures.** Key numbers become large standalone
   elements (56–90 pt), never buried in sentences. One or two per poster.
5. **Math minimization (LaTeX route):** objective + the 1–2 coupling
   constraints that carry the idea. Not the whole model. Symbol legend one
   gray line. On the HTML route, crop equations from the paper PDF
   (`pdfcrop`) rather than re-typesetting — font mismatch is visible.
6. **Area budget:** text 20–25% / graphics 40–45% / whitespace 20–30%.
   A half-empty bottom or a text wall both fail (the bundled HTML
   templates stretch figure slots to enforce the fill rule).
7. **QR code** links to DOI/arXiv page (paper, data, code). Generate:
   `uv run --with qrcode, pillow python -c "import qrcode; qrcode.make('https://doi.org/...').save('qr.png')"`
   — ≥ 12 mm printed side on posters, quiet zone 4 modules (specs.json →
   qr_code).

## 3. Visual system (shared by all templates)

- **Type scale, reading-distance floors** (A0; specs.json has the numbers):
  title 72–85 pt (3–5 m) / section heads 36–48 pt / body ≥ 24 pt (1–1.5 m)
  / captions ≥ 18 pt / ≤ 4 scale steps total. Never shrink type to fit
  more text — cut text.
- **Physical units are iron** on posters: HTML templates use mm/pt
  directly (`@page { size: 841mm 1189mm }`), so what you see is what
  prints. px belongs to screen products only (GA, cards).
- **Palette:** the pack's five-color system (navy/orange/teal/gray/light —
  same values as `slide-making`), so a group's deck and poster read as one
  family. Swap values, keep luminance roles.
- **Fonts:** Times New Roman for Latin/digits, SimSun/宋体 for CJK — both
  template routes ship this stack with fallbacks. For print delivery,
  verify embedding: `pdffonts poster.pdf` — every row must say `yes`
  (Chromium subsets-embed automatically; xelatex embeds by default).
- **Anti-card-wall:** hierarchy comes from type size/weight/spacing, not
  from bordered boxes. ≤ 3 tinted/bordered containers per poster (the
  classic template's `.panel`+`.takeaway` already spend most of that).
  No 2×2 card grids; no decorative stock images; no timelines with
  connector lines (they misalign in print).
- **classic vs better-poster:** offer both, one sentence of guidance —
  classic for technical audiences who read at the poster (OR/ML
  sessions), better-poster for mixed/broad audiences and high-traffic
  sessions. Empirical evidence does not crown either (2025 field study);
  the author's session context decides.

## 4. Product specs (read from assets/specs.json — never hardcode)

| Product | Canvas source | Notes |
|---|---|---|
| Conference poster | specs.json → conference_posters.sizes (A0/A1/48×36 in, portrait or landscape) | The venue's size policy wins over presets; change BOTH [SIZE] places in the template |
| Graphical abstract | specs.json → graphical_abstracts (Elsevier 1328×531, IEEE 660×295 ≤45 KB, Cell 1200×1200 square, …) | **INFORMS journals and AGU have NO GA channel** — for those outlets the announcement card IS the visual abstract |
| Announcement card | specs.json → social_cards (X 1200×675 / square 1080×1080 / LinkedIn 1200×628 / WeChat hero 900×383) | Element canon: claim headline + one visual + authors + journal/DOI. IEEE ≤45 KB: `pngquant` or JPEG q85 after export |
| Xiaohongshu note cards | Fixed 1080×1440 (3:4) in `render_xhs.py` — deliberately NOT in specs.json (platform screen format, not a publisher canvas) | Copy contract, themes, and publishing flow in `references/xhs-playbook.md` |

Banner-shaped GA (Elsevier/Wiley/IEEE) uses the bundled template's
left→right flow (problem → method → key result); Cell-style square stacks
the same three panels vertically.

## 4.5 Xiaohongshu (RedBook) note cards — xhs pipeline

The one product here that is NOT single-page: a RedBook note is a cover
image + 1–N content images consumed in a vertical feed. It runs on its own
Python/uv pipeline (not `render.mjs`):

```bash
cd <this skill dir>
uv sync && uv run --no-sync playwright install chromium   # once
uv run --no-sync python scripts/render_xhs.py note.md -o ./xhs_cards/<slug>/ -m auto-split
uv run --no-sync python scripts/publish_xhs.py -t "标题" -d "正文" -i cover.png card_1.png --dry-run   # then --private, then public
```

Two content modes — creation rights decide:
- **User supplied full copy → render verbatim.** Never rewrite a word.
- **User gave only a topic/material → write per the copy contract in
  `references/xhs-playbook.md`, render, and fix any ⚠️ warning by editing
  the copy (never by patching the renderer).**

Everything operational lives in `references/xhs-playbook.md` (single
source for the copy contract: publish title ≤20 UTF-16 units, ranking
entries 3–10 with ≤32-char one-liners; theme registry
`assets/themes/themes.yaml`; layout samples in `layouts/`). Publishing
needs `XHS_COOKIE` in `.env` (template `env.example.txt`; never committed)
— the gate is dry-run → private → public, spaced out to avoid platform
rate limits.

## 5. Render and verify (mandatory loop, after every content change)

### 5.1 Renderer preflight (borrowed from the official pdf skill)

`scripts/render.mjs` needs node ≥ 18 + the `playwright` npm package +
Chromium (~150–300 MB download). Before installing anything, probe:
`node render.mjs --help` (import failure = package missing) and check
`~/.cache/ms-playwright`. **If missing, ask the user first** — state the
download size; do not auto-install and do not silently fall back to
screenshots-as-PDF. If the user declines: LaTeX routes still work; the
HTML route stops (no stealth workarounds).

### 5.2 Render

```bash
node scripts/render.mjs poster.html                 # PDF + 2x PNG, size from @page
node scripts/render.mjs ga.html --width 1328px      # journal pixel override
```

Vector PDF via `page.pdf()` (never screenshot-wrapped), PNG via 2×
screenshot for journal bitmap specs. The script prints an OVERFLOW-X
warning on horizontal overflow — treat any warning as a blocker.

### 5.3 LaTeX compile

`xelatex conference-poster-tikz.tex` (verified: 0 errors) or
`xelatex conference-poster-beamer.tex` ×2 (verified: 0 errors once the
`beamerposter` package is present — install lines in the template header).

### 5.4 Visual acceptance (same discipline as `figure-plotting`)

1. Render PNG (done by render.mjs; for LaTeX A0 use `pdftoppm -png -r 40
   poster.pdf prefix`, or `gs -sDEVICE=png16m -r40 -o page.png poster.pdf`
   where poppler is not installed).
2. Look at the image: bottom void? clipped columns? overlapping labels?
   tofu boxes (missing CJK font)? QR present?
3. Fix template → re-render → re-look. Numbers beat impressions: the
   canvas must be the prescribed size (render.mjs prints it; verify
   `2383.94 × 3370.39 pt` ≈ A0 via `gs ... /MediaBox get ==`).
4. Check fonts embedded (`pdffonts`) before telling the user "done".

## 6. Poster talk (elevator pitch)

Poster sessions are conversations. Deliver alongside the poster:
- **30-second pitch** (for "so what's this about?"): claim → method in
  three words → the number → "want detail or the big picture?"
- **2-minute walkthrough**: problem → why existing tools fail → the ONE
  idea → hero figure → what changes for the practitioner.
- **Q&A pre-blocks** (as in `slide-making` §5): the two most likely
  attacks (feasibility, benchmark fairness) with one-line answers.
- Offer the QR link verbally when handing over.

## 7. Collaboration red lines

- **The venue's size policy is a hard constraint** — never "round up" a
  canvas or swap orientation without asking; printers reject at the door.
- Never delete a user-specified element (logo, funding block, template)
  to fix overflow — cut content (§2) or ask.
- No delivery without the §5 loop: render, look, fix, re-render, then
  report file paths (PDF + PNG + editable source), sizes verified.
- One product, one route: if the user asks for a second format mid-way,
  finish the first, then start it as a separate render.
- **XHS publish gate (§4.5):** no public post before `--dry-run` passes
  and a `--private` trial looks right; the cookie lives in `.env`, never
  in git; never publish a card that rendered with a truncation ⚠️ — fix
  the copy and re-render.

## 8. Bundled assets (copy in full, then edit)

| File | Product / route |
|---|---|
| `assets/specs.json` | Canvas + format specs, single source of truth, with sources & verified date |
| `assets/poster-classic.html` | A0 three-column classic poster (HTML route, verified render) |
| `assets/poster-better.html` | A0 better-poster 2.0 layout (HTML route, verified render) |
| `assets/graphical-abstract.html` | Banner GA, Elsevier default px (HTML route, verified render) |
| `assets/social-card.html` | 16:9 announcement card + variant notes (HTML route, verified render) |
| `assets/conference-poster-beamer.tex` | Math-heavy poster, beamerposter (Overleaf-ready) |
| `assets/conference-poster-tikz.tex` | Zero-install LaTeX fallback (xelatex, 0 errors verified) |
| `scripts/render.mjs` | HTML → vector PDF + 2× PNG, overflow audit |
| `scripts/render_xhs.py` | XHS: Markdown → cover + auto-paginated card PNGs (1080×1440; layouts `default` / `ranking`) |
| `scripts/publish_xhs.py` | XHS auto-publish: dry-run → private → public (cookie in `.env`) |
| `assets/themes/` | XHS theme registry — `themes.yaml` (single source) + theme CSS + `DESIGN_GUIDE.md` |
| `layouts/` | XHS layout sample images (re-render after layout changes, see its README) |
| `references/xhs-playbook.md` | XHS full playbook: copy contract, creation guide, themes, publishing flow |
| `pyproject.toml` / `uv.lock` / `env.example.txt` | uv environment + credential template for the XHS pipeline |

All four HTML templates share the five-color system and font stack, use
placeholder text as filling instructions, and were render-verified
2026-10-06 (classic & better at A0 3179×4494 px; GA at 1328×531; card at
1200×675). Local images in HTML: same-directory relative paths or base64
data URIs — absolute file:// paths are unreliable in headless Chromium.

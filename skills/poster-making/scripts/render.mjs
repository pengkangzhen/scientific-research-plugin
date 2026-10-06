#!/usr/bin/env node
// render.mjs — poster-making HTML renderer (vector PDF + hi-res PNG)
//
// Usage:
//   node render.mjs input.html [--output out_prefix] [--png-scale N]
//              [--width 841mm] [--height auto]
//
// Behavior (iron rules, learned from the official pdf skill's creative
// pipeline — do not "simplify" them away):
//   1. Vector PDF via page.pdf() with preferCSSPageSize — NEVER a
//      screenshot wrapped as PDF (raster blurs at any zoom).
//   2. PNG via page.screenshot({fullPage}) with deviceScaleFactor for
//      journal bitmap specs (300 dpi-class output).
//   3. Canvas size comes from the HTML's own `@page { size: ... }`
//      unless overridden by --width/--height. mm/pt units are physical
//      and exact in print.
//   4. Waits for document.fonts.ready (system Times/SimSun must be
//      loaded before measurement), then reports real overflow.
//
// Deps: node >= 18, playwright (npm). Browser binaries under
// ~/.cache/ms-playwright (PLAYWRIGHT_BROWSERS_PATH to override).
// If import fails: `npm i -g playwright` or run from a directory with
// playwright installed; the skill SKILL.md has the preflight dialog.

import path from "node:path";
import fs from "node:fs";
import { pathToFileURL } from "node:url";

function parseArgs(argv) {
  const a = { pngScale: 2, width: null, height: null, output: null };
  const pos = [];
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--output") a.output = argv[++i];
    else if (argv[i] === "--png-scale") a.pngScale = Number(argv[++i]);
    else if (argv[i] === "--width") a.width = argv[++i];
    else if (argv[i] === "--height") a.height = argv[++i];
    else pos.push(argv[i]);
  }
  if (!pos.length) { console.error("usage: render.mjs input.html [--output prefix] [--png-scale N] [--width W] [--height H|auto]"); process.exit(2); }
  a.input = path.resolve(pos[0]);
  a.output = a.output ? path.resolve(a.output) : a.input.replace(/\.html?$/i, "");
  return a;
}

// mm/pt/px -> CSS px (1in = 96px; 1mm = 96/25.4; 1pt = 96/72)
const toPx = (v) => {
  const m = String(v).trim().match(/^([\d.]+)\s*(mm|pt|px|in|cm)?$/);
  if (!m) return null;
  const n = Number(m[1]), u = m[2] || "px";
  return u === "mm" ? (n * 96) / 25.4
       : u === "cm" ? (n * 960) / 25.4
       : u === "pt" ? (n * 96) / 72
       : u === "in" ? n * 96 : n;
};

async function main() {
  const { chromium } = await import("playwright");
  const args = parseArgs(process.argv.slice(2));
  const html = fs.readFileSync(args.input, "utf8");

  // canvas from the file's own @page size unless overridden
  let width = args.width ? toPx(args.width) : null;
  let height = args.height === "auto" ? 0 : args.height ? toPx(args.height) : null;
  if (!width || height === null) {
    const m = html.match(/@page\s*{[^}]*size:\s*([^;}]+)/i);
    if (m) {
      const parts = m[1].trim().split(/\s+/);
      if (!width && parts[0]) width = toPx(parts[0]);
      if (height === null && parts[1] && parts[1] !== "auto") height = toPx(parts[1]);
      if (height === null && parts[0] && !parts[1]) height = width; // e.g. size: A4
    }
  }
  width = width || 1280;

  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: Math.round(width), height: Math.round(height || width * 0.75) },
    deviceScaleFactor: args.pngScale,
  });
  await page.goto(pathToFileURL(args.input).href, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(150); // settle layout after font swap

  // measure + overflow audit
  const audit = await page.evaluate(() => {
    const de = document.documentElement;
    return {
      scrollW: de.scrollWidth, clientW: de.clientWidth,
      scrollH: de.scrollHeight,
      overflowX: de.scrollWidth > de.clientWidth + 1,
    };
  });
  if (audit.overflowX) {
    console.warn(`⚠ OVERFLOW-X: content ${audit.scrollW}px > canvas ${audit.clientWidth}px — fix the HTML before delivery.`);
  }

  const pdfPath = args.output + ".pdf";
  await page.pdf({
    path: pdfPath,
    printBackground: true,
    preferCSSPageSize: true,
    width: args.width || undefined,          // only pin when user overrode
    height: args.height === "auto" ? undefined : (args.height || undefined),
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });

  const pngPath = args.output + ".png";
  await page.screenshot({ path: pngPath, fullPage: true });

  await browser.close();
  console.log(`canvas : ${Math.round(width)} x ${Math.round(audit.scrollH)} css px (scale ${args.pngScale}x for PNG)`);
  console.log(`vector : ${pdfPath}`);
  console.log(`bitmap : ${pngPath}`);
  if (audit.overflowX) process.exitCode = 1;
}

main().catch((e) => { console.error(e.message); process.exit(1); });

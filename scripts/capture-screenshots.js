#!/usr/bin/env node
/**
 * Capture preview screenshots for docs/.
 * Runs in CI from .github/workflows/screenshots.yml — Ubuntu has the
 * shared libs Chromium needs, which the Paperclip dev container does not.
 *
 * Local run (if you have system Chrome):
 *   PREVIEW_URL=https://phattbeats.github.io/sod2-diary/design/preview.html \
 *   OUT_DIR=docs/screenshots \
 *   node scripts/capture-screenshots.js
 */
const path = require('path');
const fs = require('fs');
const puppeteer = require('puppeteer');

const URL = process.env.PREVIEW_URL ||
  'https://phattbeats.github.io/sod2-diary/design/preview.html';
const OUT = path.resolve(process.env.OUT_DIR || 'docs/screenshots');

const SHOTS = [
  { name: 'preview-desktop',      width: 1280, height: 900,  full: true,  dpi: 2 },
  { name: 'preview-desktop-hero', width: 1280, height: 720,  full: false, dpi: 2 },
  { name: 'preview-mobile',       width: 390,  height: 844,  full: true,  dpi: 2 },
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  for (const s of SHOTS) {
    const page = await browser.newPage();
    await page.setViewport({
      width: s.width, height: s.height, deviceScaleFactor: s.dpi,
    });
    await page.goto(URL, { waitUntil: 'networkidle0', timeout: 60_000 });
    // Webfonts settled
    await page.evaluate(() => document.fonts && document.fonts.ready);
    // Tiny grace period so any final paint flushes
    await new Promise(r => setTimeout(r, 800));
    const out = path.join(OUT, `${s.name}.png`);
    await page.screenshot({ path: out, fullPage: s.full });
    console.log('wrote', out);
    await page.close();
  }

  await browser.close();
})().catch(err => {
  console.error(err);
  process.exit(1);
});

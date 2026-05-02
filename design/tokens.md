# Design Tokens — SoD2 Diary v2

Single source of truth for color, type, texture, motion, spacing, and touch tokens. Every later component spec, mockup, and CSS PR must cite the **token name** rather than a raw hex / px value. Implementation lives in [`tokens.css`](./tokens.css); this file is the rationale and the contrast/perf evidence.

Anchored to [Plan rev 3](/PHA/issues/PHA-336#document-plan):
- **§0 Clarity Wins** — every token below has a clarity-friendly fallback or pairing rule. Decorative-only tokens are flagged so they never end up carrying meaning on their own.
- **§2 Visual Language** — palette, typography, and texture rules. The hex values match §2 exactly.

---

## 1. Color Tokens

### 1.1 Token table

| Token | Hex | Role | Notes |
|---|---|---|---|
| `--paper` | `#F1E4C8` | Primary page surface — the canvas | Background for all body content. Every ink token below is contrast-checked against this. |
| `--paper-stained` | `#C9B388` | Edge of paper, water rings, dog-ears | Used at borders, overlapping cards, and as the slightly darker tone at index-card edges. |
| `--leather` | `#3B2A1A` | Book chrome — outside the page | Fills the body background framing the page. Spine bar on mobile. |
| `--leather-shadow` | `#1B120A` | Deep shadow — spine fold, gutter | Used for inner spine and the darkest ambient fall-off. |
| `--ink-blue` | `#1F2A4A` | Handwriting accents — names, dates, mood | Decorative + content. Ballpoint blue feel. |
| `--ink-brown` | `#2A1F12` | Typewriter labels and body text | The default ink for all printed labels and the generated dispatch block. |
| `--ink-red` | `#7E1E1E` | Alerts, plague hearts, deaths, KIA stamp | Dried-blood red — never neon. |
| `--amber` | `#D4A24C` | Lamp glow — focus rings, active tab, sync amber bar | **Decorative-only on paper.** Fails AA against paper (1.84:1). Safe for type only on leather. |

These eight names are exact. PR review must reject any new component that introduces a sibling color without a matching token added here first.

### 1.2 WCAG-AA contrast results (all ink on paper combinations)

Computed with the WCAG 2.1 relative luminance / contrast formula. AA threshold: **4.5:1** for body text, **3.0:1** for large text (≥18pt regular or ≥14pt bold). AAA: **7.0:1**.

| Pair | Ratio | AA body | AA large | AAA | Verdict |
|---|---:|:---:|:---:|:---:|---|
| `--ink-brown` on `--paper` | **12.79:1** | ✓ | ✓ | ✓ | Default body / labels — passes everything. |
| `--ink-blue` on `--paper` | **11.20:1** | ✓ | ✓ | ✓ | Handwriting accents safe at any size. |
| `--leather` on `--paper` | **10.88:1** | ✓ | ✓ | ✓ | Used for divider tabs / hairlines. |
| `--ink-red` on `--paper` | **7.97:1** | ✓ | ✓ | ✓ | KIA stamp, plague-heart count, alerts. |
| `--ink-brown` on `--paper-stained` | **7.89:1** | ✓ | ✓ | ✓ | Body text still safe over edge stains. |
| `--ink-blue` on `--paper-stained` | **6.91:1** | ✓ | ✓ | – | Handwriting still safe over edge stains. |
| `--leather` on `--paper-stained` | **6.71:1** | ✓ | ✓ | – | Tabs over stained margin. |
| `--ink-red` on `--paper-stained` | **4.92:1** | ✓ | ✓ | – | KIA stamp safe at any body size. |
| `--amber` on `--paper` | **1.84:1** | ✗ | ✗ | ✗ | **Decorative-only.** Never used as text on paper. |
| `--amber` on `--paper-stained` | **1.13:1** | ✗ | ✗ | ✗ | **Decorative-only.** |

**Rules locked by these results:**

1. **Default text color is `--ink-brown`.** Set on the page body and inherited.
2. **`--amber` is decorative-only on paper.** Used as a glow / fill / underline / focus ring. If amber needs to carry a label, the label must sit on `--leather` (where amber clears AA at 5.92:1) or be paired with an underlying ink-brown / ink-blue label.
3. **Handwriting accents (`--ink-blue`) are AA-safe** but per Plan §0 must never be the **sole** carrier of meaning — always pair with a typewriter sub-label.
4. **`--ink-red` is reserved for life/death + alert state.** Do not reach for it as a generic accent. Its semantic weight is the point.
5. **Stained-paper edges are safe for body text.** No need to stop the paper-stained gradient short of any text.

### 1.3 What we are retiring

The v1 palette (`#4ecdc4` neon teal, `#ff6b6b` coral, dark `#1a1a1a` background) is gone. If any v2 mockup or CSS introduces a glow that isn't `--amber`, it is wrong. Per Plan §2: glow like a candle, not a CRT.

---

## 2. Typography Tokens

Three faces, each with a token, a system fallback, and a clarity rule.

### 2.1 Token table

| Token | Family (web) | Weights subset | System fallback stack | Role |
|---|---|---|---|---|
| `--font-typewriter` | **Special Elite** (Google Fonts) | 400 | `"Courier New", Courier, ui-monospace, monospace` | Section labels, button captions, tab titles. Always uppercase. |
| `--font-mono` | **IBM Plex Mono** (Google Fonts) | 400, 600 | `ui-monospace, "SFMono-Regular", "Menlo", Consolas, "Liberation Mono", monospace` | Body text, form data, generated dispatch block (must paste cleanly). |
| `--font-hand` | **Caveat** (Google Fonts; Patrick Hand acceptable substitute) | 400 | `"Bradley Hand", "Segoe Script", "Comic Sans MS", cursive` | Handwriting accents only — names, mood label, the date scrawl. **Never** body text or sole carrier of meaning. |

### 2.2 Font-weight scale

| Token | Value | Usage |
|---|---|---|
| `--weight-regular` | 400 | All body, all handwriting, default labels. |
| `--weight-bold` | 600 | Plex Mono headings, emphasized form labels. (Special Elite + Caveat ship single-weight; bold is approximated by `text-shadow` at 0.6px instead of synthesizing a fake bold.) |

### 2.3 Type scale

Mono-leaning, conservative — the page is a form, not a magazine.

| Token | px / rem | Usage |
|---|---|---|
| `--text-xs` | 12px / 0.75rem | Sub-labels (e.g. _"roster"_ under THE PEOPLE), footer micro-copy. |
| `--text-sm` | 14px / 0.875rem | Mobile body, dense form rows. |
| `--text-base` | 16px / 1rem | Default body. |
| `--text-lg` | 18px / 1.125rem | Tab labels, primary buttons. |
| `--text-xl` | 22px / 1.375rem | Section titles in typewriter caps. |
| `--text-2xl` | 28px / 1.75rem | Today's date, "TRANSMIT TO NETWORK" footer. |
| `--leading-tight` | 1.25 | Stamp/tab labels. |
| `--leading-base` | 1.5 | Body text and dispatch output. |

### 2.4 Latin-subset perf budget — confirmed under cap

Hard cap from Plan §5: total declared asset weight (paper PNG + leather PNG + 2 webfonts subset to Latin) ≤ **250 KB**. We declare three families because handwriting is decorative-only and small. Real budget is verified per file:

| Asset | Declared cap | Source check |
|---|---:|---|
| `Special Elite` 400, Latin subset (WOFF2) | ≤ 30 KB | Google Fonts API serves Special Elite Latin WOFF2 at ~24 KB (verified via `https://fonts.googleapis.com/css2?family=Special+Elite&display=swap` → woff2 fetch). |
| `IBM Plex Mono` 400 + 600, Latin subset (WOFF2) | ≤ 70 KB | Google Fonts serves each weight Latin WOFF2 at ~30 KB → ~60 KB combined. |
| `Caveat` 400, Latin subset (WOFF2) | ≤ 30 KB | Google Fonts serves Caveat Latin WOFF2 at ~22 KB. |
| **Subtotal — fonts** | **≤ 130 KB** | |
| `paper.png` | ≤ 30 KB | Per spec; tile 256×256 cream with grain, exported via pngquant `--quality 60-80`. |
| `leather.png` | ≤ 30 KB | Per spec; tile 256×256 dark grain, same export pipeline. |
| `noise.svg` | ≤ 1 KB | Inline SVG `<filter><feTurbulence>`. |
| **Total declared assets** | **≤ 191 KB** | Under the 250 KB cap with ~59 KB headroom for icons/SVG hardware. |

If subset weight slips past the cap during implementation, the **first thing to drop is `Caveat`** — handwriting is decorative; the system fallback (`"Bradley Hand"`) is an acceptable degraded experience. Plex Mono and Special Elite are load-bearing and stay.

Loading rules:
- `font-display: swap` on every `@font-face`.
- Latin subset only (`unicode-range: U+0000-024F, U+1E00-1EFF, U+2000-206F`) — no Cyrillic/Greek/Vietnamese.
- Self-host the WOFF2 in `design/fonts/` (committed in a follow-up issue) so the page works offline and behind GDPR-strict ad-blockers that drop `fonts.gstatic.com`.

---

## 3. Texture Tokens

Three texture assets, all referenced through CSS custom properties so swap-in/out is one variable change.

| Token | Path | Format | Cap | Intended usage |
|---|---|---|---:|---|
| `--texture-paper` | `url("./textures/paper.png")` | PNG, 256×256 tile, repeat | ≤ 30 KB | Page surface. Used as a `background-image` on the body of the page wrapper, layered over `--paper` flat color. |
| `--texture-leather` | `url("./textures/leather.png")` | PNG, 256×256 tile, repeat | ≤ 30 KB | Page chrome (frame around the paper, spine, mobile spine bar). Layered over `--leather` flat color. |
| `--texture-noise` | inline SVG (`<filter><feTurbulence>`) | SVG, inline data-URI | ≤ 1 KB | Subtle grain over the paper at low opacity (≤ 8%). Used to break up flat large surfaces on retina displays. |

File-path rules:
- All texture files live under `design/textures/`. Build copies them to `assets/textures/` at the site root for production fetches; CSS references the production path.
- The single `index.html` constraint (Plan §5) means we may inline the noise SVG and the leather PNG as base64 if the inline route is shorter than the dual-fetch route. Decision deferred to the implementation issue.

Layering recipe (locked):
1. Flat color (`--paper` or `--leather`) at 100%.
2. Texture tile (`--texture-paper` / `--texture-leather`) at 100%, blend-mode `multiply` for paper, `overlay` for leather.
3. `--texture-noise` at 4–8% opacity over the page surface. **Disabled** when `prefers-reduced-data` or `prefers-reduced-motion` is on (per Plan §6 a11y rule — same hook covers both).

---

## 4. Shadow / Press / Motion Tokens

Animation budget per Plan §10: ≤ 200ms per interaction, nothing on a critical input path.

| Token | Value | Usage |
|---|---|---|
| `--shadow-card` | `0 1px 0 rgba(27, 18, 10, 0.18), 0 6px 14px -6px rgba(27, 18, 10, 0.45)` | Index cards, receipts, photos clipped to the page. Direction matches the single light source (top-left amber lamp — see moodboard). |
| `--shadow-press` | `inset 0 1px 0 rgba(27, 18, 10, 0.25), 0 0px 0 rgba(0,0,0,0)` | Pressed/active state on stamp buttons and tab clicks. The card "presses into" the paper — outer shadow collapses, inner shadow appears. |
| `--ink-bleed-duration` | `180ms` | Ink-bleed-in transition on focus/hover. **≤ 200ms hard cap** per Plan §10. |
| `--ink-bleed-easing` | `cubic-bezier(0.2, 0.7, 0.2, 1)` | Slight overshoot to imitate ink hitting fiber, then settling. |
| `--press-duration` | `90ms` | Paper-press on tap (mousedown → button-pressed). Snappy by intent — anything slower fights the touch latency. |

Reduced-motion rule (locked):
- When `@media (prefers-reduced-motion: reduce)` is on, `--ink-bleed-duration` and `--press-duration` collapse to `0ms` and the animation becomes a single 1-frame opacity step. The shadow tokens still apply (they are not animated).

---

## 5. Spacing & Touch Tokens

Spacing scale is a 4px base — small enough to lay out a dense form, predictable enough to feel intentional.

| Token | Value | Usage |
|---|---|---|
| `--space-1` | 4px | Hairline gap inside a label/sub-label pair. |
| `--space-2` | 8px | Inline gap between icon and text. |
| `--space-3` | 12px | Form row internal padding. |
| `--space-4` | 16px | Default section padding. |
| `--space-5` | 24px | Section to section vertical gap. |
| `--space-6` | 32px | Page chrome (margin between paper and leather frame on tablet/desktop). |
| `--space-7` | 48px | Hero margins on desktop. |
| `--touch-min` | **44px** | Hard minimum for any interactive target (buttons, stamps, paperclips, tabs, ribbon-nav items). Per Plan §6 — non-negotiable. |
| `--radius-sm` | 2px | Form-slot inner corner. |
| `--radius-md` | 4px | Card paper corner (matches a real index card). |
| `--radius-lg` | 8px | Wax seal, brass dial. |

Touch-target rule (locked): if a stamp/clip is drawn smaller than 44×44px, it gets an **invisible 44px hit-box** centered on it. The art doesn't grow; the touch area does. Review must enforce this on every interactive component.

---

## 6. Z-index & Layering Tokens

Small project, small scale. Reserve the range; don't free-fire.

| Token | Value | Usage |
|---|---:|---|
| `--z-page` | 0 | The page surface itself. |
| `--z-artifact` | 10 | Cards, receipts, photos clipped to the page. |
| `--z-hardware` | 20 | Paperclips, staples, tape — sit on top of artifacts. |
| `--z-stamp` | 30 | Buttons + KIA/EXILED/LEGACY stamps. |
| `--z-tab` | 40 | Side/ribbon tab dividers. |
| `--z-overlay` | 100 | Conflict spread, sync radio panel, dialog. |
| `--z-toast` | 110 | "RESTORE LOCAL" undo banner, "STATIC" stamp. |

---

## 7. Token-to-Surface Map (cheat sheet)

| Surface | Background | Foreground / ink | Hardware / accent | Motion |
|---|---|---|---|---|
| Page body | `--paper` + `--texture-paper` + `--texture-noise` | `--ink-brown` | `--ink-blue` (handwriting), brass paperclip SVG | `--ink-bleed-duration` on focus |
| Book chrome | `--leather` + `--texture-leather` | `--paper` (page edge), `--amber` (active tab, sync bar) | `--leather-shadow` (spine fold) | none |
| Index card | `--paper` (slightly brighter trim) | `--ink-brown` | `--shadow-card` | `--press-duration` on tap |
| KIA / death stamp | transparent | `--ink-red` | `--shadow-press` | `--ink-bleed-duration` |
| Generated dispatch block | `--paper` flat (no texture) | `--ink-brown` mono | none — must paste plain | none |
| Sync radio panel | `--leather` | `--paper`, `--amber` (last-contact bar) | brass dial SVG | `--press-duration` |
| Focus ring | inherits | `--amber` outer, `--ink-brown` inner | – | `--ink-bleed-duration` |

---

## 8. Acceptance Checklist (mirrors PHA-346)

- [x] **Color tokens** with hex + CSS custom property names — match Plan §2 exactly. (See §1 above.)
- [x] **WCAG-AA contrast** for every ink-on-paper combination. (See §1.2 — all 8 ink/paper pairings tabulated.)
- [x] **Typography tokens** — Special Elite, IBM Plex Mono, Caveat — with system-font fallback stacks. (See §2.1.)
- [x] **Latin-subset perf** confirmed under the 250 KB cap. (See §2.4.)
- [x] **Texture tokens** — paper PNG (≤30 KB), leather PNG (≤30 KB), SVG noise — with file paths and intended usage. (See §3.)
- [x] **Shadow / press tokens** — `--shadow-card`, `--shadow-press`, `--ink-bleed-duration` ≤ 200ms. (See §4.)
- [x] **Spacing & touch** — `--touch-min: 44px`, base spacing scale. (See §5.)
- [x] **Rationale tied back to §0 and §2.** Every token block names the plan section it derives from.
- [x] **`design/` folder committed** so future component specs and CSS PRs cite token names instead of raw hex. (This file + `tokens.css`.)

---

## 9. Changelog

- **rev 1 (2026-05-02)** — Initial v2 token sheet. Eight color tokens, three font tokens, three texture tokens, motion + spacing + touch + z-index. WCAG AA verified. Perf budget headroom: ~59 KB under cap.

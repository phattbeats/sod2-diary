# Design System — SoD2 Diary v2

Compact public reference for the v2 design system. The exhaustive rationale lives at [`/design/tokens.md`](../design/tokens.md); this file is the at-a-glance summary you read before opening implementation files.

**Live preview:** https://phattbeats.github.io/sod2-diary/design/preview.html

---

## 1 · Palette

| Token | Hex | Role |
|---|---|---|
| `--paper` | `#F1E4C8` | Page surface — the canvas. |
| `--paper-stained` | `#C9B388` | Edge of paper, water rings, dog-ears. |
| `--leather` | `#3B2A1A` | Book chrome — outside the page. |
| `--leather-shadow` | `#1B120A` | Spine fold, deepest ambient. |
| `--ink-blue` | `#1F2A4A` | Handwriting accents — names, dates, mood. |
| `--ink-brown` | `#2A1F12` | Typewriter labels and body text (default). |
| `--ink-red` | `#7E1E1E` | KIA, plague hearts, alerts. |
| `--amber` | `#D4A24C` | Lamp glow — focus rings, active tab. **Decorative-only on paper.** |

**Contrast vs `--paper` (WCAG-AA):** all ink tokens pass AA body. `--ink-brown` 12.79:1 (AAA), `--ink-blue` 11.20:1 (AAA), `--ink-red` 7.97:1 (AAA), `--amber` **1.84:1 — FAIL**, decorative-only. Full table at [`tokens.md` §1.2](../design/tokens.md#12-wcag-aa-contrast-results-all-ink-on-paper-combinations).

---

## 2 · Typography

| Token | Family | Role | Notes |
|---|---|---|---|
| `--font-typewriter` | Special Elite (400) | Section labels, button captions, tab titles | Always uppercase. |
| `--font-mono` | IBM Plex Mono (400/600) | Body text, form data, generated dispatch block | Must paste cleanly. |
| `--font-hand` | Caveat (400) | Names, mood label, date scrawl | Decorative-only. Never sole carrier. |

System fallback stacks are defined in [`tokens.css`](../design/tokens.css). Latin-subset budget: ~110 KB combined fonts + ~60 KB textures = ~170 KB, under the 250 KB cap by ~80 KB. First drop if budget slips: `Caveat`.

**Type scale:** `--text-xs` 12px / `--text-sm` 14px / `--text-base` 16px / `--text-lg` 18px / `--text-xl` 22px / `--text-2xl` 28px.

---

## 3 · Motion

| Token | Value | Usage |
|---|---|---|
| `--ink-bleed-duration` | 180ms | Focus / hover ink-bleed-in (≤200ms hard cap). |
| `--ink-bleed-easing` | `cubic-bezier(0.2, 0.7, 0.2, 1)` | Slight overshoot, then settle. |
| `--press-duration` | 90ms | Paper press on tap. |
| `--shadow-card` | 1px hairline + 6px soft drop, top-left light source | Cards, receipts, photos. |
| `--shadow-press` | inset 1px hairline, outer collapses | Pressed/active state. |

`@media (prefers-reduced-motion: reduce)` collapses both durations to `0ms`.

---

## 4 · Spacing & Touch

| Token | Value | Usage |
|---|---|---|
| `--space-1` … `--space-7` | 4 / 8 / 12 / 16 / 24 / 32 / 48 px | 4px base scale. |
| `--touch-min` | **44px** | Hard minimum for any interactive target. Invisible hit-box if art is smaller. |
| `--radius-sm` / `--radius-md` / `--radius-lg` | 2 / 4 / 8 px | Form slot / index card / wax seal. |

---

## 5 · Texture

| Token | File | Cap | Usage |
|---|---|---|---|
| `--texture-paper` | `design/textures/paper.png` | ≤ 30 KB | Page surface, multiplied over `--paper` flat color. |
| `--texture-leather` | `design/textures/leather.png` | ≤ 30 KB | Book chrome, overlaid over `--leather`. |
| `--texture-noise` | inline SVG turbulence | ≤ 1 KB | Subtle grain at 4–8% opacity. Disabled under reduced-data. |

PNG files are not yet sourced — the live preview uses flat color + noise overlay only. Texture sourcing belongs to PHA-347.

---

## 6 · Z-index reservations

`--z-page: 0`, `--z-artifact: 10`, `--z-hardware: 20`, `--z-stamp: 30`, `--z-tab: 40`, `--z-overlay: 100`, `--z-toast: 110`. Don't free-fire — request a new band here if you need one.

---

## 7 · Locked rules (mirror of `/docs/README.md`)

1. Clarity wins. Real `<input>`/`<label>`/`<button>` under every painted control.
2. `--amber` decorative-only on paper.
3. Handwriting decorative-only — always pair with typewriter sub-label.
4. `--ink-red` for life/death + alert state.
5. Animation ≤ 200ms.
6. Touch targets ≥ 44×44px.
7. Generated dispatch stays plain mono.
8. Total declared assets ≤ 250 KB.

---

## 8 · See also

- [Mood board](../design/moodboard.md) — five reference surfaces with token annotations.
- [Tokens (long-form)](../design/tokens.md) — rationale, contrast proofs, perf evidence.
- [Tokens (CSS)](../design/tokens.css) — implementation.
- [Design philosophy (PHA-336 Plan rev 3)](/PHA/issues/PHA-336#document-plan) — the "why."

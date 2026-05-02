# Mood Board — SoD2 Diary v2 ("The Network Logbook")

> _"Everyone's experiences matter. By sharing what we see and do, we build the knowledge that keeps us all alive."_

This is the visual reference sheet for v2. Every later spec, mockup, and CSS implementation lives downstream of this page and the [design tokens](./tokens.md). When in doubt, reach for the material that maps to the surface you are styling — and remember the tiebreaker from [Plan §0](/PHA/issues/PHA-336#document-plan): **clarity wins**.

Aesthetic in one line: a worn leather field journal kept by a survivor — paperclips, ink, masking tape, an amber lamp on the desk.

---

## Reference Grid

Five references, one per surface. Each entry names the asset, the surface it informs, what to take from it, and what to leave behind.

### 1. Leather book cover — informs `--leather`, `--leather-shadow`, page chrome

- **Source — locked: ambientCG (CC0).** Library URL: <https://ambientcg.com/list?type=Material&category=Leather>. Pick the dark-umber tile that matches `--leather` (`#3B2A1A`) under a top-left amber light — recommended candidate: **Leather011** (<https://ambientcg.com/view?id=Leather011>). Backup library if ambientCG is unreachable: Polyhaven (<https://polyhaven.com/textures/leather>), also CC0.
- **Pick rule:** 1K-resolution Color map only. We do not ship Normal / Roughness / Displacement — the journal is flat. Rename to `design/textures/leather.png` after pngquant `--quality 60-80` (must clear ≤ 30 KB per `tokens.md` §3).
- **Take:** deep umber grain (`#3B2A1A`), uneven edge highlight, slight warp at corners. The shadow falls darkest near the spine and the bottom edge.
- **Leave:** any embossed brand mark, gold leaf foil, decorative cartouche. The book is anonymous — the only mark we will paint on it is a simple "NETWORK" crosshair-in-circle (see Plan §10, brand/IP note).
- **Surface usage:** body background outside the page; spine bar across the top of the layout on mobile; full bound cover behind the two-page spread on desktop.

### 2. Aged cream paper sheet — informs `--paper`, `--paper-stained`, page surface

- **Source — locked: ambientCG (CC0).** Library URL: <https://ambientcg.com/list?type=Material&category=Paper>. Pick the warm-cream tile closest to `--paper` (`#F1E4C8`) — recommended candidate: **Paper003** (<https://ambientcg.com/view?id=Paper003>). Backup library if ambientCG is unreachable: Polyhaven (<https://polyhaven.com/textures/paper>), also CC0.
- **Pick rule:** 1K-resolution Color map only. If the source tile has a yellow cast, neutralize it in pngquant or shift the `--paper` flat color underneath (the texture is overlaid `multiply` per `tokens.md` §3 layering recipe). Rename to `design/textures/paper.png` after pngquant `--quality 60-80` (≤ 30 KB).
- **Take:** warm cream base (`#F1E4C8`) drifting to `#C9B388` at the edges; faint stains and water rings; tooth (the slight fiber noise) visible only at large sizes; very subtle horizontal grain so handwriting reads "on the line" without us drawing rules.
- **Leave:** heavy yellow tea-stain saturation, dramatic burn marks, holes. Anything that competes with ink for attention. The paper is the canvas — it must stay quiet enough that body text sits at AA contrast (verified in tokens.md).
- **Surface usage:** primary content area for every section; index card background on the People tab (a brighter trim of the same paper); torn-receipt strips for events.

### 3. Hand-written ballpoint blue + typewriter brown — informs `--ink-blue`, `--ink-brown`, `--ink-red`

- **Source candidates (CC0):**
  - Photographs of vintage field journals (Wikimedia Commons, search `field notebook 1940s`).
  - Typewriter sample sheets (e.g. Smith Corona public-domain manuals).
  - Reference for blood-ink red: ferric-tannate iron-gall ink samples, Wikimedia.
- **Take:**
  - **Faded ballpoint blue (`#1F2A4A`)** for handwriting accents — names, the daily date, mood label. Slightly inconsistent stroke pressure is what sells it; never crisp.
  - **Typewriter brown-black (`#2A1F12`)** for printed labels and body data — even, mechanical, slightly impressed into the paper.
  - **Dried-blood red (`#7E1E1E`)** for KIA stamps, plague hearts, deletions. Reads as "warning" without ever feeling neon.
- **Leave:** glossy gel-pen blacks, pure `#000`, fluorescent reds, marker bleed. Nothing that looks like it shipped from a printer cartridge in 2024.
- **Surface usage:** all interactive labels and body text (typewriter brown); name + mood + handwritten accents (ballpoint blue, decorative-only per Plan §0); alerts, deaths, plague hearts (dried-blood red).

### 4. Brass paperclip / single staple / masking tape — informs hardware SVGs, `--shadow-card`, `--shadow-press`

- **Source candidates (CC0):**
  - Unsplash: `brass paperclip macro`, `office staple paper`, `masking tape edge torn`.
  - We will redraw these as inline SVGs in the final build — the photo refs are only there to set proportion, sheen, and shadow direction.
- **Take:** warm brass highlight (a hint of `--amber` `#D4A24C`), soft drop shadow at ~6° offset (paper-press), slight rotation per element so the page never feels print-aligned. Tape edges are torn, never scissor-clean.
- **Leave:** modern plastic-coated clips, color-anodized binder clips, washi-tape patterns. The hardware is plain office-supply circa "any decade."
- **Surface usage:** clipping index cards onto the People tab; stapling resource receipts to the page; taping notes to events. Hardware is also the cue for "this group of fields belongs together" — it groups visually without needing a box border.

### 5. Amber desk-lamp glow on dark wood — informs `--amber`, focus ring, active-tab highlight

- **Source candidates (CC0):**
  - Unsplash: `tungsten desk lamp warm`, `amber lamp dark room`.
  - Polyhaven HDRI thumbnails: `studio_country_hall` (a warm-low-light reference).
- **Take:** soft amber falloff (`#D4A24C`) — the glow brightens the page edge nearest the lamp and quietly fades. This is the **only** glow allowed in the v2 palette. It is decorative-only and never used as text on paper (1.84:1 — fails AA, see tokens.md).
- **Leave:** any neon, any cyan/teal, any RGB-keyboard rainbow. The current `#4ecdc4` and `#ff6b6b` retire here.
- **Surface usage:** focus ring on inputs, active tab indicator, "TRANSMIT" wax-seal hover state, sync-radio "last contact" amber bar across the spine. On leather (`--leather` `#3B2A1A`) amber clears AA at 5.92:1 — that is the safe place to put amber type if needed.

---

## Annotation Map (which image informs which surface)

| Reference | Informs | Tokens it anchors |
|---|---|---|
| 1. Leather book cover | Body background, spine, book chrome | `--leather`, `--leather-shadow` |
| 2. Aged cream paper | Page surface, index cards, receipts | `--paper`, `--paper-stained` |
| 3. Ballpoint + typewriter ink samples | Handwriting accents, labels, body text, KIA / plague-heart red | `--ink-blue`, `--ink-brown`, `--ink-red` |
| 4. Paperclip / staple / tape | Hardware SVGs, drop-shadow direction, press feedback | `--shadow-card`, `--shadow-press` |
| 5. Amber lamp on dark wood | Focus glow, active tab, sync-radio amber bar | `--amber` |

---

## Composition Notes (for the next step — annotated mockups)

- **Page sits inside book, not flush.** Always show ~6–10px of leather framing the paper on every breakpoint, even mobile. The frame is what sells "you are inside a book."
- **Slight rotation per artifact, never per page.** The page itself is square to the screen so reading is fast; only the artifacts on it (cards, receipts, photos) rotate ±1.5°.
- **Hardware groups, never decorates.** A paperclip belongs on something — clipping a card, a receipt, a photo to the page. Never floating.
- **One light source.** Amber falls from the top-left on every breakpoint. Shadows direction-locked accordingly so the book feels like one consistent space.
- **No CRT, no neon.** If a glow is needed, it is amber and it is ≤ 8% opacity at the bloom edge. The plan already retires the v1 teal/coral palette — call this out in any review where someone reaches for it again.

---

## Asset Sourcing TODO (handed off to the texture-fetch follow-up)

- [ ] Download Color map for **ambientCG → Paper003** (<https://ambientcg.com/view?id=Paper003>), pngquant `--quality 60-80`, commit at `design/textures/paper.png` (≤ 30 KB cap from `tokens.md` §3).
- [ ] Download Color map for **ambientCG → Leather011** (<https://ambientcg.com/view?id=Leather011>), pngquant `--quality 60-80`, commit at `design/textures/leather.png` (≤ 30 KB cap).
- [ ] Author the SVG noise overlay (≈1 KB inline) per the spec in `tokens.md`.
- [ ] Redraw paperclip / staple / tape / wax-seal / radio-dial as inline SVGs (per Plan §9.5 asset inventory).

The two ambientCG slugs above are recommended candidates — the picker may swap to a sibling tile in the same library if a Color map matches the moodboard `take` lines more cleanly. Any swap stays inside the locked source decision (ambientCG primary, Polyhaven backup) and updates the attribution row below.

---

## Attribution Block

Required even for CC0 (license terms permit no attribution, but we keep the row so the source is auditable).

| File | Source URL | Creator | License | Retrieved |
|---|---|---|---|---|
| `design/textures/paper.png` | <https://ambientcg.com/view?id=Paper003> | ambientCG (Lennart Demes) | CC0 1.0 | _on download_ |
| `design/textures/leather.png` | <https://ambientcg.com/view?id=Leather011> | ambientCG (Lennart Demes) | CC0 1.0 | _on download_ |

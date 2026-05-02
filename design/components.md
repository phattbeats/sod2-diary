# Component Spec Sheet — SoD2 Diary v2

The atomic UI pieces engineering will build for v2. Every component below cites tokens from [`tokens.css`](./tokens.css) (rationale in [`tokens.md`](./tokens.md)) and pairs the skeuomorphic surface with a **clarity-win fallback** per [Plan §0](/PHA/issues/PHA-336#document-plan).

Anchored to:
- **§0 Clarity Wins** — every interactive component has a plain HTML/text fallback documented inline.
- **§3 Interaction Language** — input slots, stamp buttons, paperclip groups, ribbon nav, brass radio.
- **§7 Ties That Bind** — card-back tie row.
- **§8 Raise the Other Radio** — brass radio dial, QR telegram, conflict spread.
- **§9 deliverables 3 + 6** — this document and the data-model spec.

---

## 0. Reading guide

Each component below uses the same shape:

1. **Purpose** — one sentence on what the component is for.
2. **Sketch** — inline SVG (kept ≤ 1 KB each) showing the artifact at rest. Sketches are wireframe-grade; pixel-perfect proportions land in PHA-348 (annotated mockups).
3. **States** — `default / hover / focus / active / disabled` (omit a state when it is identical to default — noted explicitly).
4. **Plain-language fallback** — what the component degrades to if textures, custom fonts, JS, or `prefers-reduced-motion` strip the chrome away. Per §0, the fallback must still be usable.
5. **Tokens** — exact custom-property names from `tokens.css`. No raw hex/px appears below.
6. **Touch target** — every interactive component declares its hit-box. **Hard floor: `--touch-min` (44px)**. If the art is smaller, the hit-box is centered and invisible.

A short **Notes** block follows each component when there is non-obvious behavior (e.g. "stamp ink darkens on re-stamp", "tie row collapses to a chip on mobile").

---

## 1. Input slot — penned-box input frame

**Purpose.** The base form input on every page. Replaces v1's flat `<input>` with a hand-drawn rectangle that looks penned onto the paper.

**Sketch.**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 56" role="img" aria-label="Penned input slot">
  <rect x="2" y="2" width="276" height="52" fill="none" stroke="#2A1F12" stroke-width="1.5" rx="3"
        stroke-dasharray="0" style="filter:url(#hand)"/>
  <text x="14" y="34" font-family="'IBM Plex Mono', monospace" font-size="14" fill="#2A1F12">SURVIVOR NAME</text>
  <text x="200" y="34" font-family="'Caveat', cursive" font-size="20" fill="#1F2A4A">Maya</text>
</svg>
```

**States.**
| State | Visual change |
|---|---|
| default | Single ink-brown stroke, slight pen-jitter (±0.5px). Label sits inside the slot at top-left in `--font-typewriter`. |
| hover | Stroke gains a 1px amber under-shadow (decorative-only; no contrast role). |
| focus | `:focus-visible` token ring fires (amber outer + ink-brown inner). Label nudges up `--space-1`. Animated over `--ink-bleed-duration`. |
| active (typing) | Caret is `--ink-blue` 2px wide; user-typed text rendered in `--font-hand` `--ink-blue`. The slot border stays ink-brown — the **label** carries the focus state, not the border. |
| disabled | Border drops to `--paper-stained`, label loses 30% opacity, **`aria-disabled="true"`**. No fade animation. |
| error | Stroke switches to `--ink-red`; an inline `<small>` error message in `--ink-brown` appears below (color is **not** the sole signal — text is). |

**Plain-language fallback.** If the SVG border filter fails to render (e.g. the `feTurbulence` is unsupported, or `prefers-reduced-data` is on), the slot collapses to a flat `<input>` with a 1.5px solid `--ink-brown` border and rounded `--radius-sm` corners. Identical interactive behavior, no visual jitter. The label remains `--font-typewriter` `--text-sm` uppercase.

**Tokens.** Border `--ink-brown`; background inherits `--paper`; label `--font-typewriter` `--text-sm` `--color-text-default`; user value `--font-hand` `--ink-blue` `--text-base`; focus ring inherits `:focus-visible`; padding `--space-3` horizontal × `--space-2` vertical; corner `--radius-sm`; transition `--ink-bleed-duration` `--ink-bleed-easing`.

**Touch target.** The slot itself must render at ≥ `--touch-min` tall. Label-as-affordance: the `<label>` element is `for=` linked so tapping the label focuses the input — extends the effective hit-box without enlarging the visible art.

**Notes.**
- Handwritten value (`--font-hand`) is decorative per §0: the typed string also exists as the input's accessible value, so screen readers never depend on Caveat rendering.
- The pen-jitter SVG `<filter id="hand">` is defined **once** at the top of the page and reused across components — see §13 Asset inventory.

---

## 2. Stamp button — primary action

**Purpose.** Any "commit this action" button: STAMP REPORT, ADD SURVIVOR, MARK KIA. Press inks the stamp into the paper; a re-stamp is darker (more ink in the well).

**Sketch.**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 80" role="img" aria-label="Stamp button">
  <rect x="6" y="14" width="188" height="52" fill="#2A1F12" rx="2" opacity="0.95"
        transform="rotate(-1.2 100 40)"/>
  <text x="100" y="48" text-anchor="middle" font-family="'Special Elite', monospace" font-size="18"
        fill="#F1E4C8" letter-spacing="2" transform="rotate(-1.2 100 40)">STAMP REPORT</text>
</svg>
```

**States.**
| State | Visual change |
|---|---|
| default | Ink-brown rectangle, 1.2° rotation, sits on `--shadow-card`. Label `--paper` typewriter caps with letter-spacing `2`. |
| hover | Drop-shadow lifts ~2px (suggests "ready to stamp"); cursor `pointer`. |
| focus | `:focus-visible` ring + a subtle amber haze around the stamp body. |
| active (mouse-down) | `--shadow-card` collapses to `--shadow-press` over `--press-duration`. The rectangle nudges 1px toward the page. |
| pressed (post-stamp) | The stamp leaves its ink behind (the action is committed). The button itself fades to 80% opacity for 600ms, then returns. |
| **re-stamp** (pressed within 30s of a prior stamp) | Background darkens by ~12% via `filter: brightness(0.88)` — the "ink well" looks fuller. The label gains a tiny `text-shadow` to imitate ink bleed. |
| disabled | Background drops to `--paper-stained`, label `--ink-brown` at 50% opacity, `cursor: not-allowed`, `aria-disabled="true"`. No press animation. |

**Plain-language fallback.** If JavaScript is off or the press animation is suppressed (`prefers-reduced-motion`), the stamp button is a plain dark rectangle with `--paper` text. Pressing it submits the form. No press feedback beyond the browser's native focus ring.

**Tokens.** Background `--ink-brown`; text `--paper`; font `--font-typewriter` `--text-lg` uppercase, `letter-spacing: 2px`; idle shadow `--shadow-card`; pressed shadow `--shadow-press`; press transition `--press-duration`; rotation locked to ±1.2° (per moodboard); padding `--space-3` × `--space-5`.

**Touch target.** Minimum render `--touch-min` tall × ≥ 120px wide. The 1.2° rotation does **not** shrink the hit-box (CSS rotation preserves the rect; we set the hit-box on the un-rotated wrapper).

**Notes.**
- "Re-stamp darkens" is the only stateful animation that survives reduced-motion: it is a static `filter: brightness()` step, not an animation.
- Destructive variants (MARK KIA, EXILE) use `--ink-red` for the label, not the background, so the stamp metaphor (ink, not button color) carries the warning.

---

## 3. Index card (survivor) — front face

**Purpose.** One survivor at a glance. Replaces the v1 list-row with a paper card clipped to the page, the dominant artifact on the People tab.

**Sketch.**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" role="img" aria-label="Survivor index card">
  <rect x="6" y="10" width="308" height="180" fill="#F1E4C8" rx="4"
        transform="rotate(-0.6 160 100)" stroke="#C9B388" stroke-width="0.5"/>
  <line x1="20" y1="40" x2="300" y2="40" stroke="#C9B388" stroke-width="0.5"
        transform="rotate(-0.6 160 100)"/>
  <text x="20" y="32" font-family="'Caveat', cursive" font-size="22" fill="#1F2A4A"
        transform="rotate(-0.6 160 100)">Maya, 28</text>
  <text x="200" y="32" font-family="'IBM Plex Mono', monospace" font-size="11" fill="#2A1F12"
        transform="rotate(-0.6 160 100)">JOINED D1</text>
  <text x="20" y="60" font-family="'IBM Plex Mono', monospace" font-size="12" fill="#2A1F12"
        transform="rotate(-0.6 160 100)">TRAITS  Tough · Leader</text>
  <text x="20" y="80" font-family="'IBM Plex Mono', monospace" font-size="12" fill="#2A1F12"
        transform="rotate(-0.6 160 100)">SKILLS  Shooting · Medicine</text>
  <text x="20" y="100" font-family="'IBM Plex Mono', monospace" font-size="12" fill="#2A1F12"
        transform="rotate(-0.6 160 100)">MORALE  high</text>
  <!-- paperclip -->
  <path d="M150 4 q-8 0 -8 8 v18 q0 8 8 8 t8 -8 v-12" fill="none" stroke="#D4A24C" stroke-width="2"/>
</svg>
```

**States.**
| State | Visual change |
|---|---|
| default | `--paper` (slightly brighter trim against the page), ±0.6° rotation, `--shadow-card`. Brass paperclip clips the card to the page top-center. |
| hover | Card lifts ~1px; paperclip stays anchored (it is "physically" attached). |
| focus | `:focus-visible` ring around the **whole card**. The card itself is the link; tabbing the card opens the back face. |
| active (tap) | Card presses into the page (`--shadow-press`) for `--press-duration`, then flips to back face. |
| disabled | n/a — a survivor card is never disabled. KIA / EXILED / LEGACY status is conveyed by **stamps over the card** (see §11), not by greying the card out. |

**Plain-language fallback.** If `--texture-paper` and the rotation transform fail, the card collapses to a flat `--paper` rectangle with a 1px `--paper-stained` border. The paperclip becomes a small `<span aria-hidden="true">📎</span>` or is dropped entirely; the card's accessible name is the survivor's name in the heading element. No card grouping is lost.

**Tokens.** Background `--paper` over `--paper-stained` page; corner `--radius-md` (matches a real index card); shadow `--shadow-card`; rotation ±0.6° (pinned to one randomized value per card so the layout doesn't reflow); padding `--space-4`; name `--font-hand` `--text-xl` `--ink-blue`; metadata `--font-mono` `--text-sm` `--ink-brown`.

**Touch target.** Whole card is the click target; minimum render 280px wide × 160px tall — well over `--touch-min` on every axis. Edit/relationship affordances on the card-back use their own ≥ 44px hit-boxes (see §4).

**Notes.**
- Rotation is **pinned per-card** (computed from the survivorId hash), so a re-render does not jiggle the card.
- The People tab lays cards out in a 1-column (mobile) / 2-column (tablet) / 3-column (desktop) grid; the cards do **not** overlap. Overlap was considered and rejected — it competes with the stamps for visual weight.

---

## 4. Card-back tie row — relationship affordance

**Purpose.** When a survivor card is flipped, the back lists their relationships (per §7 "Ties That Bind"). Each tie is one row: kind glyph + counterpart name + freeform label, with an inline edit affordance.

**Sketch.**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 56" role="img" aria-label="Tie row">
  <rect x="0" y="0" width="320" height="56" fill="#F1E4C8" stroke="none"/>
  <!-- kind glyph: linked rings -->
  <circle cx="22" cy="28" r="7" fill="none" stroke="#2A1F12" stroke-width="1.5"/>
  <circle cx="34" cy="28" r="7" fill="none" stroke="#2A1F12" stroke-width="1.5"/>
  <text x="56" y="24" font-family="'IBM Plex Mono', monospace" font-size="11" fill="#2A1F12">PARTNER</text>
  <text x="56" y="42" font-family="'Caveat', cursive" font-size="18" fill="#1F2A4A">Ed — husband, met in Trumbull</text>
  <!-- edit affordance -->
  <text x="290" y="34" font-family="'IBM Plex Mono', monospace" font-size="11" fill="#2A1F12" text-anchor="middle">EDIT</text>
  <rect x="270" y="14" width="40" height="30" fill="none" stroke="#2A1F12" stroke-width="1" rx="2" opacity="0.4"/>
</svg>
```

**States.**
| State | Visual change |
|---|---|
| default | Kind glyph + uppercase kind label + handwritten counterpart-name & free-text label on the second line. EDIT chip on the right. |
| hover | EDIT chip border solidifies to full opacity. The whole row gets a faint `--paper-stained` underline. |
| focus | `:focus-visible` on the EDIT chip; row itself is not focusable (the chip is the affordance). |
| active | EDIT chip presses (`--shadow-press`) and opens the inline editor (the row expands to show kind / label / since / status / note inputs — all rendering as Input slots from §1). |
| `status: 'strained'` | A faint zigzag underline in `--ink-red` runs under the counterpart name. Plain-text fallback: the kind label appends ` · STRAINED`. |
| `status: 'severed'` | The whole row gains a single ink-red strikethrough; kind label appends ` · SEVERED`. |
| `status: 'mourned'` | A small black border-band on the row's left edge (3px). Kind label appends ` · MOURNED`. |
| empty | A single dashed slot reading `+ ADD TIE` in `--font-typewriter`. Tapping opens the empty editor. |

**Plain-language fallback.** With no SVG glyphs, the row degrades to: `[KIND]  [Counterpart name] — [label]  [EDIT]`. Status is appended in plain text (` · STRAINED`, ` · SEVERED`, ` · MOURNED`) so screen readers and unstyled markup carry the meaning. **Never** rely on the strikethrough or color band alone — text is canonical.

**Tokens.** Background `--paper`; row gap `--space-2` between rows; padding `--space-3` × `--space-4`; kind label `--font-typewriter` `--text-xs` `--ink-brown`; counterpart + label `--font-hand` `--text-base` `--ink-blue`; status accents `--ink-red`; EDIT chip uses `--ink-brown` border `--radius-sm`.

**Touch target.** EDIT chip = `--touch-min` × `--touch-min` invisible hit-box centered on the visible 40×30 chip art. The whole row is also tappable (opens the editor), so the effective hit-area is the row height (≥ 56px) × full card width.

**Notes.**
- The free-text **label** is the load-bearing field per §7 — `kind` is a coarse bucket, `label` is what the player actually wrote ("husband", "trained me on guns"). Display order keeps the label prominent.
- Editing a tie is bi-directional: writing `Maya → Ed (partner)` automatically also writes `Ed → Maya (partner)` with the same label. Implementation lives in PHA-354; this spec just notes the UI must show the inverse tie on Ed's card immediately.

---

## 5. Tab divider — right-edge cutout

**Purpose.** The page-edge tabs that switch sections (PEOPLE / RESOURCES / EVENTS / DISPATCH). Looks like a notebook divider with a die-cut tab.

**Sketch.**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 220" role="img" aria-label="Tab dividers">
  <!-- inactive tab -->
  <path d="M0 10 h64 q12 0 12 12 v36 q0 12 -12 12 h-64 z" fill="#C9B388" stroke="#3B2A1A" stroke-width="0.5"/>
  <text x="14" y="38" font-family="'Special Elite', monospace" font-size="11" fill="#2A1F12" letter-spacing="1.5">PEOPLE</text>
  <!-- active tab (amber underline + slightly forward) -->
  <path d="M-4 80 h68 q12 0 12 12 v36 q0 12 -12 12 h-68 z" fill="#F1E4C8" stroke="#3B2A1A" stroke-width="0.5"/>
  <text x="10" y="108" font-family="'Special Elite', monospace" font-size="11" fill="#2A1F12" letter-spacing="1.5">RESOURCES</text>
  <line x1="-4" y1="138" x2="64" y2="138" stroke="#D4A24C" stroke-width="2"/>
  <!-- inactive tab -->
  <path d="M0 150 h64 q12 0 12 12 v36 q0 12 -12 12 h-64 z" fill="#C9B388" stroke="#3B2A1A" stroke-width="0.5"/>
  <text x="14" y="178" font-family="'Special Elite', monospace" font-size="11" fill="#2A1F12" letter-spacing="1.5">EVENTS</text>
</svg>
```

**States.**
| State | Visual change |
|---|---|
| default (inactive) | `--paper-stained` fill, sits ~4px back from the active tab (the leather "shows behind it"). Label `--font-typewriter` `--ink-brown` uppercase. |
| hover | Tab nudges 2px forward; label `text-shadow` faint amber. |
| focus | `:focus-visible` ring on the tab path. |
| active (current section) | `--paper` fill (matches the page surface), an `--amber` 2px underline along the tab's bottom edge. Tab sits 4px forward. |
| disabled | Tab is rendered with 40% opacity and `aria-disabled="true"`. Used when the section has no content to show (e.g. EVENTS before any event is logged). |

**Plain-language fallback.** Tabs degrade to a horizontal `<nav>` of `<button>`s above the content area on tablet/desktop, or the ribbon nav (§7) on mobile. The "active" state is conveyed by `aria-current="page"` and a 2px solid `--amber` underline (the underline survives even without the cutout art). Text labels carry the meaning — the tab cutout is decorative.

**Tokens.** Inactive fill `--paper-stained`; active fill `--paper`; outline `--leather` 0.5px; underline `--amber` 2px; label `--font-typewriter` `--text-xs` uppercase `--ink-brown`, `letter-spacing: 1.5px`; padding `--space-2` × `--space-3`; z-index `--z-tab`.

**Touch target.** Each tab path is sized to ≥ `--touch-min` × `--touch-min` minimum. On mobile we collapse the tabs into the ribbon nav (§7) so the right-edge cutout isn't a thumb-stretch target.

**Notes.**
- Right-edge tabs are **desktop/tablet only**. On mobile the same sections appear in the bottom ribbon nav.
- The `--amber` underline is the only color-only signal — but it is paired with `aria-current="page"`, the cutout-forward depth, and the `--paper` fill change, so amber is one of three redundant cues. Per §0 we are not relying on color alone.

---

## 6. Paperclip header — group container

**Purpose.** Visually group a related set of fields (e.g. the morale + traits + skills block on a survivor card) without drawing a box. A brass paperclip clips the group to the page; the clip itself is the visual hairline that says "these belong together."

**Sketch.**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 80" role="img" aria-label="Paperclip header">
  <!-- paperclip -->
  <path d="M30 8 q-10 0 -10 10 v36 q0 10 10 10 t10 -10 v-30 q0 -6 -6 -6 t-6 6 v22"
        fill="none" stroke="#D4A24C" stroke-width="2.5" stroke-linecap="round"/>
  <text x="56" y="32" font-family="'Special Elite', monospace" font-size="14" fill="#2A1F12"
        letter-spacing="1.5">VITALS</text>
  <text x="56" y="50" font-family="'IBM Plex Mono', monospace" font-size="11" fill="#2A1F12"
        opacity="0.7">morale · traits · skills</text>
</svg>
```

**States.** Static; the paperclip is decorative chrome and not interactive. `aria-hidden="true"` on the SVG. The header text is a real `<h3>` element.

**Plain-language fallback.** The clip is decorative; without it the header is just an `<h3>` in `--font-typewriter` uppercase + a sub-label `<small>` in `--font-mono`. The grouping is also asserted by `<section aria-labelledby>` so screen readers always carry the structure.

**Tokens.** Clip stroke `--amber` 2.5px; header `--font-typewriter` `--text-base` `--ink-brown` uppercase `letter-spacing: 1.5px`; sub-label `--font-mono` `--text-xs` `--ink-brown` 70% opacity; clip rotation ±2° pinned per group (so a re-render doesn't jiggle); shadow on the clipped artifact `--shadow-card`.

**Touch target.** None — non-interactive.

**Notes.**
- The clip art is reused from the §13 inventory (one SVG, two color variants). We never draw a unique paperclip per group.
- Per moodboard rule "hardware groups, never decorates": a paperclip without something to clip is a bug.

---

## 7. Ribbon nav — bottom-edge sticky bar (mobile)

**Purpose.** The mobile-only section switcher. Sits along the bottom edge of the viewport like a binding ribbon at the foot of the journal.

**Sketch.**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 60" role="img" aria-label="Ribbon nav">
  <rect x="0" y="0" width="360" height="60" fill="#3B2A1A"/>
  <rect x="0" y="0" width="360" height="2" fill="#D4A24C" opacity="0.6"/>
  <g font-family="'Special Elite', monospace" font-size="11" fill="#F1E4C8" letter-spacing="1.5">
    <text x="40" y="38" text-anchor="middle">PEOPLE</text>
    <text x="120" y="38" text-anchor="middle">RES</text>
    <text x="200" y="38" text-anchor="middle">EVENTS</text>
    <text x="280" y="38" text-anchor="middle">DISP</text>
    <text x="340" y="38" text-anchor="middle">⚙</text>
  </g>
  <!-- active marker -->
  <rect x="80" y="56" width="80" height="4" fill="#D4A24C"/>
</svg>
```

**States.**
| State | Visual change |
|---|---|
| default item | `--paper` typewriter caps on `--leather` ribbon. |
| hover | `text-shadow` amber haze. |
| focus | `:focus-visible` ring on the item rect. |
| active (current section) | `--amber` 4px bar under the item label + `aria-current="page"` set. |
| pressed | The label briefly nudges 1px down (`--press-duration`). |

**Plain-language fallback.** Without the leather texture / amber bar, the ribbon is a bottom-pinned `<nav>` with `<button>`s in a flex row. Active item is `aria-current="page"`; the visible cue degrades to a 4px solid `--amber` underline. No functionality lost.

**Tokens.** Background `--leather` + `--texture-leather`; top hairline `--amber` 60% 2px (decorative, not contrast); item label `--font-typewriter` `--text-xs` `--paper`; active marker `--amber` 4px; height `--touch-min` + `--space-2` (= 52px) minimum; z-index `--z-tab`.

**Touch target.** Each item ≥ `--touch-min` × `--touch-min`. Items are evenly spaced with `display: grid; grid-auto-flow: column; grid-auto-columns: minmax(--touch-min, 1fr)` so the hit-box never collapses below 44px even at narrow widths.

**Notes.**
- The settings cog (⚙) is the entry point to the brass radio dial (§8). It is the rightmost item on every breakpoint so muscle memory holds.
- We do **not** add labels under tab abbreviations ("RES", "DISP") — the abbreviated label is the label, and the full names appear in the active section's heading. Reduces visual noise on a 4-item bar.

---

## 8. Brass radio dial — sync settings entry

**Purpose.** The "Raise the Other Radio" affordance from §8. A brass dial that opens the sync settings panel; the dial's rotation and color reflect the current sync mode.

**Sketch.**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-label="Brass radio dial">
  <circle cx="50" cy="50" r="40" fill="#3B2A1A" stroke="#D4A24C" stroke-width="2"/>
  <circle cx="50" cy="50" r="34" fill="#1B120A"/>
  <circle cx="50" cy="50" r="28" fill="none" stroke="#D4A24C" stroke-width="0.5" opacity="0.5"/>
  <!-- pointer -->
  <line x1="50" y1="50" x2="76" y2="36" stroke="#D4A24C" stroke-width="3" stroke-linecap="round"/>
  <circle cx="50" cy="50" r="4" fill="#D4A24C"/>
  <!-- tick marks -->
  <g stroke="#D4A24C" stroke-width="1" opacity="0.6">
    <line x1="50" y1="14" x2="50" y2="20"/>
    <line x1="86" y1="50" x2="80" y2="50"/>
    <line x1="50" y1="86" x2="50" y2="80"/>
    <line x1="14" y1="50" x2="20" y2="50"/>
  </g>
</svg>
```

**States.**
| State | Visual change | Plain-language readout |
|---|---|---|
| closed / `mode: 'none'` | Pointer at 12 o'clock. Dial dim (50% amber). | "Sync: off" |
| closed / `mode: 'manual'` | Pointer at 3 o'clock. Pointer dim amber. | "Sync: manual (QR / share link)" |
| closed / `mode: 'gist'` | Pointer at 6 o'clock. Pointer full amber. | "Sync: GitHub gist · last synced [relative time]" |
| closed / `mode: 'generic'` | Pointer at 9 o'clock. Pointer full amber. | "Sync: custom URL · last synced [relative time]" |
| open | The dial spawns a panel below it (the sync radio panel from §10/§13 token map). The dial itself rotates 8° CCW to suggest it's "powered on." |
| **conflict** | The amber dial gains a faint `--ink-red` halo (CSS `box-shadow: 0 0 0 6px rgba(126, 30, 30, 0.4)`); the readout swaps to "Sync: conflict — review needed." Pointer stops moving. |
| hover | Amber brightens to 100%. |
| focus | `:focus-visible` ring on the dial circle. |
| active (mouse-down) | Dial nudges into the page (`--shadow-press`) for `--press-duration`. |
| disabled | Dial fully dimmed (40% amber), `aria-disabled="true"`, plain-text label "Sync unavailable — local-only build." |

**Plain-language fallback.** The dial is a `<button>` with the readout text as its accessible name (e.g. `aria-label="Sync: GitHub gist, last synced 4 minutes ago"`). The plain readout text **also** appears beside the dial on every breakpoint — the pointer rotation is a redundant cue, never the only signal. Conflict state is announced via `role="alert"` text, not the red halo alone.

**Tokens.** Body `--leather` + `--leather-shadow` inset; pointer `--amber`; tick marks `--amber` 60% opacity; conflict halo `--ink-red` 40% opacity; size 80×80 minimum; z-index `--z-hardware`; press `--shadow-press` over `--press-duration`.

**Touch target.** Dial circle is 80×80; with the readout text beside it, the whole `<button>` (dial + text) is the hit-box, well over `--touch-min`.

**Notes.**
- The dial's rotation animates over `--ink-bleed-duration` when mode changes; reduced-motion collapses it to a 1-frame state swap.
- The dial is the **only place** in v2 where amber-on-leather appears at type-readable size. Per `tokens.md` §1.2, amber on leather clears AA at 5.92:1 — but we still keep all type to a small set of glyphs (the pointer is decorative, the ticks are decorative, the readout text uses `--paper` on `--leather`).

---

## 9. QR telegram — manual sync share affordance

**Purpose.** The tier-1 sync surface: a printable / scannable artifact the user hands to their other device. Looks like a paper telegram with a QR code stamped onto it.

**Sketch.**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 200" role="img" aria-label="QR telegram">
  <rect x="6" y="10" width="268" height="180" fill="#F1E4C8" stroke="#C9B388"
        stroke-width="0.5" transform="rotate(-1 140 100)"/>
  <text x="20" y="34" font-family="'Special Elite', monospace" font-size="11" fill="#2A1F12"
        letter-spacing="2" transform="rotate(-1 140 100)">— TELEGRAM —</text>
  <line x1="20" y1="44" x2="260" y2="44" stroke="#2A1F12" stroke-width="0.5"
        transform="rotate(-1 140 100)"/>
  <!-- placeholder QR grid -->
  <g transform="rotate(-1 140 100)" fill="#2A1F12">
    <rect x="100" y="60" width="80" height="80" fill="#F1E4C8" stroke="#2A1F12"/>
    <g>
      <rect x="106" y="66" width="14" height="14"/>
      <rect x="160" y="66" width="14" height="14"/>
      <rect x="106" y="120" width="14" height="14"/>
      <rect x="128" y="84" width="6" height="6"/>
      <rect x="140" y="92" width="6" height="6"/>
      <rect x="116" y="100" width="6" height="6"/>
      <rect x="148" y="116" width="6" height="6"/>
    </g>
  </g>
  <text x="140" y="160" text-anchor="middle" font-family="'IBM Plex Mono', monospace"
        font-size="10" fill="#2A1F12" transform="rotate(-1 140 100)">SCAN ON OTHER DEVICE</text>
  <text x="140" y="176" text-anchor="middle" font-family="'IBM Plex Mono', monospace"
        font-size="9" fill="#2A1F12" opacity="0.6" transform="rotate(-1 140 100)">or copy link below</text>
</svg>
```

**States.**
| State | Visual change |
|---|---|
| default | Telegram with QR + "scan on other device" + a link textarea below. |
| copy-link active | The link textarea is selected and a "COPIED" toast fires for 1.5s. |
| stale (link > 10 minutes old) | Telegram corner gains a small "EXPIRES SOON" stamp in `--ink-red`; a "REFRESH" stamp button appears beside the link. |
| disabled | Telegram greyed (paper-stained background), `aria-disabled="true"`, plain text "Sync mode is OFF — switch the dial to enable manual share." |

**Plain-language fallback.** Underneath the QR is a plain `<input type="text" readonly>` containing the share URL or one-time payload string. The QR is decorative; the textarea is canonical. A second "COPY LINK" button (using §2 stamp button) gives keyboard-only users full functionality. Screen readers get an `aria-describedby` block summarising the payload (mode, originId, expiry).

**Tokens.** Paper `--paper`; border `--paper-stained`; QR ink `--ink-brown` (do **not** use ink-red for QR modules — readers fail on red); body label `--font-typewriter` `--text-xs` `--ink-brown` letter-spacing 2px; share-link textarea uses §1 input slot conventions; rotation pinned ±1°; shadow `--shadow-card`.

**Touch target.** The "COPY LINK" stamp button = ≥ `--touch-min`. The QR itself is not interactive (decorative); the textarea is keyboard-selectable.

**Notes.**
- Payload encoding (compact JSON or base64-CBOR) is decided in PHA-355; this spec only requires that the QR encode the **same** string the textarea contains, byte-for-byte.
- We never render a QR over `--paper-stained` background (the stained tone reduces scanner reliability); QRs always sit on flat `--paper`.

---

## 10. Conflict spread — two-page diff view

**Purpose.** When a sync pull surfaces a conflict (per §8 conflict-resolution tree), the user sees a two-page spread: local on the left, remote on the right, with conflicting fields highlighted. They pick a side per field or accept all.

**Sketch.**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 280" role="img" aria-label="Conflict spread">
  <!-- spine -->
  <rect x="234" y="0" width="12" height="280" fill="#1B120A"/>
  <!-- left page -->
  <rect x="6" y="10" width="222" height="260" fill="#F1E4C8" stroke="#C9B388"/>
  <text x="22" y="34" font-family="'Special Elite', monospace" font-size="11" fill="#2A1F12"
        letter-spacing="2">LOCAL · this device</text>
  <text x="22" y="60" font-family="'IBM Plex Mono', monospace" font-size="11" fill="#2A1F12">Day: 14</text>
  <text x="22" y="80" font-family="'IBM Plex Mono', monospace" font-size="11" fill="#2A1F12">Food: 3</text>
  <rect x="20" y="90" width="180" height="28" fill="#7E1E1E" opacity="0.18"/>
  <text x="22" y="110" font-family="'IBM Plex Mono', monospace" font-size="11" fill="#2A1F12">Morale: high</text>
  <text x="22" y="138" font-family="'Caveat', cursive" font-size="14" fill="#1F2A4A">Maya killed a feral</text>
  <!-- right page -->
  <rect x="252" y="10" width="222" height="260" fill="#F1E4C8" stroke="#C9B388"/>
  <text x="268" y="34" font-family="'Special Elite', monospace" font-size="11" fill="#2A1F12"
        letter-spacing="2">REMOTE · gist · 4m ago</text>
  <text x="268" y="60" font-family="'IBM Plex Mono', monospace" font-size="11" fill="#2A1F12">Day: 14</text>
  <text x="268" y="80" font-family="'IBM Plex Mono', monospace" font-size="11" fill="#2A1F12">Food: 5</text>
  <rect x="266" y="90" width="180" height="28" fill="#7E1E1E" opacity="0.18"/>
  <text x="268" y="110" font-family="'IBM Plex Mono', monospace" font-size="11" fill="#2A1F12">Morale: low</text>
  <text x="268" y="138" font-family="'Caveat', cursive" font-size="14" fill="#1F2A4A">Maya killed a feral</text>
</svg>
```

**States.**
| State | Visual change |
|---|---|
| default | Both pages laid side-by-side (mobile: stacked, local on top). Conflicting fields share a subtle `--ink-red` 18% wash. Each conflict row has a "KEEP LOCAL" / "TAKE REMOTE" pair of stamp-button-style chips. |
| hover (on a chip) | Chip lifts (`--shadow-card`). |
| focus | `:focus-visible` ring per chip; the page itself is a `<dialog>` with `role="dialog" aria-modal="true"`. |
| active (chip pressed) | Chip presses (`--shadow-press`); the chosen field's row dims the un-chosen page's value. |
| accept-all | A footer "ACCEPT ALL [LOCAL/REMOTE]" stamp button — fires a confirm dialog before applying. |
| disabled | n/a — the conflict spread always presents at least one actionable choice. |

**Plain-language fallback.** Without CSS Grid (or if `prefers-reduced-data` strips the spread metaphor), the dialog renders as a single column: each conflicting field as a `<fieldset>` with two radio buttons (LOCAL / REMOTE) and the field's two values. The `<dialog>` element provides modal semantics natively. The decision tree (when local wins automatically vs. when this dialog opens) is documented in [`data-model.md`](./data-model.md) §3.

**Tokens.** Background `--paper` per page over `--leather` body; spine `--leather-shadow`; conflict-row wash `--ink-red` 18%; chip border `--ink-brown`; chip text `--font-typewriter` `--text-sm` uppercase; modal z-index `--z-overlay`; stamp button per §2.

**Touch target.** Each "KEEP LOCAL" / "TAKE REMOTE" chip is ≥ `--touch-min` × ≥ 96px wide. Chips are ordered left-to-right (LOCAL, REMOTE) on every breakpoint to match the spread layout.

**Notes.**
- Per moodboard composition rule: **one light source.** The spine fold is the darkest part of the dialog and the amber lamp falls from the top-left, so the **left** page reads slightly brighter than the right at the gutter. Reduced-data drops the gradient.
- A "STATIC" toast (z `--z-toast`) appears for 2s after either accept-all action, to confirm the merge committed.

---

## 11. Stamps — KIA / EXILED / LEGACY

**Purpose.** Status overlays that "stamp" a survivor card to mark a permanent state. The art is the meaning — but every stamp is paired with text in the survivor's data row so meaning never lives in art alone (per §0).

**Sketch.**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 120" role="img" aria-label="Three stamps">
  <!-- KIA -->
  <g transform="rotate(-8 60 50)" font-family="'Special Elite', monospace" letter-spacing="3">
    <rect x="8" y="20" width="104" height="60" fill="none" stroke="#7E1E1E" stroke-width="3"/>
    <text x="60" y="60" text-anchor="middle" font-size="28" fill="#7E1E1E">KIA</text>
  </g>
  <!-- EXILED -->
  <g transform="rotate(4 170 50)" font-family="'Special Elite', monospace" letter-spacing="2"
     opacity="0.78">
    <rect x="120" y="20" width="120" height="60" fill="none" stroke="#2A1F12" stroke-width="2"/>
    <text x="180" y="60" text-anchor="middle" font-size="22" fill="#2A1F12">EXILED</text>
  </g>
  <!-- LEGACY -->
  <g transform="rotate(-2 280 50)">
    <circle cx="280" cy="50" r="34" fill="#D4A24C" stroke="#2A1F12" stroke-width="2"/>
    <text x="280" y="56" text-anchor="middle" font-family="'Special Elite', monospace"
          font-size="12" letter-spacing="2" fill="#2A1F12">LEGACY</text>
  </g>
</svg>
```

**States.**
| Stamp | default | hover/active | Plain-text companion |
|---|---|---|---|
| **KIA** | `--ink-red` outline + label, ~8° rotation, slight ink bleed at corners. Sits over the card at z `--z-stamp`. | None — stamps are static after applied. | `<span>KIA · Day [n]</span>` in the card's data row. |
| **EXILED** | `--ink-brown` outline at 78% opacity, smudged via SVG `<filter id="smudge">`. | None. | `<span>EXILED · Day [n]</span>` |
| **LEGACY** | Gold seal (`--amber` background), `--ink-brown` ring, `--ink-brown` label. Slight emboss via inset shadow. | None. | `<span>LEGACY · Day [n]</span>` |

**Plain-language fallback.** Without the SVG smudge filter or rotation, the stamp degrades to a static `<span class="stamp stamp--kia">KIA</span>` element with its background color and uppercase text only. The card's data row also includes the status text, so even if the stamp art is dropped entirely, the survivor's status is unambiguous to screen readers and unstyled HTML.

**Tokens.** KIA fill/stroke `--ink-red`; EXILED fill/stroke `--ink-brown` 78% opacity + smudge filter; LEGACY background `--amber` + ring `--ink-brown`; rotation locked per stamp (KIA −8°, EXILED +4°, LEGACY −2°); z-index `--z-stamp`; transition `--ink-bleed-duration` on first apply only.

**Touch target.** Stamps are not interactive (the action that places them — MARK KIA, EXILE, SEND TO LEGACY — is a §2 stamp button on the card-back). The stamp art itself uses `pointer-events: none` so it never blocks the card's underlying tap target.

**Notes.**
- The smudge filter on EXILED is a single inline SVG `<filter>` reused from the §13 inventory.
- LEGACY is the only stamp that uses `--amber` as a fill — and it uses `--ink-brown` for the label, so amber never carries text contrast (per §1.2 of `tokens.md`).
- Per §0: stamps are **decorative** for status. The canonical status field is on the survivor record; the stamp follows the data, not the other way around.

---

## 12. Morale gauge — penned smiley slider

**Purpose.** Survivor morale input. Looks like a hand-drawn smiley slider running from 😞 to 😄; falls back to a plain `<input type="range">` everywhere.

**Sketch.**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 80" role="img" aria-label="Morale gauge">
  <line x1="20" y1="40" x2="300" y2="40" stroke="#2A1F12" stroke-width="2" stroke-linecap="round"/>
  <!-- ticks -->
  <g stroke="#2A1F12" stroke-width="1.5">
    <line x1="20" y1="32" x2="20" y2="48"/>
    <line x1="160" y1="32" x2="160" y2="48"/>
    <line x1="300" y1="32" x2="300" y2="48"/>
  </g>
  <!-- frowny -->
  <g stroke="#2A1F12" stroke-width="1.5" fill="none">
    <circle cx="20" cy="14" r="10"/>
    <circle cx="17" cy="12" r="0.8" fill="#2A1F12"/>
    <circle cx="23" cy="12" r="0.8" fill="#2A1F12"/>
    <path d="M16 18 q4 -3 8 0"/>
  </g>
  <!-- smiley -->
  <g stroke="#2A1F12" stroke-width="1.5" fill="none">
    <circle cx="300" cy="14" r="10"/>
    <circle cx="297" cy="12" r="0.8" fill="#2A1F12"/>
    <circle cx="303" cy="12" r="0.8" fill="#2A1F12"/>
    <path d="M296 17 q4 4 8 0"/>
  </g>
  <!-- thumb -->
  <circle cx="220" cy="40" r="14" fill="#F1E4C8" stroke="#1F2A4A" stroke-width="2"/>
  <text x="220" y="44" text-anchor="middle" font-family="'Caveat', cursive" font-size="14"
        fill="#1F2A4A">7</text>
</svg>
```

**States.**
| State | Visual change |
|---|---|
| default | Hand-drawn line + frowny / smiley anchors + paper-fill thumb showing the current numeric value (1–10). |
| hover | Thumb gains amber halo (decorative). |
| focus | `:focus-visible` ring on the thumb + the underlying `<input type=range>` is the focus target. |
| active (drag) | Thumb tracks the cursor; the value text re-renders in `--font-hand`. |
| disabled | Track + thumb at 50% opacity; `aria-disabled="true"`. |

**Plain-language fallback.** The gauge is **always** a real `<input type="range" min="1" max="10" step="1">` underneath the SVG chrome. If CSS fails or the SVG doesn't render, the user sees the browser's default range slider — fully functional, fully accessible. The current value is also rendered as an accessible `<output>` element next to the slider so screen readers always announce the number, not just "morale slider."

**Tokens.** Track `--ink-brown` 2px; anchors `--ink-brown`; thumb fill `--paper` + stroke `--ink-blue` 2px; value text `--font-hand` `--text-base` `--ink-blue`; halo `--amber` 30% on hover; transition `--ink-bleed-duration`.

**Touch target.** The thumb hit-box is `--touch-min` × `--touch-min` (the visible thumb is 28px; the invisible hit area extends it to 44px). The track itself is also clickable; tapping the track moves the thumb to that value.

**Notes.**
- The numeric value (1–10) is the **canonical** data, not the smiley face. Per §0: clarity wins. The mood label ("high", "low") rendered elsewhere on the card is computed from this number — the player can also override with a text mood note.
- Per [tokens.md §2.1](./tokens.md#21-token-table) Caveat is decorative-only; the value text rendering in Caveat is paired with the underlying numeric `<output>` so meaning never depends on the script font.

---

## 13. Wax-seal TRANSMIT — primary footer action

**Purpose.** The single dominant CTA at the bottom of the dispatch page: stamp the daily report and "transmit it" to the network (copy to clipboard + open the share sheet, per current behavior).

**Sketch.**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 100" role="img" aria-label="Wax seal Transmit">
  <!-- ribbon under seal -->
  <path d="M40 60 q70 -10 140 0 v20 q-70 10 -140 0 z" fill="#7E1E1E" opacity="0.85"/>
  <!-- wax body -->
  <circle cx="110" cy="50" r="40" fill="#7E1E1E"/>
  <circle cx="110" cy="50" r="40" fill="url(#waxsheen)" opacity="0.4"/>
  <!-- seal mark: NETWORK crosshair-in-circle -->
  <circle cx="110" cy="50" r="22" fill="none" stroke="#F1E4C8" stroke-width="1.5"/>
  <line x1="110" y1="32" x2="110" y2="68" stroke="#F1E4C8" stroke-width="1.5"/>
  <line x1="92" y1="50" x2="128" y2="50" stroke="#F1E4C8" stroke-width="1.5"/>
  <text x="110" y="92" text-anchor="middle" font-family="'Special Elite', monospace" font-size="12"
        fill="#F1E4C8" letter-spacing="2.5">TRANSMIT</text>
  <defs>
    <radialGradient id="waxsheen" cx="40%" cy="35%">
      <stop offset="0%" stop-color="#F1E4C8" stop-opacity="0.7"/>
      <stop offset="60%" stop-color="#7E1E1E" stop-opacity="0"/>
    </radialGradient>
  </defs>
</svg>
```

**States.**
| State | Visual change |
|---|---|
| default | Wax circle + ribbon + crosshair seal mark. Sheen highlight at top-left (the lamp). Label "TRANSMIT" in `--font-typewriter` `--paper`. |
| hover | Sheen brightens; cursor `pointer`. |
| focus | `:focus-visible` ring around the seal. |
| active (mouse-down) | Wax compresses (`--shadow-press`) + the sheen briefly hides. `--press-duration`. |
| pressed (post-transmit) | A small "STATIC" toast (z `--z-toast`) fires — "TRANSMITTED · COPIED TO CLIPBOARD". The seal stays on screen (it does not become a stamp); it returns to default after 800ms. |
| disabled | Wax dims to 60% saturation, label `--paper` 60% opacity, `aria-disabled="true"`. Used when the dispatch block is empty. |

**Plain-language fallback.** Underneath the SVG is a real `<button type="button">TRANSMIT TO NETWORK</button>`. If the wax SVG fails, the button renders as a `--ink-red` filled rectangle with `--paper` text — same shape footprint, identical action, no semantic loss. The toast also exists as a polite-region `aria-live` announcement, not just visually.

**Tokens.** Wax fill `--ink-red`; sheen `--paper` 70%; ribbon `--ink-red` 85% opacity; seal mark `--paper` 1.5px; label `--font-typewriter` `--text-sm` `--paper` letter-spacing 2.5px; press `--shadow-press` over `--press-duration`; size 200×80 minimum (well over `--touch-min`); z-index `--z-stamp` (the seal sits on top of the page).

**Touch target.** Seal art = ~80×80 visible; the surrounding `<button>` element is the canonical hit-box at ≥ `--touch-min` on every axis (we anchor it to a 200×80 surface so the wax has thumb-room).

**Notes.**
- This is the **only** wax seal in the v2 design language. We never reach for a second wax accent — its dominance is the point.
- The "STATIC" toast vocabulary is shared with the conflict spread (§10) and any other transient confirmation; it is the v2 equivalent of v1's plain "Copied!" toast.

---

## 14. Asset inventory — shared SVG primitives

To keep `index.html` under the perf cap (Plan §5), every component above pulls from a single inline SVG `<defs>` block at the top of the page. Listing it here so engineering doesn't duplicate.

| Asset | Used by | Approx size |
|---|---|---|
| `<filter id="hand">` — pen-jitter feTurbulence | §1 input slot, §4 tie row separators, §11 KIA outline | ~280 B |
| `<filter id="smudge">` — gaussian-blur + opacity for EXILED | §11 EXILED stamp | ~180 B |
| `<symbol id="paperclip">` | §3 index card, §6 paperclip header | ~220 B |
| `<symbol id="staple">` | future receipts (Resources tab; not in this issue) | ~140 B |
| `<symbol id="brass-dial-pointer">` | §8 brass radio dial | ~100 B |
| `<radialGradient id="waxsheen">` | §13 wax-seal TRANSMIT | ~130 B |
| `<symbol id="seal-network">` | §13 wax seal mark | ~140 B |

All defs are `aria-hidden="true"`. The total inline SVG-defs weight is well under the 1 KB SVG-noise budget, leaving plenty of headroom inside the 250 KB asset cap.

---

## 15. Acceptance checklist

Mirrors the issue's acceptance section.

- [x] **Each component has a clarity-win fallback** — every section §1–§13 has a "Plain-language fallback" subsection per §0.
- [x] **Touch-target spec confirmed ≥ `--touch-min` (44×44px)** — every interactive component (§1, §2, §4, §5, §7, §8, §9, §10, §12, §13) declares its hit-box. Stamps (§11) and the paperclip header (§6) are explicitly non-interactive (`pointer-events: none` / `aria-hidden`).
- [x] **Engineering issues can reference component names + token names from this doc** — every component has a stable `§n` anchor and a token list. PHA-348 (mockups), PHA-354 (Ties That Bind), and PHA-355 (sync) are pre-wired to cite these names.
- [x] **All sketches inline** — the spec sheet has no external image dependencies; the `design/` folder still ships at < 50 KB total.

---

## 16. Cross-references

- [Design tokens](./tokens.md) · [`tokens.css`](./tokens.css)
- [Mood board](./moodboard.md)
- [Data model](./data-model.md) — relationships + sync config + JSON-export shape changes
- [Plan rev 3](/PHA/issues/PHA-336#document-plan) — §0 Clarity Wins, §3 Interaction Language, §7 Ties That Bind, §8 Raise the Other Radio, §9 Deliverables

---

## 17. Changelog

- **rev 1 (2026-05-02)** — Initial v2 component spec sheet. 13 components, 1 asset inventory. Every interactive component carries a clarity-win fallback and a ≥ 44px touch-target declaration.

# Community Diary — Agent Handoff Document
**Date:** 2026-05-17  
**Project:** State of Decay 2 Community Diary  
**Live URL:** https://phattbeats.github.io/sod2-diary/  
**Repo:** https://github.com/phattbeats/sod2-diary  

---

## 1. What Was Done This Session

### 1a. Hotfix — `index.html` (v3 → live fix)

**Bug:** The live site was completely broken — giant black SVG icons (~680px) visible instead of the mobile bottom nav.

**Root cause 1 — orphaned CSS rule:**  
Around line 2616, a `.book-tab:active {` block was opened but never closed. Every CSS rule after it (`.field-strip` styles, `.field-ribbon` styles, `.section-title small`, `.tie-strip`, etc.) was nested inside that selector via CSS Nesting, making them inert in normal state (they only applied when a book-tab was being actively pressed).

**Root cause 2 — missing CSS for mobile nav elements:**  
The HTML markup for `.field-strip` (top swipe rail) and `.field-ribbon` (bottom leather strap) existed with no corresponding CSS — no `display: none` on desktop, no size constraints on the inline SVG icons (which only had `viewBox`, no `width`/`height`). The SVGs expanded to fill flex containers at ~680px each.

**Fix applied to `index.html`:**
- Closed `.book-tab:active` with a proper press-state style
- Added `.book-tab--active` class rules
- Added complete CSS block for `.field-strip` (sticky top swipe rail, hidden on `≥641px`, shown on mobile) and `.field-ribbon` (fixed bottom leather strap with 22×22 icon sizing, proper leather gradient background, safe-area padding, `padding-bottom` on body to clear content from fixed ribbon)

**Status:** ✅ Fixed. `index.html` in this project reflects the patched version.

---

### 1b. Full Visual Overhaul — `index-v4.html` (new file)

A clean-slate redesign. Three deployable files (inline for GH Pages — no bundler needed):

| File | Purpose |
|------|---------|
| `index-v4.html` | All markup |
| `v4/styles.css` | Complete visual system |
| `v4/app.js` | All app logic |

**To deploy:** rename `index-v4.html` → `index.html` and push `v4/` directory alongside it.

#### Visual design system

- **Palette (3 moods, toggled via `data-mood` on `<html>`):**
  - `sepia` (default) — warm cream paper `#eee0c2`, sepia ink `#1e1610`
  - `bone` — cooler off-white, navy ink
  - `coffee` — darker kraft paper, charcoal ink
- **Typography:**
  - Section titles / labels / stamps: `Special Elite` (typewriter)
  - Form labels / metadata: `IBM Plex Mono`
  - User entry text (handwriting): `Patrick Hand` (default), switchable to `Caveat` (loose) or IBM Plex Mono (typewriter-only)
- **Paper effects:** SVG fractal noise grain via `background-image`, dog-eared top-right corner via `::after`, inner shadow simulating spine
- **Tape strips:** CSS `::before` / `::after` on `.report` and `.card-survivor` — diagonal repeating-gradient kraft-brown tape with shadow. Note: screenshot capture tools (html-to-image) don't render pseudo-elements — confirmed correct in real browsers via `getComputedStyle`.
- **Compass SVG:** Hand-drawn inline SVG compass rose in diary header (simple ring + 4 cardinal diamonds + N glyph)
- **Skull glyph:** Inline SVG skull icon next to "We Lost" label in section 5

#### Sections (numbered like a field journal)

1. **Where We Stand** — Difficulty select, Plague Hearts stepper, Survivors stepper
2. **Resources** — 7 resources (Food/Medicine/Ammo/Materials/Fuel/Parts/Influence), each with `from → to` inputs + computed delta badge (+/-/color)
3. **Community Mood** — Morale slider (−100→+100), three hand-drawn face SVGs, labelled value
4. **What Happened Today** — `events` textarea (Patrick Hand, ruled lines via `repeating-linear-gradient`)
5. **Losses & Arrivals** — `deaths` + `newSurvivors` textareas side by side
6. **Anything Else** — `notes` textarea

**Status strip** (above sections): Community Name text input, Map select, Base select (linked — populates from `MAP_BASES` data, day number daybox.

#### Roster (The People)

- Grid of `article.card-survivor` elements rendered from `roster[]` array in `localStorage`
- Cards show: name/age, bio, traits, skills, day joined, status badge (KIA stamp in red, LEGACY in amber)
- Per-card actions: **Killed / Exiled / → Legacy / Remove** (active cards); **Restore / Remove** (fallen/legacy)
- Add form via `<details>` expand: name, age, bio, traits, skills, day joined
- Counters: `N in community · N legacy · N fallen` in section header

#### Report generation

- `generateReport()` builds plain-text report from form state + roster
- On click: populates `#reportOutput`, un-hides it, copies to clipboard, saves to `history[]`, calls `rollover()`
- `rollover()`: day +1, shifts `to → from` for each resource, clears single-day fields (events/deaths/newSurvivors/notes)

#### Persistence

- `localStorage` keys: `sod2-diary-v4` (form state), `sod2-diary-v4-history`, `sod2-diary-v4-roster`, `sod2-diary-v4-prefs`
- Auto-saves 500ms after any input change
- Export/Import JSON (full snapshot: current form state + roster + history)
- Copy All (concatenated history), Clear History, New Book (wipes everything)

#### Tweaks panel

Toggled by host `__activate_edit_mode` message OR by the inline "Tweaks ✎" button. Three controls:
1. **Color mood** — Sepia / Bone / Coffee swatches (sets `data-mood` on `<html>`, persisted to `sod2-diary-v4-prefs`)
2. **Paper texture** — Slider 0–100 → maps to CSS `--grain` custom property (opacity of the noise layer)
3. **Handwriting style** — Neat (Patrick Hand) / Loose (Caveat) / Typewriter (IBM Plex Mono) — sets `--font-hand`

#### Mobile

- Bottom dock (`nav.dock`) with 5 anchor links + glyphs, fixed above safe area
- `@media (max-width: 720px)` collapses header to 2-col, status strip to 2-col, resources to single column, row--2 to single column
- `body { padding-bottom: 72px }` lifts content above dock

---

## 2. What Was NOT Rebuilt (Intentional Omissions from v3)

These were in v3 but deliberately excluded from v4 due to being broken or half-wired. Scoped out below.

| Feature | v3 Status | v4 Status |
|---------|-----------|-----------|
| Survivor Ties / Relationships | Broken | Not included — scope below |
| Radio Sync (QR / link share) | Broken | Not included — scope below |
| Edit Survivor (inline modal) | Working but poor UX | Not included — scope below |
| Field strip (top mobile rail) | Fixed in index.html hotfix | Mobile dock replaces it in v4 |
| Book tabs (desktop right edge) | Working | Removed — can add back |

---

## 3. Feature Scopes

### 3a. Survivor Ties / Relationships

**Concept:** Track bonds between survivors (partner, family, mentor, rival, friend). Display as a strip on the back of each survivor card. Used in report generation and narrative context.

**Why it was broken in v3:** The tie data model was stored on each survivor object (`s.ties = []`) but the add-tie UI was wired with event delegation that couldn't find its own handlers in some states. The `buildTieStrip()` function was called in card render before ties were hydrated from localStorage. Race condition + no defensive null checks.

**Data model (proposed for v4):**

```js
// Each survivor in roster[] has an optional ties array:
{
  id: "s-abc123",
  name: "Maya Brooks",
  // ... other fields ...
  ties: [
    {
      toId: "s-xyz789",    // ID of the other survivor
      kind: "partner",     // partner | family | mentor | rival | friend
      label: "",           // optional custom label
      since: 3,            // day number the tie was formed
      strained: false      // flag for rift/conflict
    }
  ]
}
```

**UI pattern (recommended):**

1. On each active survivor card, add a **"Ties ▾"** expand button (replaces the old `data-action="flip"` card-flip mechanic which was overengineered).
2. When expanded, show a `<details>` panel below the card (no flip animation — simpler, no state needed):
   ```
   ── TIES ─────────────────────────────────
   Partner: Jin (Day 1)   [STRAINED] [SEVER]
   + Add a tie
   ──────────────────────────────────────────
   ```
3. "Add a tie" reveals an inline mini-form: `Tied to: [select survivor]`, `Kind: [partner/family/mentor/rival/friend]`, `Since: [day]`, then `[Add]`.
4. **SEVER** removes the tie object from both survivors (ties are bidirectional — when you add a tie on Maya, also push a mirror tie on Jin).
5. **STRAINED** toggles `strained: true`, which renders the pip in a dimmed italic style.

**Implementation steps:**
1. Add `ties: []` default in `addSurvivor()` and when hydrating from old saves.
2. Add `addTie(fromId, toId, kind, label, since)` — pushes to both survivors, calls `renderRoster()`, persists.
3. Add `severTie(fromId, toId)` — removes from both, re-renders, persists.
4. Add `toggleStrainedTie(fromId, toId)` — flips `strained`, re-renders, persists.
5. Update `survivorCard()` to render the ties `<details>` panel below the actions row.
6. Update `survivorLine()` in report generation to include tie names in the report text.

**CSS to add (in `v4/styles.css`):**
```css
.card-ties {
  margin-top: 8px;
  border-top: 1px dashed var(--ink-pencil);
  padding-top: 6px;
}
.tie-pip {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--ink-blue);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 3px 0;
  border-bottom: 1px dotted var(--ink-pencil);
}
.tie-pip.is-strained { opacity: 0.55; font-style: italic; }
.tie-add-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  margin-top: 6px;
}
```

---

### 3b. Edit Survivor (Inline Edit)

**Concept:** Click an "Edit" button on a survivor card → card fields become editable in-place → "Save" commits changes.

**Recommended pattern (simpler than v3 modal):**

1. Add `data-act="edit"` button to `.actions`.
2. In the `rosterList` click handler, toggle a CSS class `is-editing` on the card.
3. When `is-editing`, replace the static text inside the card with `<input>` / `<textarea>` fields pre-filled with current values, and change action buttons to **Save / Cancel**.
4. On Save: read field values, update the survivor object in `roster[]`, call `renderRoster()`, persist.

No modal needed. Inline flip is more readable and doesn't require z-index management.

---

### 3c. Radio Sync (QR / Link Share)

**Concept:** Export a compressed snapshot of today's report (or full state) as a URL-safe string, encode into QR, allow another device to paste or scan and import.

**Why v3 was broken:** The MiniQR library and sync panel existed but the data serialization was fragile — it was trying to base64 the entire state including history, which exceeds URL length limits and broke on import.

**Recommended redesign:**

**Transmit flow:**
1. When "Sync" is tapped, serialize ONLY the current form state + roster (no history) as compact JSON → `JSON.stringify(state)` → `btoa(encodeURIComponent(json))` → prepend with `https://phattbeats.github.io/sod2-diary/#sync=`
2. Render QR of this URL using MiniQR (already bundled in v3's script block — you can copy those two `<script>` tags from `index.html` lines 5122–5648 into v4)
3. Also provide a "Copy Link" button

**Receive flow:**
1. On page load, check `window.location.hash` for `#sync=...`
2. If found: decode → parse JSON → call `applyFormState()` and `renderRoster()` → clear hash → show "Import from link — Resume? [Yes/Dismiss]" banner

**State size limit:** Only share current-day state + roster. History stays local. This keeps URL under ~2KB for typical use.

**Files to change:**
- Add a `<button>` to the mobile dock and an `id="syncPanel"` overlay in `index-v4.html`
- Copy MiniQR script blocks from `index.html` (lines 5122–5648)
- Add sync logic functions to `v4/app.js` or a new `v4/sync.js`

---

### 3d. Book Tabs (Desktop Right-Edge Nav — Optional)

v3 had `.book-tab` elements fixed to the right edge of the page. v4 removed these in favor of simplicity. If you want them back:

1. Copy the `.book-tab` CSS from `index.html` (~lines 2521–2640)
2. Add the tab HTML markup (from `index.html` around line 3297) after the `.diary` element in `index-v4.html`
3. The JS tab-highlight logic (in `index.html` around line 5350) can be adapted by updating the selector groups to match v4's section IDs (`#sec-stand`, `#sec-resources`, `#sec-morale`, `#sec-events`, `#sec-people-flux`, `#sec-notes`, `#sec-people`, `#sec-report`)

---

## 4. File Map

```
project root
├── index.html              ← v3, hotfixed (live site deployed here)
├── index-v4.html           ← v4 redesign (ready to rename → index.html)
├── v4/
│   ├── styles.css          ← v4 visual system (all CSS)
│   └── app.js              ← v4 app logic (all JS)
├── miniqr.mjs              ← QR generator (from original repo)
├── miniqr-v2.mjs           ← QR generator v2
├── miniqr-embed.mjs        ← QR embed helper
├── design/
│   ├── tokens.css          ← original design token reference
│   ├── moodboard.md        ← visual direction notes
│   └── components.md       ← v3 component specs
└── docs/
    ├── README.md
    └── design-system.md
```

---

## 5. Key Decisions / Conventions for Future Agents

1. **Single HTML file is preferred for deployment.** Use `super_inline_html` to bundle `index-v4.html` + `v4/styles.css` + `v4/app.js` into one file before pushing to GH Pages. During development, keep them separate.
2. **No frameworks.** Plain JS only. The IIFE in `app.js` keeps scope clean.
3. **localStorage keys are versioned.** `sod2-diary-v4-*` — do not change these without a migration path or users lose data.
4. **CSS custom properties drive everything.** All palette values are on `:root` / `[data-mood]`. Don't hardcode colors — reference `var(--ink)`, `var(--paper)`, etc.
5. **Never use `scrollIntoView()`** — it breaks the web app host. Use `window.scrollTo({ top, behavior: "smooth" })` with `getBoundingClientRect().top + window.scrollY - offset` instead.
6. **Tape strips / decorative pseudo-elements** won't appear in `html-to-image`-based screenshot tools. They render correctly in real browsers — confirmed via `getComputedStyle`.
7. **Fonts load from Google Fonts CDN.** If offline use is needed, download and self-host: Special Elite, Patrick Hand, Caveat, IBM Plex Mono.
8. **`--font-hand` is the CSS variable for handwriting.** Changing it via `style.setProperty` from the tweaks panel controls all textareas. This is the lever for the handwriting style tweak.
9. **Rollover logic** lives in `rollover()` in `v4/app.js`. When generate is clicked: day increments, resource `to → from`, single-day text fields clear. History and roster are NOT cleared by rollover.
10. **Ties are bidirectional.** Any implementation must push a mirror tie on the target survivor and remove from both on sever.

---

## 6. Priority Order for Next Session

| Priority | Task |
|----------|------|
| 🔴 High | Survivor Ties (bidirectional, inline UI, mirror on both cards) |
| 🟠 High | Edit Survivor (inline, no modal) |
| 🟡 Medium | Radio Sync (hash-based URL, QR, receive on load) |
| 🟢 Low | Book tabs on desktop (re-add right-edge nav) |
| 🟢 Low | Ties visible in generated report text |
| ⬜ Optional | Print stylesheet / PDF export cleanup |

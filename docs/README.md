# SoD2 Diary — Project Docs

This folder is the **public-facing source of truth** for the diary's design philosophy, design system, and visual identity. If a question about look, feel, or vocabulary comes up, the answer lives here first — implementation files in `/index.html` and `/design/` follow what is documented here.

> _"Everyone's experiences matter. By sharing what we see and do, we build the knowledge that keeps us all alive."_

---

## Quick links

| What | Where | Notes |
|---|---|---|
| **Live preview (v2 tokens)** | https://phattbeats.github.io/sod2-diary/design/preview.html | One static page that renders every v2 token. Eyeball this before you touch any CSS. |
| **Live app (v1 today)** | https://phattbeats.github.io/sod2-diary/ | What the diary looks like in production right now. v2 is in flight. |
| **Design philosophy (Plan rev 3)** | [`/PHA/issues/PHA-336`](/PHA/issues/PHA-336#document-plan) | The "why" behind v2 — clarity-wins tiebreaker, leather/paper/ink metaphor, relationships, sync. |
| **Design system reference** | [`design-system.md`](./design-system.md) | Compact reference: palette, type, motion, spacing, with a11y rules. Mirror of `/design/tokens.md` for public reading. |
| **Mood board** | [`../design/moodboard.md`](../design/moodboard.md) | Five reference surfaces (leather, paper, ink, hardware, lamp) with annotations. |
| **Tokens (markdown spec)** | [`../design/tokens.md`](../design/tokens.md) | Full rationale + WCAG-AA contrast proofs. |
| **Tokens (CSS)** | [`../design/tokens.css`](../design/tokens.css) | The custom-property file every component imports. |
| **Screenshots** | [`screenshots/`](./screenshots/) | Auto-generated from the live preview on every push (see workflow below). |
| **Original concept art** | [`concept-art/`](./concept-art/) | Source images that inspired the v2 metaphor. Drop new art here. |

---

## What v2 is, in one paragraph

The diary turns from a dark neon utility into an **in-universe field journal a survivor would actually carry**. Every screen is a worn leather logbook, lit by a desk lamp, kept alive with paperclips and ink. The UI never lies about being a UI — but it dresses itself as something the player's character would recognize. The tiebreaker, codified as Plan §0: when in-universe styling and clarity collide, **clarity wins**.

The full philosophy lives on [PHA-336 Plan rev 3](/PHA/issues/PHA-336#document-plan); the visual vocabulary it locks lives at [`design/tokens.css`](../design/tokens.css).

---

## How to use this folder

- **Reading the design** → start with [`design-system.md`](./design-system.md), then jump to the live preview.
- **Implementing a component** → `import` `/design/tokens.css`, cite token names (never raw hex), check the contrast table before pairing colors. Issue PHA-347 captures the component spec; PHA-349 wired tokens into the live `index.html`.
- **Updating the design** → edit `/design/tokens.css` and `/design/tokens.md` together. The screenshots in [`screenshots/`](./screenshots/) regenerate automatically from the live preview on the next push to `main`.
- **Adding concept art** → drop the file in [`concept-art/`](./concept-art/) and append a row to its README so attribution stays straight.

---

## How screenshots stay current

Screenshots in [`screenshots/`](./screenshots/) are not hand-captured. The workflow at [`.github/workflows/screenshots.yml`](../.github/workflows/screenshots.yml) runs on every push to `main` (and on `workflow_dispatch`):

1. Spin up an Ubuntu runner with Chromium + system fonts.
2. Wait until GitHub Pages has redeployed `design/preview.html` from the same commit.
3. Run [`scripts/capture-screenshots.js`](../scripts/capture-screenshots.js) at three viewports (desktop wide, desktop hero, mobile).
4. Commit the resulting PNGs back to `main` under `docs/screenshots/` if they changed.

This means the screenshots in this folder are always within ~1–2 minutes of the live preview. If you ever see them drift, push an empty commit (or trigger the workflow from the Actions tab) and they will refresh.

---

## Design tiebreakers, locked

These rules override anything in implementation if there's a conflict. They came out of [Plan §0 / §6](/PHA/issues/PHA-336#document-plan) and the contrast work in [`tokens.md` §1.2](../design/tokens.md#12-wcag-aa-contrast-results-all-ink-on-paper-combinations).

1. **Clarity wins.** Real `<input>`/`<label>`/`<button>` under every painted control. No canvas-faked fields.
2. **`--amber` is decorative-only on paper.** Fails AA at 1.84:1. Used as glow / focus ring / underline. If amber must carry a label, the label sits on `--leather` (clears 5.92:1).
3. **Handwriting (`--ink-blue`, font `--font-hand`) is decorative.** AA-safe but never the sole carrier of meaning — always pair with a typewriter sub-label.
4. **`--ink-red` is reserved for life/death + alert state.** KIA, plague hearts, sync errors. Not a generic accent.
5. **Animation budget ≤ 200ms per interaction.** `--ink-bleed-duration: 180ms`, `--press-duration: 90ms`. Reduced-motion zeroes both.
6. **Touch targets ≥ 44×44px (`--touch-min`).** If the art is smaller, the hit-box is invisible-padded.
7. **Generated dispatch block stays plain mono.** Must paste into chat with zero stylistic baggage.
8. **Single `index.html`, ≤ 250 KB total declared assets.** Asset budget verified at ~191 KB ([`tokens.md` §2.4](../design/tokens.md#24-latin-subset-perf-budget--confirmed-under-cap)).

---

## Issue trail

| Issue | What |
|---|---|
| [PHA-336](/PHA/issues/PHA-336) | Design philosophy v2 (parent / plan document). |
| [PHA-346](/PHA/issues/PHA-346) | This deliverable — mood board + design tokens + live preview + this docs folder. |
| [PHA-347](/PHA/issues/PHA-347) | Component spec sheet + relationships / sync data-model spec. Picks up the token vocabulary. |
| [PHA-349](/PHA/issues/PHA-349) | Wired tokens into the live `index.html`. |

The full child-issue list lives in the [PHA-336 implementation roadmap comment](/PHA/issues/PHA-336).

# Annotated Mockups — SoD2 Diary v2

Twenty-one annotated mockups (seven screens × three breakpoints) per
[PHA-348](/PHA/issues/PHA-348). These are the pixel-level reference
engineering builds against. Every callout cites a component § from
[`design/components.md`](../components.md) and one or more tokens
from [`design/tokens.css`](../tokens.css), so the chain
plan → tokens → component spec → mockup → CSS implementation is
unbroken at every link.

Browse the full set in [`index.html`](./index.html). It loads the
SVGs through `<object>` so the device frames render at native
viewBox dimensions — no scaling, no guesswork.

## File naming

```
<screen>-<breakpoint>.svg
```

| screen                     | what it is                                                       |
| -------------------------- | ---------------------------------------------------------------- |
| `today`                    | Daily form — date, day, community, morale, resources, hearts, events |
| `people-front`             | Index-card stack with ALIVE/FALLEN/LEGACY filter                |
| `people-back`              | Card-back TIES panel (per §7 Ties That Bind)                    |
| `people-pencil-overlay`    | Desktop-only visual web of strongest ties                        |
| `history`                  | Past pages stack                                                  |
| `report`                   | Generated report panel (TRANSMIT TO NETWORK output)              |
| `sync`                     | Sync radio panel — closed / open / conflict states              |

| breakpoint | viewport width  | device viewBox |
| ---------- | --------------- | -------------- |
| `mobile`   | ≤640 px         | 360 × 760      |
| `tablet`   | 641–1024 px     | 768 × 1024     |
| `desktop`  | ≥1025 px        | 1440 × 900     |

Each SVG is the device viewBox plus a right-side annotation rail
(280–360 px wide). The rail holds numbered callouts; the device
itself shows numbered targets with leader lines pointing into the
rail.

## How to read an annotation

```
①  §1 Input slot · DATE
   --ink-brown · --font-typewriter
   Falls back to flat <input> with solid border if SVG filter
   unsupported.
```

1. **Title** — component § + a one-line role for this instance.
2. **Tokens** — the exact custom-property names from `tokens.css`
   that the implementation must reference. No raw hex/px in any
   call-out.
3. **Fallback** — the clarity-win note (per [Plan §0](/PHA/issues/PHA-336#document-plan)).
   What this component degrades to when textures, custom fonts,
   JS, or `prefers-reduced-motion` strip the chrome.

## Pencil-line overlay — why three files

The desktop pencil-line overlay (`people-pencil-overlay-desktop.svg`)
shows the visual web of strongest ties between cards. The
mobile/tablet variants are the explicit clarity-win fallback
documented inline: the same tie data surfaces via the per-card
TIES panel from §4. No data is hidden on smaller viewports —
only the spatial overlay is removed.

This honours the issue's "21 mockups" file count and the spec's
"desktop only" intent simultaneously: the fallback IS a deliverable.

## Re-rendering

```
cd design/mockups
python3 _render.py
```

The generator is the source of truth. After touching `tokens.css`
or `components.md`, re-run it and commit the regenerated SVGs in
the same change so the spec and the visual reference never drift.

The token mirror lives at the top of `_render.py` (SVG can't
read CSS variables) — keep those constants in sync if a token
changes value.

## Acceptance map (PHA-348 §Acceptance)

- [x] **All 7 screens × 3 breakpoints (= 21 mockups)** committed
      under `design/mockups/`. The pencil-overlay mobile/tablet
      variants are the documented fallback view.
- [x] **Each mockup names a clarity-win fallback in its
      annotations** — every callout's third line carries the
      fallback note; for screens whose entire rendering changes
      (pencil overlay), the fallback is the dominant content.
- [x] **Touch targets visibly meet 44 × 44 px on mobile/tablet
      variants** — every interactive element is sized at or above
      `--touch-min` (filter chips 28 px tall sit on 44 px rows
      with `display:grid grid-auto-columns:minmax(--touch-min,1fr)`,
      EDIT chips on tie rows have invisible 44 × 44 hit-boxes
      centered on the visible art per components.md §4).
- [x] **Mockup file naming `<screen>-<breakpoint>.<ext>`** so
      engineering can grep them. SVG so they version-control
      cleanly and stay crisp at any zoom.

## Cross-references

- [`../components.md`](../components.md) — component spec sheet
- [`../tokens.css`](../tokens.css) · [`../tokens.md`](../tokens.md) — design tokens
- [`../moodboard.md`](../moodboard.md) — visual reference + composition rules
- [`../data-model.md`](../data-model.md) — survivor / ties / sync / report shapes
- [Plan rev 3](/PHA/issues/PHA-336#document-plan) — §0 Clarity Wins, §3
  Interaction Language, §5 Responsive Strategy, §7 Ties That Bind,
  §8 Raise the Other Radio, §9 Deliverables.

# State of Decay 2 Community Diary

Narrative tracking tool for State of Decay 2 playthroughs. Generate daily reports to paste into LLM chats (Claude, ChatGPT, SillyTavern, etc.).

**Design source of truth:** [`/docs`](./docs/) — design philosophy, palette, type, motion, screenshots, and concept art live there. Live design preview: https://phattbeats.github.io/sod2-diary/design/preview.html

## Features

- **Daily Reports** - Resources, morale, plague hearts, events. Auto-copies on generate.
- **Survivor Roster** - Track individuals with traits and skills. Kill, exile, or send to Legacy Pool.
- **Auto-Rollover** - Values carry forward, day increments automatically.
- **Export/Import** - JSON backup of reports and roster.
- **Responsive** - Mobile and desktop.

## Example Output

```
The Survivors - Day 3 Report
Cascade Hills | Dread | Vogel House (Starter)
Plague Hearts: 9
Food: 3 -> 5
Medicine: 5 -> 4
...

Events: Cleared the police station. Lost Marcus to a feral ambush.

Active Roster:
- Maya, 28, Black F | Tough, Leader | Shooting, Medicine | Joined Day 1
- Ed, 42, White M | Asthma | Wits, Repair | Joined Day 1

Lost:
- Marcus, 35, Black M | Killed Day 3
```

## Hosting

Single HTML file. Open locally or deploy to GitHub Pages.

## Design

The v2 visual foundation (palette, typography, motion, spacing) lives in:

- [`docs/`](./docs/) — public-facing design reference (start here).
- [`design/tokens.css`](./design/tokens.css) — every CSS custom property the app uses.
- [`design/tokens.md`](./design/tokens.md) — rationale + WCAG-AA contrast proofs.
- [`design/moodboard.md`](./design/moodboard.md) — five reference surfaces with annotations.
- Live preview: https://phattbeats.github.io/sod2-diary/design/preview.html

## License

MIT

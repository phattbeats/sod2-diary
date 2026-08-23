# State of Decay 2 Community Diary

Narrative tracking tool for State of Decay 2 playthroughs. Generate daily reports to paste into LLM chats (Claude, ChatGPT, SillyTavern, etc.).

**Live:** https://phattbeats.github.io/sod2-diary/

## Features

- **Daily Reports** — resources, morale, plague hearts, events. Auto-copies on generate.
- **Survivor Roster** — track individuals with traits and skills. Kill, exile, or send to the Legacy Pool.
- **Auto-Rollover** — values carry forward, day increments automatically.
- **Export / Import** — JSON backup of reports and roster.
- **Themeable** — sepia / bone / coffee / olive moods, paper grain, handwriting styles.
- **Responsive** — mobile bottom dock + desktop layout.

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

## Layout

```
index.html        v4 — the live app (links v4/)
v4/styles.css     visual system
v4/app.js         app logic (no framework, no build step)
index-v3.html     v3 — legacy single-file fallback
docs/HANDOFF-v4.md notes on v4 + features pending re-review
```

## Hosting

Static files served from GitHub Pages (`main` branch root). No build step — open `index.html` locally or push to deploy.

## Authorship

Every commit must be authored by `phattbeats <obiwouldjablowme@protonmail.com>` and contain no `Co-authored-by` trailers. See [`docs/AUTHORSHIP.md`](./docs/AUTHORSHIP.md) and run `./scripts/install-git-hooks.sh` after cloning to enforce locally.

## License

MIT

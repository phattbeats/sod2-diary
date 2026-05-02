# Screenshots — auto-generated from the live preview

The PNGs in this folder are captured from
**https://phattbeats.github.io/sod2-diary/design/preview.html** by the GitHub
Actions workflow at [`/.github/workflows/screenshots.yml`](../../.github/workflows/screenshots.yml).
The capture script lives at [`/scripts/capture-screenshots.js`](../../scripts/capture-screenshots.js).

## Files captured each run

| File | Viewport | Notes |
|---|---|---|
| `preview-desktop.png` | 1280 × full | Wide layout, full scroll. |
| `preview-desktop-hero.png` | 1280 × 720 | Above-the-fold for the README hero. |
| `preview-mobile.png` | 390 × full | iPhone-class viewport, full scroll. |

## How to refresh manually

1. Push any commit to `main`, or
2. Open the **Actions** tab → **Screenshots** workflow → **Run workflow**.

The workflow waits up to 90 seconds for GitHub Pages to redeploy the live preview from the same commit, captures the three viewports above with system fonts loaded, and commits any PNGs that changed back to `main` under `docs/screenshots/`.

## First-run note

If this folder shows only this README and no PNGs, the workflow has not yet completed its first capture against the latest preview. Either wait ~2 minutes after a `main` push or trigger it manually from the Actions tab.

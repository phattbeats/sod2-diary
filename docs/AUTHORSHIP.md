# Authorship policy

Every sod2-diary commit must have the author identity `phattbeats <obiwouldjablowme@protonmail.com>` and must contain no `Co-authored-by` trailer, regardless of its name or email. This applies to every commit on every branch and to every commit in every PR range — not just HEAD.

## Configure a clone

```sh
git config user.name  phattbeats
git config user.email obiwouldjablowme@protonmail.com
```

sod2-diary has no `package.json` (the `scripts/package.json` is build-scratch from PHA-355 and is gitignored). Install the repo-local hooks manually:

```sh
./scripts/install-git-hooks.sh
```

or directly:

```sh
git config core.hooksPath .githooks
```

In Claude Code, set `includeCoAuthoredBy` to `false` in user or project `settings.json`. OpenClaw/Paperclip commit paths follow the same rule.

## What the gate rejects

- Any author other than `phattbeats <obiwouldjablowme@protonmail.com>` (including Claude Opus / Sonnet / Fable, Paperclip, Vision Quest, Hermes, and Brandon's other emails like `brandon@phatt.tech`, `ops@phatt.tech`, `*@users.noreply.github.com`).
- Any `Co-authored-by:` / `Co-Authored-By:` trailer, regardless of the name on it.
- Any non-`phattbeats` committer, with the single exception of GitHub's `web-flow` / `GitHub <noreply@github.com>` on a merge commit whose author is already `phattbeats`.

## Enforcement

- **Local:** `.githooks/commit-msg` rejects offending commits before they leave the clone.
- **CI:** `.github/workflows/authorship-check.yml` re-validates every commit in the PR or push range and prints the offending SHA + line.

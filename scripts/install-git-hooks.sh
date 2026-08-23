#!/usr/bin/env sh
# Wire the repo-local commit-msg hook so `git commit` enforces the
# phattbeats-only authorship policy. Idempotent: safe to re-run.
#
# sod2-diary has no package.json (pure static / scripts/ folder),
# so we install the hook path manually rather than via `npm run prepare`.
set -eu

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS_PATH=".githooks"

cd "$REPO_ROOT"

if [ ! -d "$HOOKS_PATH" ]; then
  printf 'error: missing %s/ directory.\n' "$HOOKS_PATH" >&2
  exit 1
fi

if [ ! -x "$HOOKS_PATH/commit-msg" ]; then
  chmod +x "$HOOKS_PATH/commit-msg"
fi

git config core.hooksPath "$HOOKS_PATH"

printf 'Installed git hooks from %s/ for repo %s.\n' "$HOOKS_PATH" "$REPO_ROOT"
printf 'Verify with:  git config --get core.hooksPath\n'

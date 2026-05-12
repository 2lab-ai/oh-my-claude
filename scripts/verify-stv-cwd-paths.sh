#!/usr/bin/env bash
# verify-stv-cwd-paths.sh
#
# Assertion: stv plugin must NEVER store working artifacts under the user's home
# directory (~/.claude/stv, $HOME/.claude/stv). All temporary stv artifacts
# (trace.md, spec.md, etc.) must live under the current working directory so
# multi-tenant / multi-session use (e.g. soma-work Slack agent) keeps state
# isolated per CWD.
#
# RED behavior: exits non-zero if any plugins/stv/** file contains a
# `~/.claude` or `$HOME/.claude` path.
# GREEN behavior: silent + exit 0.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STV_DIR="$ROOT/plugins/stv"

if [ ! -d "$STV_DIR" ]; then
  echo "FAIL: stv plugin dir not found at $STV_DIR" >&2
  exit 2
fi

# Match the literal `~/.claude` and `$HOME/.claude` prefixes used by stv files.
# grep -rE keeps it portable; we deliberately scan all files, not just *.md.
HITS="$(grep -rEn '(~|\$HOME)/\.claude/stv' "$STV_DIR" || true)"

if [ -n "$HITS" ]; then
  echo "FAIL: stv plugin contains home-directory storage paths:" >&2
  echo "$HITS" >&2
  echo "" >&2
  echo "All stv working artifacts must be stored CWD-relative (e.g. ./.claude/stv/...)." >&2
  exit 1
fi

echo "OK: stv plugin uses CWD-relative storage paths."

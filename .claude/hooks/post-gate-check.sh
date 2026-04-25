#!/bin/bash
# Hook: post-gate-check
# Trigger: PostToolUse[gate_check]
# Purpose: Log gate verdicts and update session state after each quality gate run.
# Env vars: GATE_NAME, GATE_SCORE, GATE_STATUS (PASSED|FAILED), GATE_BOOK_ID

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S)
GATES_LOG="$PROJECT_ROOT/production/session-logs/$DATE.md"
SESSION_FILE="$PROJECT_ROOT/production/session-state/active.md"

GATE_NAME="${GATE_NAME:-UNKNOWN}"
GATE_SCORE="${GATE_SCORE:-0.00}"
GATE_STATUS="${GATE_STATUS:-UNKNOWN}"
GATE_BOOK_ID="${GATE_BOOK_ID:-unknown}"

mkdir -p "$(dirname "$GATES_LOG")"

# Log gate result
{
  echo ""
  echo "### Gate: $GATE_NAME"
  echo "- book_id: $GATE_BOOK_ID"
  echo "- score: $GATE_SCORE"
  echo "- status: $GATE_STATUS"
  echo "- timestamp: $TIMESTAMP"
} >> "$GATES_LOG"

# Update session state
if [ -f "$SESSION_FILE" ]; then
  if [ "$GATE_STATUS" = "FAILED" ]; then
    sed -i.bak "s/^status: .*/status: blocked_at_$GATE_NAME/" "$SESSION_FILE" 2>/dev/null || true
  fi
fi

# Console output
if [ "$GATE_STATUS" = "PASSED" ]; then
  echo "[post-gate-check] ✅ $GATE_NAME PASSED (score: $GATE_SCORE)"
else
  echo "[post-gate-check] ❌ $GATE_NAME FAILED (score: $GATE_SCORE) — review required" >&2
fi

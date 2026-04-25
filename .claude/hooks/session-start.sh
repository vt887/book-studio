#!/bin/bash
# Hook: session-start
# Trigger: PostToolUse[session_start]
# Purpose: Initialize or resume session state on Book Studio startup.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SESSION_FILE="$PROJECT_ROOT/production/session-state/active.md"
LOGS_DIR="$PROJECT_ROOT/production/session-logs"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S)

mkdir -p "$LOGS_DIR"

if [ -f "$SESSION_FILE" ]; then
  PREV_STATUS=$(grep -m1 "^status:" "$SESSION_FILE" 2>/dev/null | awk '{print $2}' || echo "unknown")
  echo "[session-start] Resuming session. Previous status: $PREV_STATUS"
else
  echo "[session-start] Starting new session."
  cat > "$SESSION_FILE" << EOF
# Active Session
status: active
started: $TIMESTAMP
last_command: /start
processed_books: []
EOF
fi

LOG_ENTRY="## Session: $TIMESTAMP"$'\n'"- Event: session_start"$'\n'
echo "$LOG_ENTRY" >> "$LOGS_DIR/$DATE.md"

echo "[session-start] Session initialized at $TIMESTAMP"

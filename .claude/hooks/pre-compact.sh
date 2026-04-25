#!/bin/bash
# Hook: pre-compact
# Trigger: PreCompact
# Purpose: Save critical session state before context compression so it can be restored.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SESSION_FILE="$PROJECT_ROOT/production/session-state/active.md"
COMPACT_SNAPSHOT="$PROJECT_ROOT/production/session-state/pre-compact-snapshot.md"
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S)

echo "[pre-compact] Saving session snapshot before compaction..."

{
  echo "# Pre-Compact Snapshot"
  echo "saved_at: $TIMESTAMP"
  echo ""
  echo "## Active Session State"
  if [ -f "$SESSION_FILE" ]; then
    cat "$SESSION_FILE"
  else
    echo "(no active session)"
  fi
  echo ""
  echo "## Processed Books"
  if [ -d "$PROJECT_ROOT/session-knowledge" ]; then
    find "$PROJECT_ROOT/session-knowledge" -name "unified-knowledge.json" | while read -r f; do
      BOOK_ID=$(basename "$(dirname "$f")")
      CONCEPT_COUNT=$(python3 -c "import json,sys; d=json.load(open('$f')); print(len(d.get('concepts', [])))" 2>/dev/null || echo "?")
      echo "  - $BOOK_ID ($CONCEPT_COUNT concepts)"
    done
  fi
  echo ""
  echo "## Role Maps"
  if [ -d "$PROJECT_ROOT/production/role-maps" ]; then
    find "$PROJECT_ROOT/production/role-maps" -name "*.json" -exec basename {} .json \; 2>/dev/null | sed 's/^/  - /'
  fi
} > "$COMPACT_SNAPSHOT"

echo "[pre-compact] Snapshot saved to $COMPACT_SNAPSHOT"

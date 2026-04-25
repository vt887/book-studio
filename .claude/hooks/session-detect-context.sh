#!/bin/bash
# Hook: session-detect-context
# Trigger: PreToolUse[detect_context]
# Purpose: Detect current session context — which books are processed, active role-maps, last command.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SESSION_FILE="$PROJECT_ROOT/production/session-state/active.md"
KNOWLEDGE_DIR="$PROJECT_ROOT/session-knowledge"
OBSIDIAN_VAULT="$PROJECT_ROOT/obsidian-export"

echo "=== Book Studio Context (Obsidian-First) ==="

# Processed books
if [ -d "$KNOWLEDGE_DIR" ]; then
  BOOKS=$(find "$KNOWLEDGE_DIR" -name "unified-knowledge.json" -exec dirname {} \; | xargs -I{} basename {} 2>/dev/null | tr '\n' ', ')
  if [ -n "$BOOKS" ]; then
    echo "Processed books (session cache): ${BOOKS%,}"
  else
    echo "Processed books: none"
  fi
else
  echo "Processed books: none (session-knowledge/ not found)"
fi

# Obsidian vaults
if [ -d "$OBSIDIAN_VAULT" ]; then
  VAULTS=$(find "$OBSIDIAN_VAULT" -maxdepth 1 -mindepth 1 -type d ! -name ".git" 2>/dev/null | xargs -I{} basename {} | tr '\n' ', ')
  if [ -n "$VAULTS" ]; then
    echo "Obsidian vaults (primary output): ${VAULTS%,}"
  else
    echo "Obsidian vaults: none"
  fi
fi

# Active session
if [ -f "$SESSION_FILE" ]; then
  LAST_CMD=$(grep -m1 "^last_command:" "$SESSION_FILE" 2>/dev/null | awk '{print $2}' || echo "unknown")
  echo "Last command: $LAST_CMD"
fi

echo "=== End Context ==="

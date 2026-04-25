#!/bin/bash
# Hook: log-decision
# Trigger: PostToolUse[decision]
# Purpose: Append architectural or role-application decisions to the decisions log.
# Usage: called with env vars DECISION_TITLE, DECISION_CONTEXT, DECISION_CHOICE, DECISION_RATIONALE

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DECISIONS_DIR="$PROJECT_ROOT/production/decisions"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S)
LOG_FILE="$DECISIONS_DIR/$DATE-decisions.md"

mkdir -p "$DECISIONS_DIR"

TITLE="${DECISION_TITLE:-Unnamed Decision}"
CONTEXT="${DECISION_CONTEXT:-}"
CHOICE="${DECISION_CHOICE:-}"
RATIONALE="${DECISION_RATIONALE:-}"
BOOK="${DECISION_BOOK:-}"
CONCEPT="${DECISION_CONCEPT:-}"

{
  echo ""
  echo "## Decision: $TITLE"
  echo "**Recorded:** $TIMESTAMP"
  [ -n "$BOOK" ]    && echo "**Book:** $BOOK"
  [ -n "$CONCEPT" ] && echo "**Concept:** $CONCEPT"
  [ -n "$CONTEXT" ] && echo "**Context:** $CONTEXT"
  [ -n "$CHOICE" ]  && echo "**Decision:** $CHOICE"
  [ -n "$RATIONALE" ] && echo "**Rationale:** $RATIONALE"
  echo ""
  echo "---"
} >> "$LOG_FILE"

echo "[log-decision] Decision logged to $LOG_FILE"

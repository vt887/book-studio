#!/bin/bash
# Hook: validate-before-apply
# Trigger: PreToolUse[apply]
# Purpose: Verify prerequisites before any /apply-as-* or /auto-apply command runs.
# Exits non-zero to block if validation fails.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BOOK_ID="${APPLY_BOOK_ID:-}"
ROLE="${APPLY_ROLE:-}"

ERRORS=0

echo "[validate-before-apply] Checking prerequisites (Obsidian-first)..."

# Check 1: book_id provided (only validate if we're actually applying something)
if [ -z "$BOOK_ID" ]; then
  echo "[validate-before-apply] Skipping validation (APPLY_BOOK_ID not set - not applying)"
  exit 0
else
  # Check 2: unified-knowledge.json exists in session cache
  KNOWLEDGE_FILE="$PROJECT_ROOT/session-knowledge/$BOOK_ID/unified-knowledge.json"
  if [ ! -f "$KNOWLEDGE_FILE" ]; then
    echo "ERROR: $KNOWLEDGE_FILE not found. Run /read-book first." >&2
    ERRORS=$((ERRORS + 1))
  else
    echo "  ✓ unified-knowledge.json exists for $BOOK_ID"
  fi

  # Check 3: Obsidian vault directory exists or will be created
  OBSIDIAN_VAULT="$PROJECT_ROOT/obsidian-export/$BOOK_ID"
  if [ ! -d "$OBSIDIAN_VAULT" ]; then
    echo "  ℹ Obsidian vault will be created at $OBSIDIAN_VAULT"
  else
    echo "  ✓ Obsidian vault exists for $BOOK_ID"
  fi

  # Check 4: role-map exists (optional but recommended)
  ROLE_MAP="$PROJECT_ROOT/production/role-maps/$BOOK_ID-role-map.json"
  if [ ! -f "$ROLE_MAP" ]; then
    echo "WARNING: role-map not found for $BOOK_ID. Run /suggest-roles for better results." >&2
  else
    echo "  ✓ role-map exists for $BOOK_ID"
  fi
fi

# Check 5: role is valid
VALID_ROLES="developer architect tester devops security data performance observability techlead legacy platform"
if [ -n "$ROLE" ]; then
  if echo "$VALID_ROLES" | grep -qw "$ROLE"; then
    echo "  ✓ role '$ROLE' is valid"
  else
    echo "ERROR: role '$ROLE' is not valid. Valid roles: $VALID_ROLES" >&2
    ERRORS=$((ERRORS + 1))
  fi
fi

if [ "$ERRORS" -gt 0 ]; then
  echo "[validate-before-apply] BLOCKED: $ERRORS prerequisite(s) failed." >&2
  exit 1
fi

echo "[validate-before-apply] All prerequisites passed."

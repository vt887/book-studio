# Skill: /review-quality

**Trigger:** `/review-quality`
**Director:** `synthesis-director`
**Purpose:** Run quality gate checks against any artifact and surface findings.

---

## Steps

### Phase 1: Select Artifact
```
AskUserQuestion {
  "question": "Який артефакт перевірити?",
  "options": [
    "📄 Extraction (EXTRACT-QUALITY gate)",
    "📝 Summary (SUMMARY-QUALITY gate)",
    "🕸️ Graph (GRAPH-VALID gate)",
    "🗒️ Obsidian export (OBSIDIAN-READY gate)",
    "🗺️ Role map (ROLE-MAP-VALID gate)",
    "⚙️ Application output (APPLY-VALID gate)"
  ]
}
```

### Phase 2: Load Artifact
Load the corresponding file from `session-knowledge/` or `production/`.

### Phase 3: Run validator-spec
Agent: `validator-spec`
Input: artifact + gate name + threshold
Run all checks in the gate's checklist.

### Phase 4: Present Verdict
If PASS:
```
✅ GATE: {gate_name} PASSED ({score:.2f})
{N} checks passed. Artifact is production-ready.
```

If FAIL:
```
❌ GATE: {gate_name} FAILED ({score:.2f})
Failed checks:
  - {check_1}: {reason} (location: {field/line})
  - {check_2}: {reason}

Recommendation: {what to fix}
```

### Phase 5: Optional Fix
Ask: "Виправити знайдені проблеми автоматично? (для деяких типів помилок)"
If yes: delegate corrections to the relevant specialist.

### Verdict
```
Gate: {gate_name} | Score: {score} | Status: PASSED/FAILED
```

# Skill: /apply-as-tester

**Trigger:** `/apply-as-tester`
**Director:** `application-director`
**Specialist:** `tester-spec`
**Purpose:** Apply book concepts as a QA/test engineer — test cases, test strategy, edge case analysis.

---

## Steps

### Phase 1: Select Book + Concept
Show tester-relevant concepts from role-map.

### Phase 2: Select Task
```
AskUserQuestion {
  "question": "Що ти хочеш зробити як Tester?",
  "options": [
    "🧪 Написати тест-кейси для компонента",
    "📋 Розробити тест-стратегію",
    "🔍 Знайти edge cases",
    "🏗️ Зробити код testable (refactor for testability)",
    "🔄 Написати characterization tests для legacy-коду"
  ]
}
```

Ask for: component/function to test (paste code or describe), tech stack/framework.

### Phase 3: Load Context
Read concept from `unified-knowledge.json`.
Extract: how_to_apply, anti_pattern, related testing principles.

### Phase 4: Generate Output
Agent: `tester-spec`

Test cases: Given/When/Then format + runnable code in user's framework.
Strategy: scope, approach, levels (unit/integration/e2e), coverage targets.
Edge cases: systematic enumeration (nulls, boundaries, concurrency, failures).
Testability refactor: show how to restructure code to enable testing.
Characterization tests: capture current behavior before refactoring.

### Phase 5: Gate Check
Run `[APPLY-VALID]` (threshold: 0.85).

### Phase 6: Save
`production/applications/tester-output/{task_id}.md`

### Verdict
```
✅ COMPLETE
Concept: {concept_name} | Tests generated: {N}
Artifact: production/applications/tester-output/{task_id}.md
```

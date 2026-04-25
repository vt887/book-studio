# Skill: /apply-as-developer

**Trigger:** `/apply-as-developer`
**Director:** `application-director`
**Specialist:** `developer-spec`
**Purpose:** Apply book concepts as a software developer — code, refactoring, bug analysis.

---

## Steps

### Phase 1: Select Book + Concept
If role-map exists for a book: show developer concepts ranked by relevance.
Otherwise: ask user to describe the concept manually.

```
AskUserQuestion {
  "question": "Яку концепцію застосувати як Developer?",
  "options": ["{top developer concepts from role-map}"]
}
```

### Phase 2: Select Task
```
AskUserQuestion {
  "question": "Що ти хочеш зробити?",
  "options": [
    "💻 Написати код застосовуючи концепцію",
    "♻️ Зрефакторити існуючий код",
    "🐛 Проаналізувати баг через призму концепції",
    "📋 Скласти план покращення кодової бази"
  ]
}
```

If refactoring or bug analysis: ask user to paste the existing code.

### Phase 3: Load Context
Read `session-knowledge/{book_id}/unified-knowledge.json`.
Filter concept by ID from role-map.
Extract: definition, source_quote, how_to_apply, anti_pattern.

### Phase 4: Generate Output
Agent: `developer-spec`
Input: concept context + task + user code (if provided)

Output includes:
- Code with inline `[concept: {name}]` citations
- Before/after comparison (if refactoring)
- Explanation of how the concept shapes the solution
- Anti-pattern warning if applicable

### Phase 5: Gate Check
Run `[APPLY-VALID]` (threshold: 0.85).

### Phase 6: Save
`production/applications/developer-output/{task_id}.md`

### Verdict
```
✅ COMPLETE
Concept: {concept_name} | Task: {task_type}
Artifact: production/applications/developer-output/{task_id}.md
```

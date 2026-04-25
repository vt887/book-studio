# Skill: /apply-as-architect

**Trigger:** `/apply-as-architect`
**Director:** `application-director`
**Specialist:** `architect-spec`
**Purpose:** Apply book concepts as a software architect — ADRs, trade-off analysis, pattern catalog, risk register.

---

## Steps

### Phase 1: Select Book + Concept
Show architect-relevant concepts from role-map ranked by score.

### Phase 2: Select Task
```
AskUserQuestion {
  "question": "Що ти хочеш зробити як Architect?",
  "options": [
    "📄 Написати ADR (Architecture Decision Record)",
    "⚖️ Провести trade-off аналіз",
    "📚 Додати патерн до каталогу",
    "⚠️ Оновити risk register",
    "🗺️ Описати архітектуру компонента"
  ]
}
```

If ADR: ask for decision context (what problem, what options were considered).
If trade-off: ask for 2–4 alternatives to compare.

### Phase 3: Load Context
Read `unified-knowledge.json` + `mental-model.json` for the book.
Extract concept + mental model assumptions relevant to the task.

### Phase 4: Generate Output
Agent: `architect-spec`

ADR output: complete ADR-NNN document with context, decision, rationale (citing concept), consequences, alternatives.
Trade-off: comparison table with scores + recommendation citing concept.
Pattern: catalog entry with intent, applicability, structure, consequences.
Risk: risk register rows with mitigations.

### Phase 5: Gate Check
Run `[APPLY-VALID]` (threshold: 0.85).

### Phase 6: Save
`production/applications/architect-output/{task_id}.md`
Also copy ADR to `docs/decisions/` if task was ADR.

### Verdict
```
✅ COMPLETE
Concept: {concept_name} | Output: {output_type}
Artifact: production/applications/architect-output/{task_id}.md
```

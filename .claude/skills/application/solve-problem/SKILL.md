# Skill: /solve-problem

**Trigger:** `/solve-problem`
**Director:** `application-director`
**Purpose:** Solve a specific engineering problem using the lens of a book's concepts.

---

## Steps

### Phase 1: Define the Problem
```
AskUserQuestion {
  "question": "Опиши проблему, яку треба вирішити:",
  "fields": [
    "Проблема: (опис симптомів або бажаного результату)",
    "Контекст: (технологія, команда, обмеження)",
    "Вже пробував: (що не спрацювало)"
  ]
}
```

### Phase 2: Match to Book Knowledge
Agent: `application-director`
1. Search `library-index.json` (or available `unified-knowledge.json` files) for concepts relevant to the problem
2. If role-map exists: find concepts that have application_ideas matching the problem domain
3. Present top 3 matching concepts with justification:
   "Концепція **{name}** з **{book}** може допомогти, тому що: {justification}"

Ask user to confirm which concept to apply (or accept top match).

### Phase 3: Select Role Perspective
```
AskUserQuestion {
  "question": "З якої ролі вирішити проблему?",
  "options": ["developer", "architect", "tester", "devops", "security", "data", "performance", "observability", "techlead", "legacy", "platform"]
}
```

### Phase 4: Generate Solution
Agent: corresponding `{role}-spec`
Input: problem description + selected concept + role context

Output:
- Root cause analysis through the concept's lens
- Step-by-step solution
- Relevant code/config/diagram
- Anti-patterns to avoid (from book)
- Concept citation

### Phase 5: Gate Check
Run `[APPLY-VALID]` (threshold: 0.85).

### Phase 6: Save
`production/applications/{role}-output/{task_id}.md`

### Verdict
```
✅ COMPLETE
Problem solved via: [{concept_name}] from *{book_title}*
Artifact: production/applications/{role}-output/{task_id}.md
```

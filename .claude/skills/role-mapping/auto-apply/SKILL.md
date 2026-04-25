# Skill: /auto-apply

**Trigger:** `/auto-apply`
**Director:** `application-director`
**Purpose:** Automatically select the best role + concept from a book's role-map and generate actionable output.

---

## Steps

### Phase 1: Select Role + Concept
```
AskUserQuestion {
  "question": "Як хочеш застосувати знання?",
  "options": [
    "🤖 Авто-вибір (система обирає кращу роль і концепцію)",
    "🎯 Вибрати роль вручну",
    "🔍 Вибрати конкретну концепцію"
  ]
}
```

**If auto-select:**
Agent: `application-director`
1. Load `production/role-maps/{book_id}-role-map.json`
2. Find role with highest `score` in `role_summary`
3. Within that role, find concept with highest `relevance_score` and complexity=`simple`
4. Confirm: "Я вибрав: роль **{role}**, концепція **{concept}**. Підтверджуєш?"

**If manual role:**
Show role list from role-map, let user pick. Then show top 3 concepts for that role.

**If manual concept:**
Show all concepts from role-map, let user pick.

### Phase 2: Select Task Type
```
AskUserQuestion {
  "question": "Що ти хочеш отримати для ролі {role} + концепції {concept}?",
  "options": [
    "💻 Код / рефакторинг",
    "📐 ADR / архітектурне рішення",
    "🧪 Тести / тест-стратегія",
    "🚀 Pipeline / deployment config",
    "🔒 Threat model / security checklist",
    "📊 Schema / migration",
    "⚡ Benchmark / optimization plan",
    "📡 Observability config / dashboard",
    "👔 Team standards / onboarding",
    "🏚️ Migration plan / legacy refactor",
    "🛠️ Platform config / golden path"
  ]
}
```

### Phase 3: Load Knowledge
Agent: `application-director`
- Read `production/role-maps/{book_id}-role-map.json`
- Read `session-knowledge/{book_id}/unified-knowledge.json`
- Filter: concept + role + task context

### Phase 4: Generate task_id
`{book_id}_{role}_{concept_slug}_{timestamp}`

### Phase 5: Spawn Role Specialist
Agent: `application-director` delegates to `{role}-spec`
Input: selected concept + task type + filtered book knowledge
Output: role-appropriate artifact with concept citations

### Phase 6: Gate Check
Run `[APPLY-VALID]` (threshold: 0.85).
On fail: return specific failures to specialist for one retry.

### Phase 7: Save
Agent: `application-director`
Save to: `production/applications/{role}-output/{task_id}.md`
With header:
```markdown
# {Task Title}
- **Book:** {title} by {author}
- **Role:** {role}
- **Concept:** {concept_name}
- **Generated:** {ISO8601}
- **Gate:** APPLY-VALID PASSED ({score})
```

### Verdict
```
✅ COMPLETE
Role: {role} | Concept: {concept_name}
Artifact: production/applications/{role}-output/{task_id}.md
```

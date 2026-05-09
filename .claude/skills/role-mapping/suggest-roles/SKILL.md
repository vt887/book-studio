# Skill: /suggest-roles

**Trigger:** `/suggest-roles` (also auto-triggered after `/read-book` when `autoSuggestRoles: true`)
**Director:** `role-mapping-director`
**Purpose:** Analyze all book concepts and map them to professional roles with specific, actionable recommendations.

---

## Steps

### Phase 1: Load Book Knowledge
If invoked manually: ask which book (list available from `session-knowledge/`).
If auto-triggered: use book_id from preceding `/read-book`.

Load:
- `session-knowledge/{book_id}/unified-knowledge.json`
- `session-knowledge/{book_id}/summary.json`
- `session-knowledge/{book_id}/mental-model.json`

### Phase 2: Concept Analysis
Agent: `role-mapper-spec`
Input: `unified-knowledge.json`

For EVERY concept:
- Determine `applicable_roles` (which roles can use this?)
- Determine `primary_role` (which role benefits most?)
- Write `justification` (specific, not generic)
- Generate 2–3 `application_ideas` (format: "Використай X щоб Y у Z")
- Rate `complexity`: simple|medium|complex
- List `prerequisites`

Output: role-map object (not yet saved — pass to director for ranking)

### Phase 3: Rank and Cluster
Agent: `role-mapping-director`
- Group concepts by role
- Calculate score per role: Σ(relevance × confidence) / total
- Identify quick wins: complexity=simple AND relevance ≥ 0.8
- Sort roles by score descending

### Phase 4: Present to User
Show structured options (only roles with ≥ 1 concept):

```
AskUserQuestion {
  "question": "На основі '{{title}}' знайдено {{N}} концепцій. Топ ролей за релевантністю:",
  "options": [
    "👨‍💻 Developer ({{N}} концепцій) — {{concept_1}}, {{concept_2}}, {{concept_3}}",
    "🏗️ Architect ({{N}} концепцій) — ...",
    "🧪 Tester ({{N}} концепцій) — ...",
    "🚀 DevOps ({{N}} концепцій) — ...",
    "🔒 Security ({{N}} концепцій) — ...",
    "📊 Data Engineer ({{N}} концепцій) — ...",
    "⚡ Performance ({{N}} концепцій) — ...",
    "📡 Observability ({{N}} концепцій) — ...",
    "👔 TechLead ({{N}} концепцій) — ...",
    "🏚️ Legacy Modernizer ({{N}} концепцій) — ...",
    "🛠️ Platform Engineer ({{N}} концепцій) — ...",
    "🎯 Всі ролі (повний звіт)"
  ]
}
```

### Phase 5: Gate Check
Run `[ROLE-MAP-VALID]` (threshold: 0.80).
On fail: retry role-mapper-spec with specific corrections.

After scoring, log the result explicitly via Bash:
```bash
GATE_NAME="ROLE-MAP-VALID" GATE_STATUS="PASSED_OR_FAILED" GATE_SCORE="0.00" \
  GATE_BOOK_ID="{book_id}" bash .claude/hooks/post-gate-check.sh
```
Replace `PASSED_OR_FAILED` and `0.00` with actual verdict and score.

### Phase 6: Save
Agent: `role-mapping-director`
Save to:
- `production/role-maps/{book_id}-role-map.json` (machine)
- `production/role-maps/{book_id}-role-map.md` (human-readable)

### Phase 7: Hand Off
If user selected a role: invoke `/auto-apply` with selected role + book_id.

### Verdict
```
✅ COMPLETE
Concepts mapped: {N}
Roles with applicable concepts: {N_roles}
Quick wins: {N_quick_wins}
Artifacts: production/role-maps/{book_id}-role-map.json
```

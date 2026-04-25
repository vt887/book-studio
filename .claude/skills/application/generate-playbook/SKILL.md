# Skill: /generate-playbook

**Trigger:** `/generate-playbook`
**Director:** `application-director`
**Purpose:** Generate a comprehensive role-specific playbook from a book's knowledge — a reusable reference guide for a team or individual.

---

## Steps

### Phase 1: Select Book + Role
Ask which book and which role the playbook is for.
Load role-map for that book.

### Phase 2: Define Scope
```
AskUserQuestion {
  "question": "Що охоплює playbook?",
  "options": [
    "📚 Всі концепції для обраної ролі",
    "⚡ Тільки quick wins (simple complexity)",
    "🎯 Конкретна тема (вибрати з концепцій)",
    "👥 Онбординг нового члена команди"
  ]
}
```

### Phase 3: Load Concepts
Filter `role-map.json` by selected role and scope.
Sort by: quick_wins first, then by complexity (simple → complex).

### Phase 4: Generate Playbook
Agent: corresponding `{role}-spec`

Playbook structure:
```markdown
# Playbook: {role} — {book_title}

## Overview
{what this playbook covers, who it's for}

## Concepts (ordered by priority)

### 1. {concept_name} [complexity: simple]
**What:** {definition}
**Why it matters:** {why_it_matters}
**How to apply:** {how_to_apply}
**Application ideas:**
- {idea_1}
- {idea_2}
**Anti-pattern:** {anti_pattern}
**Prerequisite:** {prerequisites}
---

### 2. {concept_name} [complexity: medium]
...

## Quick Reference Card
| Concept | Action | When to Use |
|---|---|---|

## Checklist
- [ ] {concept applied}
```

### Phase 5: Gate Check
Run `[APPLY-VALID]` (threshold: 0.85).

### Phase 6: Save
`production/applications/{role}-output/playbook-{book_id}-{timestamp}.md`

### Verdict
```
✅ COMPLETE
Playbook: {role} | {N} concepts | Book: {title}
Artifact: production/applications/{role}-output/playbook-{book_id}-{timestamp}.md
```

# Skill: /review-implementation

**Trigger:** `/review-implementation`
**Director:** `application-director`
**Purpose:** Review an existing implementation against book concepts — identify adherence, violations, and improvement opportunities.

---

## Steps

### Phase 1: Collect Implementation
```
AskUserQuestion {
  "question": "Що ти хочеш переглянути?",
  "options": [
    "📄 Вставити код для огляду",
    "📁 Вказати шлях до файлу",
    "🏗️ Описати архітектуру (текстом)"
  ]
}
```
Also ask: which book to use as the review lens, which role perspective.

### Phase 2: Load Review Lens
Read `unified-knowledge.json` for the selected book.
Filter concepts relevant to the selected role.
Particularly focus on: anti-patterns, principles, how_to_apply notes.

### Phase 3: Review
Agent: `{role}-spec`

Review output format:
```markdown
# Implementation Review
**Book Lens:** {title} by {author}
**Role:** {role}
**Reviewed:** {date}

## Summary
{2–3 sentence overall assessment}

## Adherences ✅ (what's done well)
| Concept | Evidence | Quality |
|---|---|---|
| {concept} | {code reference} | {good/excellent} |

## Violations ⚠️ (what could improve)
| Concept | Violation | Location | Severity |
|---|---|---|---|
| {concept} | {description} | {file:line} | high/med/low |

## Anti-Patterns Found ❌
| Anti-Pattern | Location | Risk | Fix |
|---|---|---|---|

## Improvement Plan
1. **{highest priority fix}** — {concept reference} — Effort: {days}
2. ...

## Score
Adherence to [{book}] principles: {score}/10
```

### Phase 4: Gate Check
Run `[APPLY-VALID]` (threshold: 0.85) — verify review cites real concepts.

### Phase 5: Save
`production/applications/{role}-output/review-{task_id}.md`

### Verdict
```
✅ COMPLETE
Adherences: {N} | Violations: {N} | Anti-patterns: {N}
Artifact: production/applications/{role}-output/review-{task_id}.md
```

# Example: /suggest-roles — Clean Code by Robert C. Martin

This example shows what happens when you run `/suggest-roles` after processing "Clean Code".

---

## Input
Book processed: `clean-code` (23 concepts extracted)

---

## Phase 2 Output: Concept Mappings (excerpt from role-map.json)

```json
{
  "concept_id": "clean-code_srp",
  "concept_name": "Single Responsibility Principle",
  "applicable_roles": ["developer", "architect", "techlead"],
  "primary_role": "developer",
  "justification": "Developer can use SRP to split classes with multiple reasons to change into focused, single-purpose classes, reducing the blast radius of changes",
  "application_ideas": [
    "Використай SRP щоб розбити OrderService на OrderValidator + OrderPricer + OrderRepository у payment microservice",
    "Використай SRP щоб виокремити NotificationService з UserService щоб email-логіка не залежала від user CRUD",
    "Використай SRP щоб виявити God Objects у legacy codebase через аналіз кількості причин для зміни"
  ],
  "complexity": "medium",
  "prerequisites": ["OOP basics", "dependency injection"]
}
```

```json
{
  "concept_id": "clean-code_meaningful-names",
  "concept_name": "Meaningful Names",
  "applicable_roles": ["developer", "techlead"],
  "primary_role": "developer",
  "justification": "Developer can use Meaningful Names to make code self-documenting, reducing the need for comments and speeding up code review",
  "application_ideas": [
    "Використай Meaningful Names щоб замінити всі однобуквені змінні у критичних алгоритмах розкриваючи їх намір",
    "Використай Meaningful Names щоб провести rename refactoring у legacy codebase починаючи з публічного API"
  ],
  "complexity": "simple",
  "prerequisites": []
}
```

---

## Phase 4 Output: AskUserQuestion

```
На основі "Clean Code" знайдено 23 концепції. Топ ролей за релевантністю:

👨‍💻 Developer (12 концепцій) — SRP, Meaningful Names, Unit Tests
🏗️ Architect (5 концепцій) — Separation of Concerns, Dependency Inversion, Open/Closed Principle
🧪 Tester (4 концепцій) — Testable Design, TDD, Test Isolation, F.I.R.S.T. Principles
👔 TechLead (2 концепцій) — Boy Scout Rule, Code Standards
🏚️ Legacy Modernizer (2 концепцій) — Refactoring, Seam Identification
🏗️ Platform Engineer (0 — omitted)
...
🎯 Всі ролі (повний звіт)
```

User selects: **👨‍💻 Developer**

---

## Phase 5: Saved Artifacts

**JSON:** `production/role-maps/clean-code-role-map.json`
**Markdown:** `production/role-maps/clean-code-role-map.md`

---

## Role Map Markdown (excerpt)

```markdown
# Role Map: Clean Code

## 👨‍💻 Developer (12 concepts, score: 0.91)
### Quick Wins (can apply in 1–2 days)
- **Meaningful Names** — Rename variables in a module to reveal intent
- **Boy Scout Rule** — Leave every file you touch cleaner than you found it

### Medium Effort (1 week)
- **Single Responsibility Principle** — Split OrderService into focused classes
- **Unit Tests** — Add test suite to uncovered critical path

### Complex (1+ month)
- **Clean Architecture** — Restructure to separate business rules from I/O
```

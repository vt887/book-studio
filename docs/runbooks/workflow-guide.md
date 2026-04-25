# Workflow Guide

Complete guide to using Book Studio's multi-agent reading and knowledge application system.

---

## Core Workflow

### 1. Process a New Book
```
/read-book
```
- Paste text, provide file path, or URL
- System extracts concepts, summarizes, builds mental model
- Produces `session-knowledge/{book_id}/unified-knowledge.json`
- **Auto-triggers:** `/suggest-roles` if `autoSuggestRoles: true`

### 2. Explore Role Recommendations
```
/suggest-roles
```
- System maps all concepts to 11 professional roles
- Presents ranked options with concept counts
- Select a role to proceed to application

### 3. Apply Knowledge
```
/auto-apply                    # System picks best role + concept
/apply-as-developer            # Apply as developer
/apply-as-architect            # Apply as architect
/apply-as-tester               # Apply as tester
/apply-as-devops               # Apply as DevOps engineer
/apply-as-security             # Apply as security engineer
```

### 4. Build Knowledge Graph (optional)
```
/build-graph
```
- Generates Neo4j Cypher statements
- Saves to `graph-export/{book_id}/`

### 5. Export to Obsidian (optional)
```
/export-obsidian
```
- Atomic notes per concept
- Backlinks + tags
- Saves to `obsidian-export/{book_id}/`

---

## Multi-Book Workflow

### Compare Two Books
```
/compare-books
```
Select 2+ processed books → get conflicts, consensus, evolution chains.

### Library Synthesis
```
/synthesize-library
```
Processes all books → global concept index + cross-cutting concepts.

---

## Problem-Solving Workflow

```
/solve-problem
```
Describe your problem → system finds matching concepts → you choose role → get solution.

---

## Quality Review

```
/review-quality
```
Run any gate against any artifact to check quality.

---

## Typical Session: "Clean Code" → Developer Application

```
1. /read-book
   → Paste Clean Code text
   → 23 concepts extracted
   → /suggest-roles auto-triggered

2. /suggest-roles output:
   👨‍💻 Developer (12) — SRP, meaningful names, unit tests
   🏗️ Architect (5) — separation of concerns, DI
   🧪 Tester (4) — testable design, TDD
   👔 TechLead (2) — boy scout rule, code standards

3. User selects: Developer

4. /apply-as-developer
   → Select concept: Single Responsibility Principle
   → Task: refactor existing OrderService
   → Paste code
   → Get before/after refactoring with concept citations

5. Artifact saved:
   production/applications/developer-output/clean-code_developer_srp_20260425-143000.md
```

---

## Directory Reference

| Path | Purpose |
|------|---------|
| `session-knowledge/{book_id}/` | Processed book artifacts |
| `production/role-maps/` | Role mapping JSON + Markdown |
| `production/applications/` | Application outputs by role |
| `production/decisions/` | Logged decisions |
| `production/session-logs/` | Daily session logs |
| `graph-export/` | Neo4j Cypher exports |
| `obsidian-export/` | Obsidian vault exports |

---

## Troubleshooting

**Gate failure:** Run `/review-quality`, select the failing gate, address itemized failures.

**Role-map missing:** Run `/suggest-roles` for the book before `/apply-as-*`.

**No books processed:** Run `/read-book` first.

**Context lost after compaction:** Check `production/session-state/pre-compact-snapshot.md`.

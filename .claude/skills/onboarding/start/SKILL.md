# Skill: /start

**Trigger:** `/start`
**Director:** none (onboarding)
**Purpose:** Orient the user to Book Studio, show available commands, and check system state.

---

## Steps

### Step 1: Display Welcome
Show the system overview:
```
📚 Book Studio v2.0 — Multi-Agent Reading System

You can:
  /read-book          — Process a new book (extracts, summarizes, builds mental model)
  /build-graph        — Build knowledge graph from processed book
  /export-obsidian    — Export to Obsidian vault
  /suggest-roles      — Map book concepts to professional roles (auto-runs after /read-book)
  /auto-apply         — Automatically apply best concept to best role
  /apply-as-developer — Apply book concepts as a developer
  /apply-as-architect — Apply book concepts as an architect
  /apply-as-tester    — Apply book concepts as a tester
  /apply-as-devops    — Apply book concepts as a DevOps engineer
  /apply-as-security  — Apply book concepts as a security engineer
  /compare-books      — Compare two or more books
  /synthesize-library — Synthesize your entire library
  /review-quality     — Run quality review on any artifact
  /generate-playbook  — Generate a role-specific playbook
  /solve-problem      — Solve a specific problem using book knowledge
```

### Step 2: Check Session State
Read `production/session-state/active.md`.
- If a previous session exists: show its status and ask if the user wants to resume.
- If no session: initialize new session state.

### Step 3: Check Processed Books
List any existing `session-knowledge/*/unified-knowledge.json` files.
If found: "You have {N} processed books: {list}. Use /suggest-roles or /apply-as-{role} to work with them."

### Step 4: Prompt
Ask: "What would you like to do? You can paste a book excerpt or path, or use a command above."

# Rules: Obsidian Export

Rules governing the obsidian-exporter-spec and Obsidian vault output.

## Atomicity Rules
- One concept = one note. Never combine two concepts in a single note.
- Notes must be self-contained — a reader should understand the concept without opening other notes.
- Index notes (`_index-{book_id}.md`) are the only exception to the one-concept rule.

## Frontmatter Rules
Every note must have valid YAML frontmatter:
```yaml
---
title: "string"
book: "[[book_title]]"
author: "[[author_name]]"
type: principle|pattern|technique|anti-pattern|mental-model
confidence: float
tags:
  - "#domain/name"
  - "#type"
  - "#book/book_id"
---
```
All fields are required. Missing frontmatter = OBSIDIAN-READY gate failure.

## Backlink Rules
- Backlinks must be bidirectional: if note A links to B, note B must link back to A
- Use `[[Note Name]]` syntax — exact match to the note's title field
- Related concepts section must list all `related_concepts` from unified-knowledge.json
- Book index note must link to every concept note for that book

## Tag Rules
Tag taxonomy (must be followed exactly):
- `#domain/{name}` — architecture, testing, security, devops, data, performance, observability, leadership, legacy, platform
- `#principle` / `#pattern` / `#technique` / `#anti-pattern` / `#mental-model`
- `#book/{book_id}` — e.g., `#book/clean-code`
- `#role/{role_name}` — for role-applicable concepts
- Tag names: lowercase, kebab-case only

## Content Rules
- Source quotes must be verbatim — never paraphrased in `> quote` blocks
- "How to Apply" must be actionable: verb + object + context
- Anti-pattern sections must be labeled with ⚠️ or `[anti-pattern]` marker
- File names: kebab-case, e.g., `single-responsibility-principle.md`
- Index file: `_index-{book_id}.md`
- Tags file: `_tags.md` (one entry per tag used in this book's notes)

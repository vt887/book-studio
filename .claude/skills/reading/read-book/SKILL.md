# Skill: /read-book

**Trigger:** `/read-book`
**Director:** `reading-director`
**Purpose:** Ingest a book and produce structured knowledge artifacts.

---

## Steps

### Phase 1: Input Collection
Ask user:
```
AskUserQuestion {
  "question": "Яку книгу ти хочеш обробити?",
  "options": [
    "📁 Вказати шлях до файлу (PDF/EPUB/TXT)",
    "📋 Вставити текст/уривок",
    "🔗 Вказати URL"
  ]
}
```
Also collect: book title, author, year (if not derivable from file).

### Phase 2: Generate book_id
`book_id = slugify(title)` — e.g., "Clean Code" → `clean-code`
Create directory: `session-knowledge/{book_id}/`

### Phase 3: Chunking
Agent: `reading-director`
- Split book into chunks (2000–4000 tokens, 200-token overlap)
- Tag each chunk: `{ book_id, chapter, section, chunk_index }`

### Phase 4: Parallel Extraction + Summarization
Spawn in parallel:
- `extractor-spec` → processes all chunks → `session-knowledge/{book_id}/extraction.json`
- `summarizer-spec` → processes all chunks → `session-knowledge/{book_id}/summary.json`

### Phase 5: Gate Check
Run gates in parallel:
- `[EXTRACT-QUALITY]` against `extraction.json` (threshold: 0.85)
- `[SUMMARY-QUALITY]` against `summary.json` (threshold: 0.85)

If either FAILS:
- Retry the failing specialist once with corrective context
- If still fails: surface BLOCKED verdict with itemized failures, stop

### Phase 6: Mental Model Construction
Agent: `mental-model-spec`
Input: `extraction.json` + `summary.json`
Output: `session-knowledge/{book_id}/mental-model.json`

### Phase 7: Merge to Unified Knowledge
Agent: `reading-director`
Merge extraction + summary + mental-model into:
`session-knowledge/{book_id}/unified-knowledge.json`

### Phase 8: Log + Auto-trigger
- Append to `production/session-logs/{date}.md`
- If `autoSuggestRoles: true`: automatically invoke `/suggest-roles` for this book_id

### Verdict
```
✅ COMPLETE
Book: {title} by {author}
Concepts extracted: {N}
Artifacts: session-knowledge/{book_id}/
Next: /suggest-roles (running automatically) OR /build-graph
```

# Skill: /extract-knowledge

**Trigger:** `/extract-knowledge`
**Director:** `reading-director`
**Purpose:** Re-run or deepen knowledge extraction for an already-chunked book.

---

## Steps

### Phase 1: Select Book
If multiple books processed: ask which one.
Load: `session-knowledge/{book_id}/extraction.json` if exists.

### Phase 2: Extraction Mode
```
AskUserQuestion {
  "question": "Що ти хочеш екстрагувати?",
  "options": [
    "🔄 Повна повторна екстракція",
    "➕ Додати нові концепції (incremental)",
    "🎯 Фокус на конкретній темі",
    "🔍 Глибша екстракція для певного розділу"
  ]
}
```

### Phase 3: Run extractor-spec
Agent: `extractor-spec`
- Full: process all chunks again
- Incremental: process only chunks without high-confidence concepts
- Focused: filter chunks by topic keyword, process those
- Deep: re-process specific chapter with expanded context

### Phase 4: Gate Check
Run `[EXTRACT-QUALITY]` (threshold: 0.85).
On fail: show itemized failures, ask user to confirm retry or stop.

### Phase 5: Merge
If incremental: merge new extractions into existing `extraction.json`.
Regenerate `unified-knowledge.json`.

### Verdict
```
✅ COMPLETE
New concepts: {N_new} | Updated: {N_updated} | Total: {N_total}
Artifact: session-knowledge/{book_id}/extraction.json
```

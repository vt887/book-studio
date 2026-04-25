# Skill: /compare-books

**Trigger:** `/compare-books`
**Director:** `synthesis-director`
**Purpose:** Compare two or more books to find common concepts, conflicts, and evolution chains.

---

## Steps

### Phase 1: Select Books
List available processed books from `session-knowledge/`.
Ask user to select 2 or more.

### Phase 2: Load Knowledge
Load `unified-knowledge.json` for each selected book.
Verify minimum 2 books selected.

### Phase 3: Spawn cross-book-spec
Agent: `cross-book-spec`
Input: all selected `unified-knowledge.json` files
Output:
- `synthesis/synthesis-report.json`
- `synthesis/conflicts.json`
- `synthesis/evolution-map.json`

### Phase 4: Gate Check
Run `[CROSS-BOOK-SYNC]` (threshold: 0.80).
On fail: retry with targeted corrections.

### Phase 5: Present Results
Show summary:
```
📊 Comparison: {book1} vs {book2}

Common concepts: {N}
  ✅ Consensus: {N_agree}
  ⚠️  Partial: {N_partial}
  ❌ Conflicts: {N_conflict}

Unique to {book1}: {N}
Unique to {book2}: {N}

Evolution chains: {N}
```

Show top 3 conflicts with both positions.
Ask if user wants full report or to explore specific conflict.

### Verdict
```
✅ COMPLETE
Artifacts: synthesis/synthesis-report.json, synthesis/conflicts.json, synthesis/evolution-map.json
```

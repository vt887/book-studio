# Skill: /synthesize-library

**Trigger:** `/synthesize-library`
**Director:** `synthesis-director`
**Purpose:** Build a unified knowledge model across all processed books in the library.

---

## Steps

### Phase 1: Discover All Books
Scan `session-knowledge/` for all `unified-knowledge.json` files.
Show user: "Found {N} books: {list}. Synthesizing all."

### Phase 2: Cross-Book Analysis
Agent: `cross-book-spec`
Process all books pairwise + globally.
Output:
- `synthesis/library-index.json` — global concept index
- `synthesis/synthesis-report.json` — updated with all books
- `synthesis/evolution-map.json` — concept evolution across all books

### Phase 3: Gate Check
Run `[CROSS-BOOK-SYNC]` (threshold: 0.80).

### Phase 4: Build Library Index
`library-index.json` schema:
```json
{
  "last_updated": "ISO8601",
  "book_count": 0,
  "total_concepts": 0,
  "concept_index": {
    "{concept_name}": {
      "appears_in": ["book_id_1"],
      "consensus": "agree|partial|conflict",
      "master_definition": "string"
    }
  },
  "cross_cutting_concepts": ["string"]
}
```

### Phase 5: Present Summary
```
📚 Library Synthesis Complete

Books analyzed: {N}
Total concepts: {N}
Cross-cutting concepts (appear in 3+ books): {list}
Top conflicts: {list}
```

### Verdict
```
✅ COMPLETE
Artifact: synthesis/library-index.json
```

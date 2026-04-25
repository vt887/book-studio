# Skill: /build-graph

**Trigger:** `/build-graph`
**Director:** `knowledge-director`
**Purpose:** Build a Neo4j knowledge graph from processed book knowledge.

---

## Steps

### Phase 1: Select Book
If multiple books: ask which one.
Load: `session-knowledge/{book_id}/unified-knowledge.json`
Verify file exists — if not: "Run /read-book first."

### Phase 2: Spawn graph-builder-spec
Agent: `graph-builder-spec`
Input: `unified-knowledge.json`
Output:
- `graph-export/{book_id}/cypher-statements.cypher`
- `graph-export/{book_id}/graph-schema.json`
- `graph-export/{book_id}/graph-index.json`

### Phase 3: Gate Check
Run `[GRAPH-VALID]` (threshold: 0.95).
On fail: retry graph-builder-spec with itemized corrections.

### Phase 4: Execute (optional)
```
AskUserQuestion {
  "question": "Як застосувати граф?",
  "options": [
    "📋 Показати Cypher statements (без виконання)",
    "🗃️ Зберегти до файлу (cypher-statements.cypher)",
    "🔌 Виконати в Neo4j (вкажи URL)"
  ]
}
```
If Neo4j URL provided: execute via `cypher-shell` or HTTP API.

### Phase 5: Update Index
Append this book's node IDs to `graph-export/global-index.json`.

### Verdict
```
✅ COMPLETE
Nodes: {N_nodes} | Edges: {N_edges}
Artifact: graph-export/{book_id}/cypher-statements.cypher
```

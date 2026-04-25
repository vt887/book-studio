# Rules: Knowledge Graph

Rules governing the graph-builder-spec and Neo4j output.

## Node Rules
- All nodes use MERGE (idempotent) — never CREATE without existence check
- Required properties per node type:
  - Book: id, title, author, year
  - Author: name
  - Concept: id, name, definition, type, confidence, book_id
  - Domain: name
  - Term: name, definition, book_id
- No orphan nodes — every node must have at least one edge before the transaction commits
- Concept IDs: `{book_id}_{concept_slug}` — slugs are lowercase kebab-case

## Edge Rules
- All edges use MERGE (idempotent)
- Edges must always be preceded by MATCH on both endpoints
- Required properties per edge type:
  - RELATES_TO: weight (float), description (string)
  - APPLIES_TO: weight (float)
  - CONTRADICTS: evidence (string)
  - EVOLVED_FROM: year_delta (integer)
  - AUTHORED_BY: year (integer)
  - CONTAINS: chapter (string)
  - APPLICABLE_AS: relevance (float), primary (boolean)
- All float properties: range [0.0, 1.0]
- Role names in APPLICABLE_AS edges must match settings.json available_roles exactly

## Cypher Output Rules
- Batch statements in groups of 50 per transaction block
- Section comments required: `// === BOOK NODES ===`, `// === CONCEPT NODES ===`, etc.
- Final output must pass `GRAPH-VALID` gate (threshold: 0.95)
- graph-index.json maps book_id → list of concept node IDs in this book

## Cross-Book Rules
- When a concept appears in multiple books: create a RELATES_TO edge between the two concept nodes
- Contradicting concepts from different books: create a CONTRADICTS edge with evidence from both books

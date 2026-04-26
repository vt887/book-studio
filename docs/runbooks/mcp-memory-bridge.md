# Lean-ctx MCP Memory Bridge

Production-ready minimal memory operating layer for multi-agent AI workflows.

## Components

- FastAPI service: `mcp_bridge` (stateless API layer)
- Postgres + pgvector: canonical semantic concept memory
- Redis: query cache + session memory (ephemeral)
- Neo4j: concept graph links only

## API Endpoints

- `GET /health`
- `GET /live`
- `GET /ready`
- `POST /ctx/read`
- `POST /ctx/write`
- `POST /ctx/graph/link`
- `GET /mcp/tools`
- `POST /mcp/call`

## Start

```bash
docker compose up -d --build
```

### Start with rollout flags

Use env vars to control retrieval/quality rollout safely:

```bash
RETRIEVAL_V2_ENABLED=true \
QUERY_EXPANSION_RETRY_ENABLED=true \
QUALITY_GATE_ENABLED=true \
QUALITY_GATE_ENFORCE=false \
QUALITY_THRESHOLD=0.80 \
docker compose up -d --build mcp_bridge
```

Suggested rollout path:

1. `QUALITY_GATE_ENFORCE=false` (audit mode)
2. Scan 1-2 books and inspect `/quality/evaluate`
3. Switch to `QUALITY_GATE_ENFORCE=true`

Check readiness:

```bash
curl -s http://localhost:8080/live
curl -s http://localhost:8080/ready
```

If Neo4j remains in `Waiting`, re-evaluate health and logs:

```bash
docker compose ps
docker compose logs neo4j --tail=200
```

Neo4j container healthcheck uses HTTP listener probe (`:7474`) to avoid long Bolt/plugin startup hangs.
Application-level Neo4j readiness is still validated in `GET /ready` via Bolt query.

## MCP Tool Definitions

```json
[
  {
    "name": "ctx_read",
    "input": {
      "query": "string",
      "top_k": "number",
      "role": "string?"
    },
    "output": {
      "source": "cache|postgres",
      "results": "array"
    }
  },
  {
    "name": "ctx_write",
    "input": {
      "book_id": "string",
      "data": {
        "concepts": "array"
      }
    }
  },
  {
    "name": "ctx_graph_link",
    "input": {
      "from_id": "string",
      "to_id": "string",
      "relation": "string",
      "weight": "float"
    }
  }
]
```

## Minimal Usage Examples

1) Ingest concepts

```bash
curl -s http://localhost:8080/ctx/write \
  -H 'Content-Type: application/json' \
  -d '{
    "book_id": "clean-code",
    "data": {
      "concepts": [
        {
          "concept_id": "cc-srp",
          "name": "Single Responsibility Principle",
          "definition": "A module should have one reason to change.",
          "summary": "Separates concerns to reduce coupling.",
          "tags": ["design", "maintainability"],
          "applicable_roles": ["developer", "architect"]
        }
      ]
    }
  }'
```

2) Read memory

```bash
curl -s http://localhost:8080/ctx/read \
  -H 'Content-Type: application/json' \
  -d '{"query":"how to reduce coupling","top_k":5,"role":"developer"}'
```

2.1) Write chunks for grounding

```bash
curl -s http://localhost:8080/chunks/write \
  -H 'Content-Type: application/json' \
  -d '{
    "chunks": [
      {
        "chunk_id": "clean-code-ch-001",
        "book_id": "clean-code",
        "text_hash": "e3b0c44298fc1c14",
        "text_content": "Functions should do one thing."
      }
    ]
  }'
```

3) Link graph concepts

```bash
curl -s http://localhost:8080/ctx/graph/link \
  -H 'Content-Type: application/json' \
  -d '{"from_id":"cc-srp","to_id":"cc-ocp","relation":"supports","weight":0.84}'
```

4) MCP-style tool call

```bash
curl -s http://localhost:8080/mcp/call \
  -H 'Content-Type: application/json' \
  -d '{
    "tool": "ctx_read",
    "arguments": {"query": "clean abstractions", "top_k": 3}
  }'
```

5) Evaluate quality for scanned concepts

By `book_id`:

```bash
curl -s http://localhost:8080/quality/evaluate \
  -H 'Content-Type: application/json' \
  -d '{"book_id":"clean-code"}'
```

By explicit concept IDs:

```bash
curl -s http://localhost:8080/quality/evaluate \
  -H 'Content-Type: application/json' \
  -d '{
    "book_id":"clean-code",
    "concept_ids":["cc-srp","cc-ocp"]
  }'
```

Check graph consistency for one concept:

```bash
curl -s http://localhost:8080/quality/consistency/cc-srp
```

## Determinism and Performance Notes

- Deterministic embeddings by SHA-256 token projection (same input -> same vector)
- Stable ordering by `(distance, concept_id)` to avoid random ties
- Cache key: `ctx:{query_hash}:{role}:{top_k}`
- Cached reads return in one Redis roundtrip
- Uncached reads use one Postgres query after embedding build
- Startup includes retry with backoff for Postgres, Redis, and Neo4j

## Latency Benchmark

Run quick benchmark for cached vs uncached reads:

```bash
python3 benchmark_ctx_read.py --base-url http://localhost:8080 --cached-runs 30 --uncached-runs 30
```

Targets:
- cached p95 < 200 ms
- uncached p95 < 500 ms

## Operational Checklist (Single Book)

Use this short flow to scan one book from ingestion to quality pass.

1) Start stack in audit mode

```bash
RETRIEVAL_V2_ENABLED=true \
QUERY_EXPANSION_RETRY_ENABLED=true \
QUALITY_GATE_ENABLED=true \
QUALITY_GATE_ENFORCE=false \
QUALITY_THRESHOLD=0.80 \
docker compose up -d --build mcp_bridge
```

2) Verify readiness

```bash
curl -s http://localhost:8080/ready
curl -s http://localhost:8080/cache/stats
```

3) Ingest chunks (`chunk_id`, `text_hash`, `book_id`)

```bash
curl -s http://localhost:8080/chunks/write \
  -H 'Content-Type: application/json' \
  -d '{"chunks":[{"chunk_id":"book-ch-001","book_id":"my-book","text_hash":"abc123","text_content":"..."}]}'
```

4) Ingest concepts (`ctx_write`) with grounding

```bash
curl -s http://localhost:8080/ctx/write \
  -H 'Content-Type: application/json' \
  -d '{"book_id":"my-book","data":{"concepts":[{"concept_id":"c-1","name":"...","definition":"...","summary":"...","importance_score":0.8,"source_chunks":["book-ch-001"],"tags":["..."],"applicable_roles":["developer"]}]}}'
```

5) Read role-aware memory (`ctx_read`) and confirm cache behavior

```bash
curl -s http://localhost:8080/ctx/read -H 'Content-Type: application/json' -d '{"query":"...","top_k":5,"role":"developer"}'
curl -s http://localhost:8080/ctx/read -H 'Content-Type: application/json' -d '{"query":"...","top_k":5,"role":"developer"}'
```

Expected: first call `source=postgres`, second call `source=cache`.

6) Link graph relations

```bash
curl -s http://localhost:8080/ctx/graph/link \
  -H 'Content-Type: application/json' \
  -d '{"from_id":"c-1","to_id":"c-2","relation":"supports","weight":0.9}'
```

7) Evaluate quality

```bash
curl -s http://localhost:8080/quality/evaluate -H 'Content-Type: application/json' -d '{"book_id":"my-book"}'
curl -s http://localhost:8080/quality/consistency/c-1
```

8) Move from audit to enforce mode

After quality is stable, restart with:

```bash
QUALITY_GATE_ENFORCE=true docker compose up -d --build mcp_bridge
```

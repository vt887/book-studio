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

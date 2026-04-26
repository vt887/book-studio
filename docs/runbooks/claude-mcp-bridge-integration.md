# Claude + mcp_bridge Integration

This runbook shows how to connect `mcp_bridge` to Claude as an MCP tool server
and use it during book scanning (`/read-book`, `/extract-knowledge`).

## 1) Prerequisites

- `mcp_bridge` is running locally: `http://localhost:8080`
- Bridge is healthy:

```bash
curl -s http://localhost:8080/ready
```

Expected: `"status":"ready"` and `postgres=true`, `redis=true`.

Install adapter dependency locally (outside docker image):

```bash
pip install -r requirements-mcp-adapter.txt
```

## 2) Adapter server (stdio MCP)

Adapter file:

- `scripts/claude_mcp_bridge_server.py`

It exposes these tools to Claude:

- `bridge_health`
- `ctx_read(query, top_k, role?)`
- `ctx_write(book_id, data)`
- `ctx_graph_link(from_id, to_id, relation, weight)`

## 3) Add server to Claude

Use one of these methods.

### Option A: Claude Code CLI (recommended)

```bash
claude mcp add book-studio-memory-bridge \
  --env MCP_BRIDGE_BASE_URL=http://localhost:8080 \
  -- python3 /Users/tymoshv/MyPetProjects/book-studio/scripts/claude_mcp_bridge_server.py
```

Then verify in Claude Code:

```bash
/mcp
```

You should see `book-studio-memory-bridge` in connected servers.

### Option B: Claude Desktop config JSON

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "book-studio-memory-bridge": {
      "command": "python3",
      "args": [
        "/Users/tymoshv/MyPetProjects/book-studio/scripts/claude_mcp_bridge_server.py"
      ],
      "env": {
        "MCP_BRIDGE_BASE_URL": "http://localhost:8080",
        "MCP_BRIDGE_TIMEOUT": "15"
      }
    }
  }
}
```

Restart Claude Desktop after config changes.

## 4) Use during book scanning

Recommended pattern for `/read-book` and `/extract-knowledge`:

1. **After each chunk extraction**: push concepts with `ctx_write`.
2. **Before processing next chunk**: query prior knowledge with `ctx_read`.
3. **After section/chapter synthesis**: link related concepts with `ctx_graph_link`.
4. **During role-specific application**: use `ctx_read(..., role="developer")` (or another role).

## 5) Minimal usage examples in prompts

Example instruction to Claude while reading a book:

```text
For each processed chapter:
1) Save extracted concepts via ctx_write(book_id=<book>, data={concepts:[...]})
2) Fetch supporting memory via ctx_read(query=<chapter summary>, top_k=5, role="developer")
3) Add strong concept relations via ctx_graph_link(...)
```

## 6) Troubleshooting

- If tools are visible but calls fail, run:

```bash
python3 functional_test_mcp_bridge.py --base-url http://localhost:8080
```

- If Claude cannot connect to adapter:
  - verify path to `scripts/claude_mcp_bridge_server.py`
  - check `python3` is available in Claude environment
  - confirm `MCP_BRIDGE_BASE_URL` points to reachable host

- If readiness is flaky:

```bash
curl -s http://localhost:8080/ready
curl -s http://localhost:8080/health
```

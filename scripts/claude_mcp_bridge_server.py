#!/usr/bin/env python3
"""MCP stdio adapter for the local mcp_bridge HTTP service.

This server exposes bridge endpoints as MCP tools so Claude can call them
directly during reading/extraction workflows.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib import request

from mcp.server.fastmcp import FastMCP


BASE_URL = os.environ.get("MCP_BRIDGE_BASE_URL", "http://localhost:8080").rstrip("/")
TIMEOUT_SECONDS = float(os.environ.get("MCP_BRIDGE_TIMEOUT", "15"))
NO_PROXY_OPENER = request.build_opener(request.ProxyHandler({}))

mcp = FastMCP("book-studio-memory-bridge")


def _http_json(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = request.Request(url=url, data=data, headers=headers, method=method)
    with NO_PROXY_OPENER.open(req, timeout=TIMEOUT_SECONDS) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


@mcp.tool()
def bridge_health() -> dict[str, Any]:
    """Return health/readiness snapshot for mcp_bridge."""
    ready = _http_json("GET", "/ready")
    health = _http_json("GET", "/health")
    return {"base_url": BASE_URL, "ready": ready, "health": health}


@mcp.tool()
def ctx_read(query: str, top_k: int = 5, role: str | None = None) -> dict[str, Any]:
    """Read semantic memory from mcp_bridge with optional role filtering."""
    payload: dict[str, Any] = {"query": query, "top_k": top_k}
    if role:
        payload["role"] = role
    return _http_json("POST", "/ctx/read", payload)


@mcp.tool()
def ctx_write(book_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Write extracted concepts to semantic memory for a book."""
    payload = {"book_id": book_id, "data": data}
    return _http_json("POST", "/ctx/write", payload)


@mcp.tool()
def ctx_graph_link(from_id: str, to_id: str, relation: str, weight: float) -> dict[str, Any]:
    """Create/update a concept relation in graph memory."""
    payload = {
        "from_id": from_id,
        "to_id": to_id,
        "relation": relation,
        "weight": weight,
    }
    return _http_json("POST", "/ctx/graph/link", payload)


if __name__ == "__main__":
    mcp.run()

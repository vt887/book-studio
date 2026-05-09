from mcp_bridge.main import ctx_graph_link, ctx_read, ctx_write


TOOLS = [
    {
        "name": "ctx_read",
        "description": "Deterministic semantic memory retrieval with role filtering",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 50},
                "role": {"type": "string"},
            },
            "required": ["query", "top_k"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "enum": ["cache", "postgres"]},
                "results": {"type": "array"},
            },
            "required": ["source", "results"],
        },
        "handler": ctx_read,
    },
    {
        "name": "ctx_write",
        "description": "Ingest structured concept memory into canonical semantic store",
        "input_schema": {
            "type": "object",
            "properties": {
                "book_id": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "concepts": {"type": "array"},
                    },
                    "required": ["concepts"],
                },
            },
            "required": ["book_id", "data"],
        },
        "handler": ctx_write,
    },
    {
        "name": "ctx_graph_link",
        "description": "Create or update concept relationship in graph memory",
        "input_schema": {
            "type": "object",
            "properties": {
                "from_id": {"type": "string"},
                "to_id": {"type": "string"},
                "relation": {"type": "string"},
                "weight": {"type": "number", "minimum": 0, "maximum": 1},
            },
            "required": ["from_id", "to_id", "relation", "weight"],
        },
        "handler": ctx_graph_link,
    },
]

from contextlib import asynccontextmanager
import asyncio
from typing import Any

from fastapi import FastAPI, HTTPException
from redis.asyncio import Redis

from mcp_bridge import cache, db
from mcp_bridge.config import settings
from mcp_bridge.embedding import deterministic_embedding
from mcp_bridge.graph import Neo4jStore
from mcp_bridge.models import (
    CtxGraphLinkRequest,
    CtxGraphLinkResponse,
    CtxReadRequest,
    CtxReadResponse,
    CtxWriteRequest,
    CtxWriteResponse,
    HealthResponse,
    ToolCallRequest,
    ToolCallResponse,
)


async def _retry_async(fn, name: str, attempts: int = 8, base_delay: float = 0.25, max_delay: float = 3.0):
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            return await fn()
        except Exception as exc:
            last_error = exc
            if attempt == attempts:
                break
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            await asyncio.sleep(delay)
    raise RuntimeError(f"{name} not available after {attempts} attempts") from last_error


@asynccontextmanager
async def lifespan(app: FastAPI):
    pg_pool = await _retry_async(
        lambda: db.init_pg_pool(settings.pg_dsn),
        name="postgres",
    )

    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    await _retry_async(redis_client.ping, name="redis")

    graph = Neo4jStore(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)

    neo4j_online = True
    try:
        await _retry_async(graph.healthcheck, name="neo4j", attempts=12, base_delay=0.5)
        await _retry_async(graph.ensure_indexes, name="neo4j-indexes", attempts=12, base_delay=0.5)
    except Exception:
        neo4j_online = False

    app.state.pg_pool = pg_pool
    app.state.redis = redis_client
    app.state.graph = graph
    app.state.neo4j_online = neo4j_online

    try:
        yield
    finally:
        await pg_pool.close()
        await redis_client.close()
        await graph.close()


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status_endpoint": "/ready",
        "health_endpoint": "/health",
    }


@app.get("/live")
async def live() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/ready")
async def ready() -> dict[str, Any]:
    required_checks = {
        "postgres": False,
        "redis": False,
    }
    optional_checks = {
        "neo4j": False,
    }

    checks = {
        "postgres": False,
        "redis": False,
        "neo4j": False,
    }
    try:
        checks["postgres"] = await db.healthcheck(app.state.pg_pool)
        required_checks["postgres"] = checks["postgres"]
    except Exception:
        checks["postgres"] = False
        required_checks["postgres"] = False

    try:
        checks["redis"] = bool(await app.state.redis.ping())
        required_checks["redis"] = checks["redis"]
    except Exception:
        checks["redis"] = False
        required_checks["redis"] = False

    try:
        checks["neo4j"] = bool(app.state.neo4j_online) and await app.state.graph.healthcheck()
        optional_checks["neo4j"] = checks["neo4j"]
    except Exception:
        checks["neo4j"] = False
        optional_checks["neo4j"] = False

    ready_status = all(required_checks.values())

    return {
        "status": "ready" if ready_status else "not_ready",
        "checks": checks,
        "required_checks": required_checks,
        "optional_checks": optional_checks,
    }


async def _ctx_read_logic(request: CtxReadRequest) -> CtxReadResponse:
    cached = await cache.get_cached_results(
        app.state.redis,
        request.query,
        request.role,
        request.top_k,
    )
    if cached is not None:
        return CtxReadResponse(source="cache", results=cached)

    embedding = deterministic_embedding(request.query, settings.embedding_dim)
    rows = await db.semantic_search(
        app.state.pg_pool,
        query_embedding=embedding,
        top_k=request.top_k,
        role=request.role,
    )

    await cache.set_cached_results(
        app.state.redis,
        request.query,
        request.role,
        request.top_k,
        rows,
        settings.cache_ttl_seconds,
    )
    return CtxReadResponse(source="postgres", results=rows)


async def _ctx_write_logic(request: CtxWriteRequest) -> CtxWriteResponse:
    if not request.data.concepts:
        raise HTTPException(status_code=400, detail="data.concepts cannot be empty")

    normalized = []
    for concept in request.data.concepts:
        emb = concept.embedding
        if not emb:
            emb = deterministic_embedding(
                f"{concept.name} {concept.definition} {concept.summary}",
                settings.embedding_dim,
            )
        if len(emb) != settings.embedding_dim:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid embedding dimension for concept_id={concept.concept_id}; expected {settings.embedding_dim}",
            )
        normalized.append(
            {
                "concept_id": concept.concept_id,
                "name": concept.name,
                "definition": concept.definition,
                "summary": concept.summary,
                "embedding": emb,
                "tags": concept.tags,
                "applicable_roles": concept.applicable_roles,
            }
        )

    inserted, updated = await db.upsert_concepts(app.state.pg_pool, request.book_id, normalized)
    await cache.set_session_memory(
        app.state.redis,
        session_id=request.book_id,
        data={"book_id": request.book_id, "concepts_count": len(normalized)},
        ttl_seconds=settings.session_ttl_seconds,
    )
    return CtxWriteResponse(status="ok", inserted=inserted, updated=updated)


async def _ctx_graph_link_logic(request: CtxGraphLinkRequest) -> CtxGraphLinkResponse:
    relation = request.relation.strip().lower()
    if not relation:
        raise HTTPException(status_code=400, detail="relation cannot be empty")

    await app.state.graph.link_concepts(
        from_id=request.from_id,
        to_id=request.to_id,
        relation=relation,
        weight=request.weight,
    )

    return CtxGraphLinkResponse(
        status="ok",
        relation=relation,
        from_id=request.from_id,
        to_id=request.to_id,
        weight=request.weight,
    )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    checks = {
        "postgres": False,
        "redis": False,
        "neo4j": False,
    }

    try:
        checks["postgres"] = await db.healthcheck(app.state.pg_pool)
    except Exception:
        checks["postgres"] = False

    try:
        checks["redis"] = bool(await app.state.redis.ping())
    except Exception:
        checks["redis"] = False

    try:
        checks["neo4j"] = await app.state.graph.healthcheck()
    except Exception:
        checks["neo4j"] = False

    status = "ok" if all(checks.values()) else "degraded"
    return HealthResponse(status=status, checks=checks)


@app.post("/ctx/read", response_model=CtxReadResponse)
async def ctx_read(request: CtxReadRequest) -> CtxReadResponse:
    return await _ctx_read_logic(request)


@app.post("/ctx/write", response_model=CtxWriteResponse)
async def ctx_write(request: CtxWriteRequest) -> CtxWriteResponse:
    return await _ctx_write_logic(request)


@app.post("/ctx/graph/link", response_model=CtxGraphLinkResponse)
async def ctx_graph_link(request: CtxGraphLinkRequest) -> CtxGraphLinkResponse:
    if not app.state.neo4j_online:
        raise HTTPException(status_code=503, detail="neo4j not ready")
    return await _ctx_graph_link_logic(request)


@app.get("/mcp/tools")
async def mcp_tools() -> dict[str, Any]:
    return {
        "tools": [
            {
                "name": "ctx_read",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "top_k": {"type": "integer", "minimum": 1, "maximum": 50},
                        "role": {"type": "string"},
                    },
                    "required": ["query", "top_k"],
                },
            },
            {
                "name": "ctx_write",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "book_id": {"type": "string"},
                        "data": {"type": "object"},
                    },
                    "required": ["book_id", "data"],
                },
            },
            {
                "name": "ctx_graph_link",
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
            },
        ]
    }


@app.post("/mcp/call", response_model=ToolCallResponse)
async def mcp_call(request: ToolCallRequest) -> ToolCallResponse:
    if request.tool == "ctx_read":
        result = await _ctx_read_logic(CtxReadRequest(**request.arguments))
    elif request.tool == "ctx_write":
        result = await _ctx_write_logic(CtxWriteRequest(**request.arguments))
    elif request.tool == "ctx_graph_link":
        result = await _ctx_graph_link_logic(CtxGraphLinkRequest(**request.arguments))
    else:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {request.tool}")

    return ToolCallResponse(tool=request.tool, result=result.model_dump())

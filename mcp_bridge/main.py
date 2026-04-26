from contextlib import asynccontextmanager
import asyncio
import time
from typing import Any

from fastapi import FastAPI, HTTPException
from redis.asyncio import Redis

from mcp_bridge import cache, db
from mcp_bridge.config import settings
from mcp_bridge.embedding import deterministic_embedding
from mcp_bridge.graph import Neo4jStore
from mcp_bridge.models import (
    ChunkWriteRequest,
    ChunkWriteResponse,
    CacheInvalidateRequest,
    CacheInvalidateResponse,
    CacheStatsResponse,
    CtxGraphLinkRequest,
    CtxGraphLinkResponse,
    CtxReadRequest,
    CtxReadResponse,
    CtxWriteRequest,
    CtxWriteResponse,
    HealthResponse,
    QualityEvaluateItem,
    QualityEvaluateRequest,
    QualityEvaluateResponse,
    ToolCallRequest,
    ToolCallResponse,
)
from mcp_bridge import quality


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
    await _retry_async(lambda: db.ensure_schema(pg_pool), name="postgres-schema")

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
    start = time.perf_counter()
    filters = "none"

    redis_available = True
    retrieval_model_version = f"{settings.embedding_model_version}:{settings.retrieval_version}"
    try:
        cached = await cache.get_cached_results(
            app.state.redis,
            query=request.query,
            top_k=request.top_k,
            role=request.role,
            filters=filters,
            model_version=retrieval_model_version,
            cache_version=settings.cache_version,
        )
    except Exception:
        cached = None
        redis_available = False

    if cached is not None:
        cache_key, envelope = cached
        return CtxReadResponse(
            source="cache",
            results=envelope.get("data", []),
            cache_hit=True,
            cache_key=cache_key,
            latency_ms=(time.perf_counter() - start) * 1000.0,
        )

    top_k = max(3, min(request.top_k, settings.retrieval_top_k_max))

    semantic_key = cache.make_cache_key(
        layer="l1",
        domain="semantic",
        query=request.query,
        top_k=top_k,
        role=request.role,
        filters=filters,
        model_version=retrieval_model_version,
        version=settings.cache_version,
    )

    def _insufficient(rows: list[dict[str, Any]]) -> bool:
        if len(rows) < 3:
            return True
        best_score = float(rows[0].get("score", 0.0)) if rows else 0.0
        return best_score < 0.45

    async def _search_with_query(query_text: str, requested_top_k: int) -> list[dict[str, Any]]:
        emb_from_cache = False
        embedding_start = time.perf_counter()

        embedding = None
        if redis_available:
            try:
                emb_cached = await cache.get_cached_embedding(
                    app.state.redis,
                    query=query_text,
                    model_version=retrieval_model_version,
                    cache_version=settings.cache_version,
                )
                if emb_cached is not None:
                    _, embedding = emb_cached
                    emb_from_cache = True
            except Exception:
                emb_from_cache = False

        if embedding is None:
            embedding = deterministic_embedding(query_text, settings.embedding_dim)
            if redis_available:
                try:
                    await cache.set_cached_embedding(
                        app.state.redis,
                        query=query_text,
                        model_version=retrieval_model_version,
                        cache_version=settings.cache_version,
                        embedding=embedding,
                        ttl_seconds=settings.embedding_cache_ttl_seconds,
                        latency_ms=(time.perf_counter() - embedding_start) * 1000.0,
                    )
                except Exception:
                    pass

        cache.stats.postgres_calls += 1
        rows = await db.semantic_search(
            app.state.pg_pool,
            query_embedding=embedding,
            top_k=max(requested_top_k, settings.retrieval_candidate_pool),
            role=request.role,
        )

        if settings.retrieval_v2_enabled:
            for row in rows:
                row["score"] = cache.composite_score(row, request.role)
            rows.sort(key=lambda x: (-float(x.get("score", 0.0)), x.get("concept_id", "")))
        return rows[:requested_top_k]

    async def produce_rows() -> tuple[list[dict[str, Any]], bool]:
        emb_from_cache = False
        rows = await _search_with_query(request.query, top_k)

        if settings.query_expansion_retry_enabled and _insufficient(rows):
            expanded_query = f"{request.query} architecture implementation patterns"
            retry_top_k = min(settings.retrieval_top_k_max, top_k + 2)
            retry_rows = await _search_with_query(expanded_query, retry_top_k)
            if retry_rows:
                rows = retry_rows

        return rows, emb_from_cache

    rows, emb_from_cache = await cache.get_or_create(semantic_key, produce_rows)

    if redis_available:
        try:
            await cache.set_cached_results(
                app.state.redis,
                query=request.query,
                top_k=top_k,
                role=request.role,
                filters=filters,
                model_version=retrieval_model_version,
                cache_version=settings.cache_version,
                rows=rows,
                ttl_seconds=settings.role_cache_ttl_seconds if request.role else settings.cache_ttl_seconds,
                latency_ms=(time.perf_counter() - start) * 1000.0,
            )
        except Exception:
            pass

    return CtxReadResponse(
        source="postgres",
        results=rows,
        cache_hit=False,
        cache_key=semantic_key,
        latency_ms=(time.perf_counter() - start) * 1000.0,
    )


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
                "importance_score": concept.importance_score,
                "source_chunks": concept.source_chunks,
                "embedding": emb,
                "tags": concept.tags,
                "applicable_roles": concept.applicable_roles,
            }
        )

    if settings.quality_gate_enabled:
        for item in normalized:
            q = await quality.score_concept_quality(app.state.pg_pool, item)
            if settings.quality_gate_enforce and q["quality_score"] < settings.quality_threshold:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Concept quality below threshold for concept_id={item['concept_id']}; "
                        f"quality_score={q['quality_score']:.3f}, threshold={settings.quality_threshold:.2f}"
                    ),
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
    if relation not in {"supports", "contrasts", "extends", "depends_on"}:
        raise HTTPException(status_code=400, detail="invalid relation type")

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


@app.get("/cache/stats", response_model=CacheStatsResponse)
async def cache_stats() -> CacheStatsResponse:
    return CacheStatsResponse(**cache.cache_stats())


@app.post("/cache/invalidate", response_model=CacheInvalidateResponse)
async def cache_invalidate(request: CacheInvalidateRequest) -> CacheInvalidateResponse:
    deleted = await cache.invalidate_pattern(app.state.redis, request.pattern)
    return CacheInvalidateResponse(status="ok", pattern=request.pattern, deleted=deleted)


@app.post("/chunks/write", response_model=ChunkWriteResponse)
async def chunks_write(request: ChunkWriteRequest) -> ChunkWriteResponse:
    if not request.chunks:
        raise HTTPException(status_code=400, detail="chunks cannot be empty")
    payload = [
        {
            "chunk_id": c.chunk_id,
            "book_id": c.book_id,
            "text_hash": c.text_hash,
            "text_content": c.text_content,
        }
        for c in request.chunks
    ]
    inserted, updated = await db.upsert_chunks(app.state.pg_pool, payload)
    return ChunkWriteResponse(status="ok", inserted=inserted, updated=updated)


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


@app.get("/quality/consistency/{concept_id}")
async def quality_consistency(concept_id: str) -> dict[str, Any]:
    if not app.state.neo4j_online:
        raise HTTPException(status_code=503, detail="neo4j not ready")
    rel = await app.state.graph.relation_types_for(concept_id)
    score = quality.relation_consistency_score(rel)
    return {
        "concept_id": concept_id,
        "consistency_score": score,
        "targets": len(rel),
    }


@app.post("/quality/evaluate", response_model=QualityEvaluateResponse)
async def quality_evaluate(request: QualityEvaluateRequest) -> QualityEvaluateResponse:
    concepts = await db.get_concepts_for_quality(
        app.state.pg_pool,
        book_id=request.book_id,
        concept_ids=request.concept_ids,
    )

    items: list[QualityEvaluateItem] = []
    valid_count = 0

    for concept in concepts:
        q = await quality.score_concept_quality(app.state.pg_pool, concept)
        valid = q["quality_score"] >= settings.quality_threshold
        if valid:
            valid_count += 1
        items.append(
            QualityEvaluateItem(
                concept_id=concept["concept_id"],
                grounding_score=q["grounding_score"],
                completeness_score=q["completeness_score"],
                consistency_score=q["consistency_score"],
                quality_score=q["quality_score"],
                valid=valid,
            )
        )

    total = len(items)
    return QualityEvaluateResponse(
        status="ok",
        threshold=settings.quality_threshold,
        total=total,
        valid_count=valid_count,
        invalid_count=total - valid_count,
        items=items,
    )


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

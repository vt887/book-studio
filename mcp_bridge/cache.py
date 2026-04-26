import asyncio
import hashlib
import json
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from redis.asyncio import Redis


ROLES = {
    "architect",
    "developer",
    "researcher",
    "summarizer",
    "graph-builder",
    "global",
}


@dataclass
class CacheStats:
    redis_hits: int = 0
    redis_misses: int = 0
    postgres_calls: int = 0
    embedding_hits: int = 0
    embedding_misses: int = 0
    coalesced_waiters: int = 0
    latency_samples: int = 0
    latency_total_ms: float = 0.0


stats = CacheStats()


def _safe_role(role: str | None) -> str:
    value = (role or "global").strip().lower()
    if value in ROLES:
        return value
    return "global"


def _hash_material(query: str, top_k: int, role: str, filters: str, model_version: str) -> str:
    raw = f"{query.strip().lower()}|{top_k}|{filters}|{role}|{model_version}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:8]


def make_cache_key(
    *,
    layer: str,
    domain: str,
    query: str,
    top_k: int,
    role: str | None,
    filters: str,
    model_version: str,
    version: str,
) -> str:
    role_value = _safe_role(role)
    h = _hash_material(query, top_k, role_value, filters, model_version)
    return f"ctx:{layer}:{domain}:{h}:{role_value}:{version}"


def make_embedding_key(query: str, model_version: str, version: str) -> str:
    h = hashlib.md5(f"{query.strip().lower()}|{model_version}".encode("utf-8")).hexdigest()[:8]
    return f"ctx:l1:embedding:{h}:global:{version}"


def _serialize_envelope(
    *,
    source: str,
    latency_ms: float,
    data: list[dict[str, Any]] | list[float],
    ttl: int,
    role: str,
    model: str,
    tokens_saved: int = 0,
) -> str:
    payload = {
        "timestamp": int(time.time()),
        "ttl": ttl,
        "source": source,
        "latency_ms": round(latency_ms, 3),
        "data": data,
        "metadata": {
            "model": model,
            "role": role,
            "tokens_saved": tokens_saved,
        },
    }
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=True)


def _deserialize_envelope(value: str) -> dict[str, Any]:
    parsed = json.loads(value)
    if isinstance(parsed, dict) and "data" in parsed:
        return parsed
    # Backward compatibility with old plain list payloads.
    return {
        "timestamp": int(time.time()),
        "ttl": 0,
        "source": "cache",
        "latency_ms": 0.0,
        "data": parsed,
        "metadata": {},
    }


async def get_cache_envelope(redis: Redis, key: str) -> dict[str, Any] | None:
    value = await redis.get(key)
    if not value:
        stats.redis_misses += 1
        return None
    stats.redis_hits += 1
    return _deserialize_envelope(value)


async def set_cache_envelope(
    redis: Redis,
    *,
    key: str,
    source: str,
    latency_ms: float,
    data: list[dict[str, Any]] | list[float],
    ttl_seconds: int,
    role: str,
    model: str,
    tokens_saved: int = 0,
) -> None:
    payload = _serialize_envelope(
        source=source,
        latency_ms=latency_ms,
        data=data,
        ttl=ttl_seconds,
        role=role,
        model=model,
        tokens_saved=tokens_saved,
    )
    await redis.setex(key, ttl_seconds, payload)


async def get_cached_results(
    redis: Redis,
    *,
    query: str,
    top_k: int,
    role: str | None,
    filters: str,
    model_version: str,
    cache_version: str,
) -> tuple[str, dict[str, Any]] | None:
    key = make_cache_key(
        layer="l1",
        domain="semantic",
        query=query,
        top_k=top_k,
        role=role,
        filters=filters,
        model_version=model_version,
        version=cache_version,
    )
    envelope = await get_cache_envelope(redis, key)
    if envelope is None:
        return None
    return key, envelope


async def set_cached_results(
    redis: Redis,
    *,
    query: str,
    top_k: int,
    role: str | None,
    filters: str,
    model_version: str,
    cache_version: str,
    rows: list[dict[str, Any]],
    ttl_seconds: int,
    latency_ms: float,
) -> str:
    key = make_cache_key(
        layer="l1",
        domain="semantic",
        query=query,
        top_k=top_k,
        role=role,
        filters=filters,
        model_version=model_version,
        version=cache_version,
    )
    await set_cache_envelope(
        redis,
        key=key,
        source="postgres",
        latency_ms=latency_ms,
        data=rows,
        ttl_seconds=ttl_seconds,
        role=_safe_role(role),
        model=model_version,
        tokens_saved=0,
    )
    return key


async def get_cached_embedding(
    redis: Redis,
    *,
    query: str,
    model_version: str,
    cache_version: str,
) -> tuple[str, list[float]] | None:
    key = make_embedding_key(query, model_version, cache_version)
    envelope = await get_cache_envelope(redis, key)
    if envelope is None:
        stats.embedding_misses += 1
        return None
    stats.embedding_hits += 1
    data = envelope.get("data")
    if isinstance(data, list):
        return key, [float(v) for v in data]
    return None


async def set_cached_embedding(
    redis: Redis,
    *,
    query: str,
    model_version: str,
    cache_version: str,
    embedding: list[float],
    ttl_seconds: int,
    latency_ms: float,
) -> str:
    key = make_embedding_key(query, model_version, cache_version)
    await set_cache_envelope(
        redis,
        key=key,
        source="computed",
        latency_ms=latency_ms,
        data=embedding,
        ttl_seconds=ttl_seconds,
        role="global",
        model=model_version,
        tokens_saved=0,
    )
    return key


async def set_session_memory(redis: Redis, session_id: str, data: dict, ttl_seconds: int) -> None:
    key = f"session:{session_id}"
    await redis.setex(key, ttl_seconds, json.dumps(data, separators=(",", ":"), ensure_ascii=True))


in_flight: dict[str, asyncio.Task] = {}
in_flight_lock = asyncio.Lock()


@asynccontextmanager
async def record_latency(start_perf: float):
    try:
        yield
    finally:
        elapsed = (time.perf_counter() - start_perf) * 1000.0
        stats.latency_samples += 1
        stats.latency_total_ms += elapsed


async def get_or_create(key: str, producer):
    async with in_flight_lock:
        existing = in_flight.get(key)
        if existing is not None:
            stats.coalesced_waiters += 1
            task = existing
        else:
            task = asyncio.create_task(producer())
            in_flight[key] = task

    try:
        return await task
    finally:
        async with in_flight_lock:
            if in_flight.get(key) is task:
                del in_flight[key]


def cache_stats() -> dict[str, Any]:
    total = stats.redis_hits + stats.redis_misses
    hit_rate = (stats.redis_hits / total) if total else 0.0
    miss_rate = (stats.redis_misses / total) if total else 0.0
    emb_total = stats.embedding_hits + stats.embedding_misses
    embedding_reuse_rate = (stats.embedding_hits / emb_total) if emb_total else 0.0
    avg_latency_ms = (stats.latency_total_ms / stats.latency_samples) if stats.latency_samples else 0.0
    return {
        "hit_rate": round(hit_rate, 4),
        "miss_rate": round(miss_rate, 4),
        "avg_latency_ms": round(avg_latency_ms, 3),
        "postgres_calls": stats.postgres_calls,
        "redis_hits": stats.redis_hits,
        "redis_misses": stats.redis_misses,
        "embedding_reuse_rate": round(embedding_reuse_rate, 4),
        "coalesced_waiters": stats.coalesced_waiters,
    }


def role_relevance_score(role: str | None, applicable_roles: list[str]) -> float:
    safe_role = _safe_role(role)
    if safe_role == "global":
        return 1.0
    return 1.0 if safe_role in {r.strip().lower() for r in applicable_roles} else 0.0


def graph_centrality_score(row: dict[str, Any]) -> float:
    # Deterministic fallback until dedicated centrality store is added.
    tags = row.get("tags") or []
    if not tags:
        return 0.5
    return min(1.0, 0.5 + (len(tags) * 0.05))


def composite_score(row: dict[str, Any], role: str | None) -> float:
    semantic_similarity = float(row.get("score", 0.0))
    importance = float(row.get("importance_score", 0.5))
    role_rel = role_relevance_score(role, row.get("applicable_roles") or [])
    centrality = graph_centrality_score(row)
    return (
        0.4 * semantic_similarity
        + 0.2 * importance
        + 0.2 * role_rel
        + 0.2 * centrality
    )


async def invalidate_pattern(redis: Redis, pattern: str) -> int:
    keys = []
    async for key in redis.scan_iter(match=pattern, count=500):
        keys.append(key)
    if not keys:
        return 0
    return int(await redis.delete(*keys))

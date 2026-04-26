import hashlib
import json

from redis.asyncio import Redis


def query_hash(query: str) -> str:
    return hashlib.sha256(query.strip().lower().encode("utf-8")).hexdigest()[:16]


def cache_key(query: str, role: str | None, top_k: int) -> str:
    role_value = role or "all"
    return f"ctx:v2:{query_hash(query)}:{role_value}:{top_k}"


async def get_cached_results(
    redis: Redis,
    query: str,
    role: str | None,
    top_k: int,
) -> list[dict] | None:
    key = cache_key(query, role, top_k)
    value = await redis.get(key)
    if not value:
        return None
    return json.loads(value)


async def set_cached_results(
    redis: Redis,
    query: str,
    role: str | None,
    top_k: int,
    rows: list[dict],
    ttl_seconds: int,
) -> None:
    key = cache_key(query, role, top_k)
    payload = json.dumps(rows, separators=(",", ":"), ensure_ascii=True)
    await redis.setex(key, ttl_seconds, payload)


async def set_session_memory(redis: Redis, session_id: str, data: dict, ttl_seconds: int) -> None:
    key = f"session:{session_id}"
    await redis.setex(key, ttl_seconds, json.dumps(data, separators=(",", ":"), ensure_ascii=True))

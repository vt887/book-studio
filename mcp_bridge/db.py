import json
from typing import Any

import asyncpg


_schema_checked = False


async def ensure_schema(pool: asyncpg.Pool) -> None:
    global _schema_checked
    if _schema_checked:
        return

    statements = [
        "ALTER TABLE concepts ADD COLUMN IF NOT EXISTS importance_score DOUBLE PRECISION NOT NULL DEFAULT 0.5",
        "ALTER TABLE concepts ADD COLUMN IF NOT EXISTS source_chunks JSONB NOT NULL DEFAULT '[]'::jsonb",
        """
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            book_id TEXT NOT NULL,
            text_hash TEXT NOT NULL,
            text_content TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_chunks_book_hash ON chunks (book_id, text_hash)",
        "CREATE INDEX IF NOT EXISTS idx_chunks_book_id ON chunks (book_id)",
        "CREATE INDEX IF NOT EXISTS idx_concepts_source_chunks_gin ON concepts USING gin (source_chunks jsonb_path_ops)",
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """,
        "DROP TRIGGER IF EXISTS trg_chunks_updated_at ON chunks",
        "CREATE TRIGGER trg_chunks_updated_at BEFORE UPDATE ON chunks FOR EACH ROW EXECUTE FUNCTION set_updated_at()",
    ]

    async with pool.acquire() as conn:
        async with conn.transaction():
            for stmt in statements:
                await conn.execute(stmt)

    _schema_checked = True


def _normalize_json_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except json.JSONDecodeError:
            return []
    return []


def vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{v:.8f}" for v in values) + "]"


async def init_pg_pool(dsn: str, min_size: int = 5, max_size: int = 20) -> asyncpg.Pool:
    return await asyncpg.create_pool(dsn=dsn, min_size=min_size, max_size=max_size)


async def healthcheck(pool: asyncpg.Pool) -> bool:
    async with pool.acquire() as conn:
        value = await conn.fetchval("SELECT 1")
    return value == 1


async def upsert_concepts(
    pool: asyncpg.Pool,
    book_id: str,
    concepts: list[dict[str, Any]],
) -> tuple[int, int]:
    inserted = 0
    updated = 0

    async with pool.acquire() as conn:
        async with conn.transaction():
            for concept in concepts:
                emb = vector_literal(concept["embedding"])
                tags = concept.get("tags", [])
                roles = concept.get("applicable_roles", [])
                source_chunks = concept.get("source_chunks", [])
                importance_score = float(concept.get("importance_score", 0.5))

                existed = await conn.fetchval(
                    "SELECT 1 FROM concepts WHERE concept_id = $1",
                    concept["concept_id"],
                )

                await conn.execute(
                    """
                    INSERT INTO concepts (
                        concept_id,
                        book_id,
                        name,
                        definition,
                        summary,
                        importance_score,
                        source_chunks,
                        embedding,
                        tags,
                        applicable_roles
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8::vector, $9::jsonb, $10::jsonb)
                    ON CONFLICT (concept_id)
                    DO UPDATE SET
                        book_id = EXCLUDED.book_id,
                        name = EXCLUDED.name,
                        definition = EXCLUDED.definition,
                        summary = EXCLUDED.summary,
                        importance_score = EXCLUDED.importance_score,
                        source_chunks = EXCLUDED.source_chunks,
                        embedding = EXCLUDED.embedding,
                        tags = EXCLUDED.tags,
                        applicable_roles = EXCLUDED.applicable_roles,
                        updated_at = NOW()
                    """,
                    concept["concept_id"],
                    book_id,
                    concept["name"],
                    concept.get("definition", ""),
                    concept.get("summary", ""),
                    importance_score,
                    json.dumps(source_chunks),
                    emb,
                    json.dumps(tags),
                    json.dumps(roles),
                )

                if existed:
                    updated += 1
                else:
                    inserted += 1

    return inserted, updated


async def semantic_search(
    pool: asyncpg.Pool,
    query_embedding: list[float],
    top_k: int,
    role: str | None,
) -> list[dict[str, Any]]:
    emb = vector_literal(query_embedding)

    sql = """
        SELECT
            concept_id,
            book_id,
            name,
            definition,
            summary,
            importance_score,
            source_chunks,
            tags,
            applicable_roles,
            1 - (embedding <=> $1::vector) AS score
        FROM concepts
    """

    args: list[Any] = [emb]
    if role:
        sql += " WHERE applicable_roles ? $2 "
        args.append(role)

    sql += " ORDER BY embedding <=> $1::vector, concept_id ASC "
    if role:
        sql += " LIMIT $3 "
        args.append(top_k)
    else:
        sql += " LIMIT $2 "
        args.append(top_k)

    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *args)

    results: list[dict[str, Any]] = []
    for row in rows:
        tags = _normalize_json_list(row["tags"])
        roles = _normalize_json_list(row["applicable_roles"])
        source_chunks = _normalize_json_list(row["source_chunks"])
        results.append(
            {
                "concept_id": row["concept_id"],
                "book_id": row["book_id"],
                "name": row["name"],
                "definition": row["definition"],
                "summary": row["summary"],
                "importance_score": float(row["importance_score"] or 0.5),
                "source_chunks": source_chunks,
                "tags": tags,
                "applicable_roles": roles,
                "score": float(row["score"]),
            }
        )
    return results


async def upsert_chunks(pool: asyncpg.Pool, chunks: list[dict[str, Any]]) -> tuple[int, int]:
    inserted = 0
    updated = 0

    async with pool.acquire() as conn:
        async with conn.transaction():
            for chunk in chunks:
                existed = await conn.fetchval(
                    "SELECT 1 FROM chunks WHERE chunk_id = $1",
                    chunk["chunk_id"],
                )

                await conn.execute(
                    """
                    INSERT INTO chunks (chunk_id, book_id, text_hash, text_content)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (chunk_id)
                    DO UPDATE SET
                        book_id = EXCLUDED.book_id,
                        text_hash = EXCLUDED.text_hash,
                        text_content = EXCLUDED.text_content,
                        updated_at = NOW()
                    """,
                    chunk["chunk_id"],
                    chunk["book_id"],
                    chunk["text_hash"],
                    chunk.get("text_content", ""),
                )

                if existed:
                    updated += 1
                else:
                    inserted += 1

    return inserted, updated


async def valid_chunk_count(pool: asyncpg.Pool, chunk_ids: list[str]) -> int:
    if not chunk_ids:
        return 0
    async with pool.acquire() as conn:
        return int(
            await conn.fetchval(
                "SELECT COUNT(*) FROM chunks WHERE chunk_id = ANY($1::text[])",
                chunk_ids,
            )
            or 0
        )


async def get_concepts_for_quality(
    pool: asyncpg.Pool,
    *,
    book_id: str | None = None,
    concept_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    concept_ids = concept_ids or []
    sql = """
        SELECT
            concept_id,
            book_id,
            name,
            definition,
            summary,
            importance_score,
            source_chunks,
            tags,
            applicable_roles
        FROM concepts
    """
    args: list[Any] = []
    if book_id and concept_ids:
        sql += " WHERE book_id = $1 AND concept_id = ANY($2::text[]) "
        args = [book_id, concept_ids]
    elif book_id:
        sql += " WHERE book_id = $1 "
        args = [book_id]
    elif concept_ids:
        sql += " WHERE concept_id = ANY($1::text[]) "
        args = [concept_ids]

    sql += " ORDER BY concept_id ASC "

    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *args)

    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(
            {
                "concept_id": row["concept_id"],
                "book_id": row["book_id"],
                "name": row["name"],
                "definition": row["definition"],
                "summary": row["summary"],
                "importance_score": float(row["importance_score"] or 0.5),
                "source_chunks": _normalize_json_list(row["source_chunks"]),
                "tags": _normalize_json_list(row["tags"]),
                "applicable_roles": _normalize_json_list(row["applicable_roles"]),
                "embedding": [],
            }
        )
    return out

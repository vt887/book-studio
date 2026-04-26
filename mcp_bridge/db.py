import json
from typing import Any

import asyncpg


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
                        embedding,
                        tags,
                        applicable_roles
                    )
                    VALUES ($1, $2, $3, $4, $5, $6::vector, $7::jsonb, $8::jsonb)
                    ON CONFLICT (concept_id)
                    DO UPDATE SET
                        book_id = EXCLUDED.book_id,
                        name = EXCLUDED.name,
                        definition = EXCLUDED.definition,
                        summary = EXCLUDED.summary,
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
        tags = row["tags"] or []
        roles = row["applicable_roles"] or []
        results.append(
            {
                "concept_id": row["concept_id"],
                "book_id": row["book_id"],
                "name": row["name"],
                "definition": row["definition"],
                "summary": row["summary"],
                "tags": tags,
                "applicable_roles": roles,
                "score": float(row["score"]),
            }
        )
    return results

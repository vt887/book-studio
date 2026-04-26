from neo4j import AsyncGraphDatabase


class Neo4jStore:
    def __init__(self, uri: str, user: str, password: str) -> None:
        self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self) -> None:
        await self._driver.close()

    async def healthcheck(self) -> bool:
        async with self._driver.session() as session:
            value = await session.run("RETURN 1 AS ok")
            record = await value.single()
        return bool(record and record["ok"] == 1)

    async def ensure_indexes(self) -> None:
        async with self._driver.session() as session:
            await session.run(
                "CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.concept_id IS UNIQUE"
            )

    async def link_concepts(
        self,
        from_id: str,
        to_id: str,
        relation: str,
        weight: float,
    ) -> None:
        query = """
        MERGE (a:Concept {concept_id: $from_id})
        MERGE (b:Concept {concept_id: $to_id})
        MERGE (a)-[r:RELATES {type: $relation}]->(b)
        SET r.weight = $weight
        """
        async with self._driver.session() as session:
            await session.run(
                query,
                from_id=from_id,
                to_id=to_id,
                relation=relation,
                weight=weight,
            )

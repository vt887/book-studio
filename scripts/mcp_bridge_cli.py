import asyncio
import argparse
import json
import time
from mcp_bridge import db, cache
from mcp_bridge.config import settings
from mcp_bridge.embedding import deterministic_embedding
from mcp_bridge.graph import Neo4jStore
from mcp_bridge.models import CtxReadRequest, CtxWriteRequest, CtxGraphLinkRequest

class MCPBridgeCLI:
    def __init__(self):
        self.pg_pool = None
        self.redis = None
        self.graph = None

    async def connect(self):
        self.pg_pool = await db.init_pg_pool(settings.pg_dsn)
        try:
            from redis.asyncio import Redis
            self.redis = Redis.from_url(settings.redis_url, decode_responses=True)
            await self.redis.ping()
        except Exception:
            self.redis = None
        self.graph = Neo4jStore(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)

    async def close(self):
        if self.pg_pool: await self.pg_pool.close()
        if self.redis: await self.redis.close()
        if self.graph: await self.graph.close()

    async def run_read(self, query, top_k=5, role=None):
        req = CtxReadRequest(query=query, top_k=top_k, role=role)
        # Note: logic here would call internal _ctx_read_logic
        print(f"Executing read: {query}")

    async def run_write(self, book_id, data):
        # Implementation of _ctx_write_logic logic
        print(f"Executing write for {book_id}")

    async def run_graph_link(self, from_id, to_id, relation, weight):
        # Implementation of _ctx_graph_link_logic logic
        print(f"Linking {from_id} -> {to_id}")

async def main():
    parser = argparse.ArgumentParser(description="Book Studio Native CLI Bridge")
    subparsers = parser.add_subparsers(dest="command")

    read_parser = subparsers.add_parser("read")
    read_parser.add_argument("--query", required=True)
    read_parser.add_argument("--top_k", type=int, default=5)
    read_parser.add_argument("--role")

    write_parser = subparsers.add_parser("write")
    write_parser.add_argument("--book_id", required=True)
    write_parser.add_argument("--data", required=True, help="JSON string")

    link_parser = subparsers.add_parser("link")
    link_parser.add_argument("--from_id", required=True)
    link_parser.add_argument("--to_id", required=True)
    link_parser.add_argument("--relation", required=True)
    link_parser.add_argument("--weight", type=float, default=1.0)

    args = parser.parse_args()
    
    bridge = MCPBridgeCLI()
    await bridge.connect()
    
    if args.command == "read":
        await bridge.run_read(args.query, args.top_k, args.role)
    elif args.command == "write":
        await bridge.run_write(args.book_id, json.loads(args.data))
    elif args.command == "link":
        await bridge.run_graph_link(args.from_id, args.to_id, args.relation, args.weight)
        
    await bridge.close()

if __name__ == "__main__":
    asyncio.run(main())

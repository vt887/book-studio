import os


class Settings:
    app_name: str = "lean-ctx-mcp-memory-bridge"
    app_version: str = "0.1.0"

    host: str = os.getenv("MCP_BRIDGE_HOST", "0.0.0.0")
    port: int = int(os.getenv("MCP_BRIDGE_PORT", "8080"))

    pg_dsn: str = os.getenv(
        "POSTGRES_DSN",
        "postgresql://leanctx:leanctx_pass@postgres:5432/leanctx_db",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "leanctx_pass")

    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "384"))
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "600"))
    session_ttl_seconds: int = int(os.getenv("SESSION_TTL_SECONDS", "1800"))


settings = Settings()

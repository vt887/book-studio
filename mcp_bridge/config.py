import os


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


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
    embedding_model_version: str = os.getenv("EMBEDDING_MODEL_VERSION", "deterministic-v1")

    cache_version: str = os.getenv("CACHE_VERSION", "v3")
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "600"))
    role_cache_ttl_seconds: int = int(os.getenv("ROLE_CACHE_TTL_SECONDS", "3600"))
    graph_cache_ttl_seconds: int = int(os.getenv("GRAPH_CACHE_TTL_SECONDS", "86400"))
    embedding_cache_ttl_seconds: int = int(os.getenv("EMBEDDING_CACHE_TTL_SECONDS", "86400"))
    session_ttl_seconds: int = int(os.getenv("SESSION_TTL_SECONDS", "1800"))

    retrieval_version: str = os.getenv("RETRIEVAL_VERSION", "v2")
    retrieval_top_k_max: int = int(os.getenv("RETRIEVAL_TOP_K_MAX", "7"))
    retrieval_candidate_pool: int = int(os.getenv("RETRIEVAL_CANDIDATE_POOL", "30"))
    retrieval_v2_enabled: bool = _env_bool("RETRIEVAL_V2_ENABLED", True)
    query_expansion_retry_enabled: bool = _env_bool("QUERY_EXPANSION_RETRY_ENABLED", True)

    quality_gate_enabled: bool = _env_bool("QUALITY_GATE_ENABLED", True)
    quality_gate_enforce: bool = _env_bool("QUALITY_GATE_ENFORCE", True)
    quality_threshold: float = float(os.getenv("QUALITY_THRESHOLD", "0.80"))


settings = Settings()

from typing import Any

from pydantic import BaseModel, Field


class ConceptIn(BaseModel):
    concept_id: str
    name: str
    definition: str = ""
    summary: str = ""
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    source_chunks: list[str] = Field(default_factory=list)
    embedding: list[float] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    applicable_roles: list[str] = Field(default_factory=list)


class CtxWriteData(BaseModel):
    concepts: list[ConceptIn] = Field(default_factory=list)


class CtxWriteRequest(BaseModel):
    book_id: str
    data: CtxWriteData


class CtxWriteResponse(BaseModel):
    status: str
    inserted: int
    updated: int


class CtxReadRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=50)
    role: str | None = None


class CtxReadResult(BaseModel):
    concept_id: str
    book_id: str
    name: str
    definition: str
    summary: str
    importance_score: float = Field(default=0.5)
    source_chunks: list[str] = Field(default_factory=list)
    tags: list[str]
    applicable_roles: list[str]
    score: float


class ChunkIn(BaseModel):
    chunk_id: str
    book_id: str
    text_hash: str
    text_content: str = ""


class ChunkWriteRequest(BaseModel):
    chunks: list[ChunkIn] = Field(default_factory=list)


class ChunkWriteResponse(BaseModel):
    status: str
    inserted: int
    updated: int


class QualityEvaluateRequest(BaseModel):
    book_id: str | None = None
    concept_ids: list[str] = Field(default_factory=list)


class QualityEvaluateItem(BaseModel):
    concept_id: str
    grounding_score: float
    completeness_score: float
    consistency_score: float
    quality_score: float
    valid: bool


class QualityEvaluateResponse(BaseModel):
    status: str
    threshold: float
    total: int
    valid_count: int
    invalid_count: int
    items: list[QualityEvaluateItem]


class CtxReadResponse(BaseModel):
    source: str
    results: list[CtxReadResult]
    cache_hit: bool = False
    cache_key: str | None = None
    latency_ms: float | None = None


class CacheInvalidateRequest(BaseModel):
    pattern: str = "ctx:l1:semantic:*"


class CacheInvalidateResponse(BaseModel):
    status: str
    pattern: str
    deleted: int


class CacheStatsResponse(BaseModel):
    hit_rate: float
    miss_rate: float
    avg_latency_ms: float
    postgres_calls: int
    redis_hits: int
    redis_misses: int
    embedding_reuse_rate: float
    coalesced_waiters: int


class CtxGraphLinkRequest(BaseModel):
    from_id: str
    to_id: str
    relation: str
    weight: float = Field(ge=0.0, le=1.0)


class CtxGraphLinkResponse(BaseModel):
    status: str
    relation: str
    from_id: str
    to_id: str
    weight: float


class HealthResponse(BaseModel):
    status: str
    checks: dict[str, Any]


class ToolCallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolCallResponse(BaseModel):
    tool: str
    result: dict[str, Any]

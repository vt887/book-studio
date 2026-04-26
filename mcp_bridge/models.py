from typing import Any

from pydantic import BaseModel, Field


class ConceptIn(BaseModel):
    concept_id: str
    name: str
    definition: str = ""
    summary: str = ""
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
    tags: list[str]
    applicable_roles: list[str]
    score: float


class CtxReadResponse(BaseModel):
    source: str
    results: list[CtxReadResult]


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

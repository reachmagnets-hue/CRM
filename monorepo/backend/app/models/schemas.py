from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    ok: bool = True
    ts: float
    version: str


class SearchResult(BaseModel):
    score: float
    filename: str
    page: int | None = None
    snippet: str


class SearchResponse(BaseModel):
    results: List[SearchResult]


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = Field(default_factory=list)
    top_k: int = 5
    tenant: Optional[str] = None


class IngestResponse(BaseModel):
    ok: bool
    doc_id: str
    chunks: int


class TenantsResponse(BaseModel):
    tenants: dict

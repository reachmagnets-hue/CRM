from __future__ import annotations

from typing import AsyncIterator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from ..auth import require_public_key, resolve_tenant
from ..models.schemas import ChatRequest
from ..services.llm import stream_generate
from ..services.rag import build_prompt, retrieve


router = APIRouter(tags=["chat"], dependencies=[Depends(require_public_key)])


@router.post("/chat/stream")
async def chat_stream(request: Request, body: ChatRequest) -> StreamingResponse:
    # Allow body to request tenant override; attach to state for resolver
    if body.tenant:
        request.state.tenant_id = body.tenant
    tenant_id = resolve_tenant(request)
    hits = await retrieve(tenant_id, body.message, top_k=body.top_k)
    messages = build_prompt(body.message, hits)

    async def _gen() -> AsyncIterator[bytes]:
        async for chunk in stream_generate(messages):
            yield chunk.encode("utf-8")

    return StreamingResponse(_gen(), media_type="text/plain; charset=utf-8")

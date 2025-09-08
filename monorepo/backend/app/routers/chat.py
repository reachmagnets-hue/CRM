from __future__ import annotations

from typing import AsyncIterator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from ..auth import require_site_auth, resolve_tenant
from ..models.schemas import ChatRequest
from ..services.llm import stream_generate
from ..services.rag import build_prompt, retrieve
from ..services.db import open_session, ChatLog


router = APIRouter(tags=["chat"], dependencies=[Depends(require_site_auth)])


@router.post("/chat/stream")
async def chat_stream(request: Request, body: ChatRequest) -> StreamingResponse:
    # Allow body to request tenant override; attach to state for resolver
    if body.tenant:
        request.state.tenant_id = body.tenant
    tenant_id = resolve_tenant(request)
    # Optional per-customer filtering
    filter_meta = {"customer_id": body.customer_id} if getattr(body, "customer_id", None) else None
    hits = await retrieve(tenant_id, body.message, body.top_k, filter_meta)
    messages = build_prompt(body.message, hits)

    chunks: list[str] = []
    async def _gen() -> AsyncIterator[bytes]:
        async for chunk in stream_generate(messages):
            chunks.append(chunk)
            yield chunk.encode("utf-8")

    async def _on_complete() -> None:
        # Persist chat log best-effort
        try:
            answer = "".join(chunks)
            with open_session() as session:
                session.add(ChatLog(site_id=tenant_id, customer_id=body.customer_id, question=body.message, answer=answer))
                session.commit()
        except Exception:
            pass

    response = StreamingResponse(_gen(), media_type="text/plain; charset=utf-8")
    # Attach background callback via FastAPI-style background tasks if available
    try:
        from fastapi import BackgroundTasks

        bg = BackgroundTasks()
        bg.add_task(_on_complete)
        # FastAPI StreamingResponse supports background parameter
        response.background = bg
    except Exception:
        # Fall back: fire-and-forget
        import asyncio

        asyncio.create_task(_on_complete())

    return response

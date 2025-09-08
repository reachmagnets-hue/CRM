from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from ..auth import require_site_auth, resolve_tenant
from ..models.schemas import SearchResponse, SearchResult
from ..services.embed import embed_texts
from ..services.vector import ChromaStore
from ..config import SETTINGS


router = APIRouter(tags=["search"], dependencies=[Depends(require_site_auth)])


@router.get("/search", response_model=SearchResponse)
async def search(
    request: Request,
    q: str = Query(...),
    top_k: int = Query(5, ge=1, le=20),
    customer_id: str | None = Query(default=None),
) -> SearchResponse:
    tenant_id = resolve_tenant(request)
    if not q.strip():
        raise HTTPException(status_code=400, detail="Empty query")
    [qvec] = await embed_texts([q])
    store = ChromaStore(SETTINGS.chroma_dir, tenant_id)
    where = {"customer_id": customer_id} if customer_id else None
    hits = store.query(qvec, top_k=top_k, where=where)
    results = [
        SearchResult(
            score=float(h.get("score", 0.0)),
            filename=h.get("metadata", {}).get("filename", ""),
            page=h.get("metadata", {}).get("page"),
            snippet=h.get("metadata", {}).get("text", "")[:400],
        )
        for h in hits
    ]
    return SearchResponse(results=results)

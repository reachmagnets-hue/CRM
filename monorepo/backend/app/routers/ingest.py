from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status, Query

from ..auth import require_admin_key, require_site_auth, resolve_tenant
from ..models.schemas import IngestResponse
from ..services.chunk import chunk_text
from ..services.embed import embed_texts
from ..services.storage import extract_text, save_upload
from ..services.vector import ChromaStore
from ..config import SETTINGS
from ..services.db import open_session, Upload


router = APIRouter(tags=["ingest"], dependencies=[Depends(require_admin_key), Depends(require_site_auth)])


ALLOWED_MIME = {"application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_SIZE_MB = 25


@router.post("/ingest/upload", response_model=IngestResponse)
async def ingest_upload(
    request: Request,
    file: UploadFile = File(...),
    customer_id: str | None = Query(default=None, description="Optional customer id to scope docs")
) -> IngestResponse:
    tenant_id = resolve_tenant(request)
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
    doc_id, saved_path = save_upload(tenant_id, file, customer_id=customer_id)
    text = extract_text(saved_path)
    if not text.strip():
        raise HTTPException(status_code=400, detail="Empty or unreadable document")
    chunks = chunk_text(text)
    embeddings = await embed_texts(chunks)
    store = ChromaStore(SETTINGS.chroma_dir, tenant_id)
    items = []
    for idx, (chunk, vec) in enumerate(zip(chunks, embeddings)):
        items.append(
            (
                f"{doc_id}-{idx}",
                vec,
                {
                    "doc_id": doc_id,
                    "filename": saved_path.name,
                    "page": idx + 1,
                    "text": chunk,
                    **({"customer_id": customer_id} if customer_id else {}),
                },
            )
        )
    count = store.upsert(items)
    # Log upload best-effort
    try:
        import json
        meta = {"doc_id": doc_id, "customer_id": customer_id}
        with open_session() as session:
            session.add(Upload(site_id=tenant_id, customer_id=customer_id, filename=saved_path.name, metadata_json=json.dumps(meta)))
            session.commit()
    except Exception:
        pass
    return IngestResponse(ok=True, doc_id=doc_id, chunks=count)

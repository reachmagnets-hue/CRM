from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from ..auth import require_admin_key, resolve_tenant
from ..models.schemas import IngestResponse
from ..services.chunk import chunk_text
from ..services.embed import embed_texts
from ..services.storage import extract_text, save_upload
from ..services.vector import ChromaStore
from ..config import SETTINGS


router = APIRouter(tags=["ingest"], dependencies=[Depends(require_admin_key)])


ALLOWED_MIME = {"application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_SIZE_MB = 25


@router.post("/ingest/upload", response_model=IngestResponse)
async def ingest_upload(request: Request, file: UploadFile = File(...)) -> IngestResponse:
    tenant_id = resolve_tenant(request)
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
    doc_id, saved_path = save_upload(tenant_id, file)
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
                {"doc_id": doc_id, "filename": saved_path.name, "page": idx + 1, "text": chunk},
            )
        )
    count = store.upsert(items)
    return IngestResponse(ok=True, doc_id=doc_id, chunks=count)

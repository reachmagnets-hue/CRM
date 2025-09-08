from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status

from ..auth import require_site_auth, resolve_tenant
from ..services.storage import save_upload
from ..services.db import open_session, Upload


router = APIRouter(tags=["uploads"], dependencies=[Depends(require_site_auth)])


ALLOWED_MIME = {"application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_SIZE_MB = 25


@router.post("/uploads")
async def uploads(request: Request, file: UploadFile = File(...), customer_id: str | None = Query(default=None)) -> dict:
    tenant_id = resolve_tenant(request)
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
    # TODO: enforce max size by reading .spool? Depends on web server; keep simple for now
    doc_id, saved_path = save_upload(tenant_id, file, customer_id=customer_id)
    # Log upload
    try:
        import json
        meta = {"doc_id": doc_id, "customer_id": customer_id}
        with open_session() as session:
            session.add(Upload(site_id=tenant_id, customer_id=customer_id, filename=saved_path.name, metadata_json=json.dumps(meta)))
            session.commit()
    except Exception:
        pass
    return {"ok": True, "doc_id": doc_id, "filename": saved_path.name}

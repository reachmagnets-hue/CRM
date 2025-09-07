from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from ..auth import require_admin_key, require_public_key, resolve_tenant
from ..config import SETTINGS
from ..models.schemas import TenantsResponse
from pathlib import Path
import json


router = APIRouter(tags=["tenants"])


@router.get("/tenants", response_model=TenantsResponse, dependencies=[Depends(require_admin_key)])
def list_tenants() -> TenantsResponse:
    return TenantsResponse(
        tenants={
            t: {"domains": doms, "origins": SETTINGS.tenant_origins.get(t, [])}
            for t, doms in SETTINGS.tenant_domains.items()
        }
    )


@router.get("/tenants/info", dependencies=[Depends(require_public_key)])
def tenant_info(request: Request) -> dict:
    tenant_id = resolve_tenant(request)
    booking_urls = SETTINGS.booking_pages.get(tenant_id, [])
    booking_url = booking_urls[0] if booking_urls else None
    # Try load services json: DATA_DIR/tenants/{tenant_id}/services.json
    path = Path(SETTINGS.data_dir) / "tenants" / tenant_id / "services.json"
    services = []
    if path.exists():
        try:
            services = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            services = []
    return {
        "tenant_id": tenant_id,
        "booking_url": booking_url,
        "services": services,
    }

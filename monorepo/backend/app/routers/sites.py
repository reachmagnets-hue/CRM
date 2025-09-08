from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pathlib import Path
import json

from ..auth import require_site_auth, resolve_tenant
from ..config import SETTINGS


router = APIRouter(tags=["sites"], dependencies=[Depends(require_site_auth)])


@router.get("/sites/info")
def site_info(request: Request) -> dict:
    site_id = resolve_tenant(request)
    booking_urls = SETTINGS.booking_pages.get(site_id, [])
    booking_url = booking_urls[0] if booking_urls else None
    path = Path(SETTINGS.data_dir) / "tenants" / site_id / "services.json"
    services = []
    numbers = SETTINGS.twilio_number_map.get(site_id, [])
    if path.exists():
        try:
            services = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            services = []
    return {"site_id": site_id, "booking_url": booking_url, "services": services, "numbers": numbers}

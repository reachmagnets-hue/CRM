from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from ..auth import require_site_auth, resolve_tenant


router = APIRouter(tags=["webhooks"], dependencies=[Depends(require_site_auth)])


@router.post("/webhooks/wp")
async def from_wp(request: Request) -> Dict[str, Any]:
    """
    WordPress -> Backend webhook endpoint.
    Configure this URL as an Action in WP Webhooks (Send Data).

    Auth: X-Site-Id + X-Api-Key headers (validated by require_site_auth).
    Body: Arbitrary JSON; recommended shape {"event": str, "data": {..}, "sent_at": ts}
    """
    # Site is validated by dependency; resolve tenant if possible, else fall back in dev/tests
    try:
        tenant_id = resolve_tenant(request)
    except Exception:
        tenant_id = getattr(request.state, "tenant_id", None) or "default"
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # You can route by event here
    event = str(body.get("event", "")).strip()
    data = body.get("data") or {}

    # Example: simple acknowledgement; extend with your own handlers/persistence
    return {"ok": True, "tenant_id": tenant_id, "event": event or None}


async def send_to_wp(event: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Backend -> WordPress sender helper.
    Uses env vars:
      - WP_WEBHOOK_URL: The WP Webhooks (Receive Data) URL
      - WP_WEBHOOK_KEY: Optional shared secret for HMAC-SHA256 signature
    """
    url = os.getenv("WP_WEBHOOK_URL", "").strip()
    secret = os.getenv("WP_WEBHOOK_KEY", "").strip()
    if not url:
        return {"ok": False, "reason": "WP_WEBHOOK_URL not set"}

    payload = {"event": event, "data": data}
    headers = {"Content-Type": "application/json"}

    # Optional: sign body so WP can verify it (map this header in WP if supported)
    if secret:
        digest = hmac.new(
            secret.encode("utf-8"),
            json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        headers["X-Webhook-Secret"] = digest

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(url, json=payload, headers=headers)
        return {"ok": resp.status_code < 300, "status": resp.status_code, "text": resp.text}

from __future__ import annotations

from fastapi import Header, HTTPException, Request
from starlette import status

from .config import SETTINGS


def require_public_key(x_public_key: str | None = Header(default=None)) -> None:
    if not SETTINGS.api_public_keys:
        return  # allow if unset in dev
    if not x_public_key or x_public_key not in SETTINGS.api_public_keys:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid public key")


def require_admin_key(x_admin_key: str | None = Header(default=None)) -> None:
    if not SETTINGS.admin_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin key not configured")
    if x_admin_key != SETTINGS.admin_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin key")


def resolve_tenant(request: Request, x_tenant_id: str | None = None) -> str:
    """Resolve tenant by header, body field (set upstream), or Host header mapping.
    Safe for direct calls from route handlers.
    """
    # 1. Explicit header (prefer passed arg; else read from request headers)
    if not x_tenant_id:
        x_tenant_id = request.headers.get("x-tenant-id")
    if x_tenant_id:
        return str(x_tenant_id)
    # 2. Request state/body (set by routes)
    tenant_from_body = getattr(request.state, "tenant_id", None)
    if tenant_from_body:
        return tenant_from_body
    # 3. Host header mapping
    host = request.headers.get("host", "").split(":")[0].lower()
    for tenant_id, domains in SETTINGS.tenant_domains.items():
        if host in [d.lower() for d in domains]:
            return tenant_id
    # If tenants configured, reject unknown hosts
    if SETTINGS.tenant_domains:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown tenant host")
    # Fallback single-tenant dev
    return "default"


def require_site_auth(
    request: Request,
    site_id: str | None = Header(default=None, alias="X-Site-Id"),
    api_key: str | None = Header(default=None, alias="X-Api-Key"),
):
    # Allow dev fallback if not configured
    if not SETTINGS.site_api_keys:
        return
    if not site_id or not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing site_id/api_key")
    valid = SETTINGS.site_api_keys.get(site_id, [])
    if api_key not in valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid api_key for site_id")
    # bridge: attach site_id to request.state for downstream tenant resolution
    request.state.tenant_id = site_id

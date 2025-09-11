from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..auth import require_bearer_or_public


router = APIRouter(tags=["crm"])


@router.get("/v1/customers", dependencies=[Depends(require_bearer_or_public)])
def list_customers(limit: int = Query(10, ge=1, le=100)) -> list[dict]:
    """Demo customers endpoint for WP server-to-server pulls.
    Replace with real DB queries when available.
    """
    stub = [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
        {"id": 3, "name": "Alex Lee", "email": "alex@example.com"},
        {"id": 4, "name": "Sam Patel", "email": "sam@example.com"},
        {"id": 5, "name": "Chris Kim", "email": "chris@example.com"},
    ]
    return stub[:limit]

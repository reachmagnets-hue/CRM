from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from ..auth import require_site_auth, resolve_tenant
from ..services.db import open_session, Appointment

router = APIRouter(tags=["appointments"], dependencies=[Depends(require_site_auth)])


@router.post("/appointments")
async def create_appointment(request: Request, payload: dict):
    site_id = resolve_tenant(request)
    if not isinstance(payload, dict) or not payload:
        raise HTTPException(status_code=400, detail="Invalid payload")
    with open_session() as session:
        session.add(Appointment(site_id=site_id, customer_id=str(payload.get("customer_id") or ""), data_json=str(payload)))
        session.commit()
    return {"ok": True}


@router.get("/appointments")
async def list_appointments(request: Request, limit: int = 50, offset: int = 0):
    site_id = resolve_tenant(request)
    with open_session() as session:
        rows = (
            session.query(Appointment)
            .filter(Appointment.site_id == site_id)
            .order_by(Appointment.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        data = [
            {
                "id": r.id,
                "customer_id": r.customer_id,
                "data": r.data_json,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    return {"appointments": data}

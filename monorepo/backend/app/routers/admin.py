from __future__ import annotations

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path

from ..auth import require_admin_key, require_site_auth, resolve_tenant
from ..services.db import open_session, ChatLog, CallLog, Upload, Appointment
from ..config import SETTINGS

router = APIRouter(tags=["admin"], dependencies=[Depends(require_admin_key), Depends(require_site_auth)])


@router.get("/admin/overview")
async def admin_overview(request: Request, limit: int = 20):
    site_id = resolve_tenant(request)
    with open_session() as session:
        chats = session.query(ChatLog).filter(ChatLog.site_id == site_id).order_by(ChatLog.id.desc()).limit(limit).all()
        calls = session.query(CallLog).filter(CallLog.site_id == site_id).order_by(CallLog.id.desc()).limit(limit).all()
        uploads = session.query(Upload).filter(Upload.site_id == site_id).order_by(Upload.id.desc()).limit(limit).all()
    return {
        "chats": [{"id": c.id, "q": c.question[:120], "a": c.answer[:120], "ts": c.created_at.isoformat()} for c in chats],
        "calls": [{"id": c.id, "from": c.from_number, "intent": c.service_intent, "outcome": c.outcome, "ts": c.created_at.isoformat()} for c in calls],
        "uploads": [{"id": u.id, "filename": u.filename, "ts": u.created_at.isoformat()} for u in uploads],
    }


@router.get("/admin/chats")
async def admin_chats(request: Request, limit: int = 100, offset: int = 0):
    site_id = resolve_tenant(request)
    with open_session() as session:
        rows = (
            session.query(ChatLog)
            .filter(ChatLog.site_id == site_id)
            .order_by(ChatLog.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
    return {
        "chats": [
            {"id": r.id, "customer_id": r.customer_id, "question": r.question, "answer": r.answer, "created_at": r.created_at.isoformat()}
            for r in rows
        ]
    }


@router.get("/admin/calls")
async def admin_calls(request: Request, limit: int = 100, offset: int = 0):
    site_id = resolve_tenant(request)
    with open_session() as session:
        rows = (
            session.query(CallLog)
            .filter(CallLog.site_id == site_id)
            .order_by(CallLog.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
    return {
        "calls": [
            {
                "id": r.id,
                "from_number": r.from_number,
                "customer_id": r.customer_id,
                "transcript": r.transcript,
                "service_intent": r.service_intent,
                "outcome": r.outcome,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    }


@router.get("/admin/uploads")
async def admin_uploads(request: Request, limit: int = 100, offset: int = 0):
    site_id = resolve_tenant(request)
    with open_session() as session:
        rows = (
            session.query(Upload)
            .filter(Upload.site_id == site_id)
            .order_by(Upload.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
    return {
        "uploads": [
            {"id": r.id, "customer_id": r.customer_id, "filename": r.filename, "metadata": r.metadata_json, "created_at": r.created_at.isoformat()}
            for r in rows
        ]
    }


@router.get("/admin/appointments")
async def admin_appointments(request: Request, limit: int = 100, offset: int = 0):
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
    return {
        "appointments": [
            {"id": r.id, "customer_id": r.customer_id, "data": r.data_json, "created_at": r.created_at.isoformat()}
            for r in rows
        ]
    }


@router.get("/admin/download/{upload_id}")
async def admin_download(request: Request, upload_id: int):
    site_id = resolve_tenant(request)
    with open_session() as session:
        row = session.query(Upload).filter(Upload.site_id == site_id, Upload.id == upload_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Upload not found")
    # Files are stored under DATA_DIR/docs/<site_id>[/<customer_id>]/<doc_id>.<ext>
    # We only stored filename and metadata_json with doc_id, so locate by filename within site tree.
    base = Path(SETTINGS.data_dir) / "docs" / site_id
    candidate = base / row.filename
    if not candidate.exists():
        # Try search once under subfolders
        for p in base.rglob(row.filename):
            candidate = p
            break
    if not candidate.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(candidate, filename=row.filename)


@router.get("/admin/view", response_class=HTMLResponse)
async def admin_view(request: Request):
    # Lightweight HTML dashboard
    site_id = resolve_tenant(request)
    with open_session() as session:
        chats = session.query(ChatLog).filter(ChatLog.site_id == site_id).order_by(ChatLog.id.desc()).limit(20).all()
        calls = session.query(CallLog).filter(CallLog.site_id == site_id).order_by(CallLog.id.desc()).limit(20).all()
        uploads = session.query(Upload).filter(Upload.site_id == site_id).order_by(Upload.id.desc()).limit(20).all()
        appts = session.query(Appointment).filter(Appointment.site_id == site_id).order_by(Appointment.id.desc()).limit(20).all()
    html = [
        "<html><head><title>Admin View</title><meta charset='utf-8'/><style>body{font:14px sans-serif} table{border-collapse:collapse} td,th{border:1px solid #ccc;padding:4px}</style></head><body>",
        f"<h1>Site: {site_id}</h1>",
        "<h2>Chats</h2>",
        "<table><tr><th>ID</th><th>Customer</th><th>Q</th><th>A</th><th>TS</th></tr>",
        *[f"<tr><td>{c.id}</td><td>{c.customer_id or ''}</td><td>{(c.question or '')[:80]}</td><td>{(c.answer or '')[:80]}</td><td>{c.created_at}</td></tr>" for c in chats],
        "</table>",
        "<h2>Calls</h2>",
        "<table><tr><th>ID</th><th>From</th><th>Intent</th><th>Outcome</th><th>TS</th></tr>",
        *[f"<tr><td>{x.id}</td><td>{x.from_number or ''}</td><td>{x.service_intent or ''}</td><td>{x.outcome or ''}</td><td>{x.created_at}</td></tr>" for x in calls],
        "</table>",
        "<h2>Uploads</h2>",
        "<table><tr><th>ID</th><th>Customer</th><th>Filename</th><th>TS</th></tr>",
        *[f"<tr><td>{u.id}</td><td>{u.customer_id or ''}</td><td>{u.filename}</td><td>{u.created_at}</td></tr>" for u in uploads],
        "</table>",
        "<h2>Appointments</h2>",
        "<table><tr><th>ID</th><th>Customer</th><th>Data</th><th>TS</th></tr>",
        *[f"<tr><td>{a.id}</td><td>{a.customer_id or ''}</td><td>{(a.data_json or '')[:100]}</td><td>{a.created_at}</td></tr>" for a in appts],
        "</table>",
        "</body></html>",
    ]
    return HTMLResponse("".join(html))

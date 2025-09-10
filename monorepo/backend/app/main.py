from __future__ import annotations

import os
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from .config import SETTINGS
from .log import setup_logging
from .routers import chat, health, ingest, search, tenants, twilio, appointments, admin, ads, uploads, sites, webhooks


def _collect_cors_origins() -> List[str]:
    origins: List[str] = []
    for _, tenant_origins in SETTINGS.tenant_origins.items():
        origins.extend(tenant_origins)
    # Fallback dev permissive if none set
    if not origins:
        origins = ["*"]
    return origins


setup_logging()
app = FastAPI(title="Multi-tenant RAG Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_collect_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Ensure data directories exist
DATA_DIR = Path(SETTINGS.data_dir)
(DATA_DIR / "audio").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "docs").mkdir(parents=True, exist_ok=True)

# Serve TTS audio files in dev (prod should be via nginx)
app.mount("/static/audio", StaticFiles(directory=str(DATA_DIR / "audio")), name="audio")

# Routers
app.include_router(health.router)
app.include_router(tenants.router, prefix="/api/v1")
app.include_router(ingest.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(twilio.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(ads.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1")
app.include_router(sites.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")


@app.get("/")
def index() -> dict:
    return {"ok": True, "service": "rag-backend", "version": app.version}

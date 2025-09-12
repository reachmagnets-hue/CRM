from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import rtc


def test_rtc_health_ok():
    app = FastAPI()
    app.include_router(rtc.router, prefix="/api/v1")
    client = TestClient(app)
    r = client.get("/api/v1/rtc/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "pc" in body

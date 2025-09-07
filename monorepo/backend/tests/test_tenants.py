from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_tenants_requires_admin():
    client = TestClient(app)
    r = client.get("/api/v1/tenants")
    assert r.status_code in (401, 403)

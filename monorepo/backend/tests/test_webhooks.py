from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_wp_webhook_ok_in_dev():
    client = TestClient(app)
    r = client.post("/api/v1/webhooks/wp", json={"event": "ping", "data": {}})
    assert r.status_code == 200
    assert r.json().get("ok") is True

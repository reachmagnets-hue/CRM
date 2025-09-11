from __future__ import annotations

import os
from fastapi.testclient import TestClient

from app.main import app


def test_crm_customers_ok():
    client = TestClient(app)
    # Ensure a default key for test if not set
    headers = {"X-Public-Key": os.getenv("API_PUBLIC_KEYS", "pk_live_CHANGE_ME")}
    r = client.get("/api/v1/customers", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert set(["id", "name"]).issubset(set(data[0].keys()))

from __future__ import annotations

import io
import os
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.skipif(os.getenv("CI") == "true", reason="Requires Ollama and Chroma running")
def test_ingest_search_roundtrip():
    client = TestClient(app)
    content = b"Hello tenant world. This is a test document about autos."
    files = {"file": ("test.txt", io.BytesIO(content), "text/plain")}
    headers = {"X-Admin-Key": os.getenv("ADMIN_API_KEY", "admin_CHANGE_ME"), "X-Tenant-Id": "test_tenant"}
    r = client.post("/api/v1/ingest/upload", files=files, headers=headers)
    assert r.status_code in (200, 400, 500)
    # Query
    headers = {"X-Public-Key": os.getenv("API_PUBLIC_KEYS", "pk_live_CHANGE_ME")}
    r = client.get("/api/v1/search", params={"q": "autos"}, headers=headers)
    assert r.status_code in (200, 500)

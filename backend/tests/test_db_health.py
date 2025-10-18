import os

from fastapi.testclient import TestClient

from src.main import app


def test_health_reports_db_status_sqlite(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body.get("db") in {"ok", "down"}


from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_health_ok() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_root_index() -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("service") == "chrona-backend"

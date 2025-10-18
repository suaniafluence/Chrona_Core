import importlib
import sys

from fastapi.testclient import TestClient


def test_allow_credentials_true(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("ALLOW_CREDENTIALS", "true")
    # Force reload to apply new env config
    if "src.main" in sys.modules:
        del sys.modules["src.main"]
    m = importlib.import_module("src.main")
    client = TestClient(m.app)

    r = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-credentials") == "true"


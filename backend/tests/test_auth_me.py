from fastapi.testclient import TestClient

from src.main import app


def test_me_requires_token(tmp_path, monkeypatch) -> None:
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    with TestClient(app) as client:
        r = client.get("/auth/me")
        assert r.status_code == 401


def test_register_login_me_flow(tmp_path, monkeypatch) -> None:
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    with TestClient(app) as client:
        # Register
        r = client.post(
            "/auth/register",
            json={"email": "alice@example.com", "password": "secretpw"},
        )
        assert r.status_code == 201, r.text
        # Login to get token
        r2 = client.post(
            "/auth/token",
            data={"username": "alice@example.com", "password": "secretpw"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert r2.status_code == 200, r2.text
        token = r2.json()["access_token"]
        # Call /auth/me with bearer
        r3 = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r3.status_code == 200, r3.text
        body = r3.json()
        assert body["email"] == "alice@example.com"
        assert body["role"] == "user"

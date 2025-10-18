from fastapi.testclient import TestClient

from src.main import app


def test_register_and_login_sqlite(tmp_path, monkeypatch) -> None:
    # Use temp SQLite file to isolate test
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    with TestClient(app) as client:
        # Register
        r = client.post(
            "/auth/register",
            json={"email": "user@example.com", "password": "pass1234"},
        )
        assert r.status_code == 201, r.text
        # Login
        r2 = client.post(
            "/auth/token",
            data={"username": "user@example.com", "password": "pass1234"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert r2.status_code == 200, r2.text
        token = r2.json().get("access_token")
        assert token and isinstance(token, str)

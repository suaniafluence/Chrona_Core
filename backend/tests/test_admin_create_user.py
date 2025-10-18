import asyncio

from fastapi.testclient import TestClient
from sqlalchemy import text

from src.db import engine
from src.main import app


def _promote_in_db(email: str) -> None:
    async def _run():
        async with engine.begin() as conn:
            await conn.execute(
                text("UPDATE users SET role='admin' WHERE email=:email"),
                {"email": email},
            )

    asyncio.get_event_loop().run_until_complete(_run())


def _login(c: TestClient, email: str, password: str) -> str:
    r = c.post(
        "/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    return r.json()["access_token"]


def test_admin_can_create_user_with_role(tmp_path, monkeypatch) -> None:
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    with TestClient(app) as client:
        # bootstrap admin
        client.post("/auth/register", json={"email": "admin@example.com", "password": "adminpass"})
        _promote_in_db("admin@example.com")
        admin_token = _login(client, "admin@example.com", "adminpass")

        # create user with role admin via endpoint
        r = client.post(
            "/admin/users",
            json={"email": "new@example.com", "password": "newpass123", "role": "admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert r.status_code == 201, r.text
        assert r.json()["role"] == "admin"

        # new admin can call admin route
        new_token = _login(client, "new@example.com", "newpass123")
        ok = client.get("/admin/ping", headers={"Authorization": f"Bearer {new_token}"})
        assert ok.status_code == 200


def test_admin_create_user_invalid_role(tmp_path, monkeypatch) -> None:
    db_file = tmp_path / "test2.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    with TestClient(app) as client:
        client.post("/auth/register", json={"email": "admin2@example.com", "password": "adminpass"})
        _promote_in_db("admin2@example.com")
        admin_token = _login(client, "admin2@example.com", "adminpass")

        r = client.post(
            "/admin/users",
            json={"email": "x@example.com", "password": "pass", "role": "superuser"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert r.status_code == 400


import asyncio

from fastapi.testclient import TestClient
from sqlalchemy import text

from src.db import engine
from src.main import app


def _promote_to_admin(email: str) -> None:
    async def _run():
        async with engine.begin() as conn:
            await conn.execute(text("UPDATE user SET role='admin' WHERE email=:email"), {"email": email})

    asyncio.get_event_loop().run_until_complete(_run())


def test_admin_ping_requires_admin(tmp_path, monkeypatch) -> None:
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    with TestClient(app) as client:
        # Register normal user
        email = "bob@example.com"
        pwd = "pass12345"
        r = client.post("/auth/register", json={"email": email, "password": pwd})
        assert r.status_code == 201

        # Login returns user token (role=user)
        r2 = client.post(
            "/auth/token",
            data={"username": email, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_user = r2.json()["access_token"]

        # Access admin should be forbidden with user token
        r_forbidden = client.get(
            "/admin/ping", headers={"Authorization": f"Bearer {token_user}"}
        )
        assert r_forbidden.status_code in (401, 403)

        # Promote in DB then login again to get a fresh token
        _promote_to_admin(email)
        r3 = client.post(
            "/auth/token",
            data={"username": email, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_admin = r3.json()["access_token"]

        # Now admin route should succeed
        r_ok = client.get("/admin/ping", headers={"Authorization": f"Bearer {token_admin}"})
        assert r_ok.status_code == 200, r_ok.text
        assert r_ok.json().get("pong") is True

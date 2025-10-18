import asyncio

from fastapi.testclient import TestClient
from sqlalchemy import text

from src.db import engine
from src.main import app


def _promote_in_db(email: str) -> None:
    async def _run():
        async with engine.begin() as conn:
            await conn.execute(text("UPDATE user SET role='admin' WHERE email=:email"), {"email": email})

    asyncio.get_event_loop().run_until_complete(_run())


def test_admin_can_promote_user(tmp_path, monkeypatch) -> None:
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    with TestClient(app) as client:
        # Create two users
        a_email, a_pwd = "a@example.com", "aaa11111"
        b_email, b_pwd = "b@example.com", "bbb22222"
        ra = client.post("/auth/register", json={"email": a_email, "password": a_pwd})
        rb = client.post("/auth/register", json={"email": b_email, "password": b_pwd})
        assert ra.status_code == 201 and rb.status_code == 201
        target_id = rb.json()["id"]

        # Promote A to admin directly (bootstrap), fetch token
        _promote_in_db(a_email)
        la = client.post(
            "/auth/token",
            data={"username": a_email, "password": a_pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        admin_token = la.json()["access_token"]

        # Use admin endpoint to promote B
        rp = client.patch(
            f"/admin/users/{target_id}/role",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert rp.status_code == 200, rp.text
        assert rp.json()["role"] == "admin"

        # Now B should access admin route
        lb = client.post(
            "/auth/token",
            data={"username": b_email, "password": b_pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        b_token = lb.json()["access_token"]
        ok = client.get("/admin/ping", headers={"Authorization": f"Bearer {b_token}"})
        assert ok.status_code == 200


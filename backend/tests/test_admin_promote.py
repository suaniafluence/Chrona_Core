import asyncio

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.main import app


def _promote_in_db(email: str):
    """Helper to promote a user to admin role directly in DB."""
    import os

    database_url = os.getenv("DATABASE_URL")

    async def _run():
        engine = create_async_engine(database_url)
        async with engine.begin() as conn:
            await conn.execute(
                text("UPDATE users SET role = 'admin' WHERE email = :email"),
                {"email": email},
            )
        await engine.dispose()

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
        r_token = client.post(
            "/auth/token",
            data={"username": a_email, "password": a_pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        admin_token = r_token.json()["access_token"]

        # Admin promotes B to manager
        r_promote = client.post(
            f"/admin/users/{target_id}/role",
            json={"role": "manager"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert r_promote.status_code == 200
        assert r_promote.json()["role"] == "manager"

        # Verify B's role changed
        r_login_b = client.post(
            "/auth/token",
            data={"username": b_email, "password": b_pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_b = r_login_b.json()["access_token"]
        r_me = client.get(
            "/auth/me", headers={"Authorization": f"Bearer {token_b}"}
        )
        assert r_me.json()["role"] == "manager"

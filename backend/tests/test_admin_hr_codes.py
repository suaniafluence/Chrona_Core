"""Tests for HR code creation and management endpoints."""

import asyncio

from fastapi.testclient import TestClient
from sqlalchemy import text

from src.db import engine
from src.main import app


def _promote_to_admin(email: str) -> None:
    """Promote user to admin role in database."""

    async def _run():
        async with engine.begin() as conn:
            await conn.execute(
                text("UPDATE users SET role='admin' WHERE email=:email"),
                {"email": email},
            )

    asyncio.get_event_loop().run_until_complete(_run())


def test_create_hr_code_requires_admin(tmp_path, monkeypatch) -> None:
    """Test that non-admin users cannot create HR codes."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")

    with TestClient(app) as client:
        # Register normal user
        email = "user@example.com"
        pwd = "pass12345"
        r = client.post("/auth/register", json={"email": email, "password": pwd})
        assert r.status_code == 201

        # Login as normal user
        r2 = client.post(
            "/auth/token",
            data={"username": email, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = r2.json()["access_token"]

        # Try to create HR code - should be forbidden
        r3 = client.post(
            "/admin/hr-codes",
            json={
                "employee_email": "newemployee@example.com",
                "employee_name": "John Doe",
                "expires_in_days": 7,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r3.status_code in (401, 403)


def test_create_hr_code_success(tmp_path, monkeypatch) -> None:
    """Test successful HR code creation."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")

    with TestClient(app) as client:
        # Register and promote admin
        admin_email = "admin@example.com"
        pwd = "pass12345"
        r = client.post("/auth/register", json={"email": admin_email, "password": pwd})
        assert r.status_code == 201

        _promote_to_admin(admin_email)

        # Login as admin
        r2 = client.post(
            "/auth/token",
            data={"username": admin_email, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = r2.json()["access_token"]

        # Create HR code
        employee_email = "employee@example.com"
        employee_name = "Jane Smith"
        r3 = client.post(
            "/admin/hr-codes",
            json={
                "employee_email": employee_email,
                "employee_name": employee_name,
                "expires_in_days": 7,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert r3.status_code == 201, r3.text
        data = r3.json()
        assert data["code"].startswith("EMPL-")
        assert data["employee_email"] == employee_email
        assert data["employee_name"] == employee_name
        assert data["is_used"] is False
        assert data["expires_at"] is not None


def test_create_hr_code_with_minimal_data(tmp_path, monkeypatch) -> None:
    """Test HR code creation with only required fields."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")

    with TestClient(app) as client:
        # Setup admin
        admin_email = "admin@example.com"
        pwd = "pass12345"
        client.post("/auth/register", json={"email": admin_email, "password": pwd})
        _promote_to_admin(admin_email)

        r2 = client.post(
            "/auth/token",
            data={"username": admin_email, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = r2.json()["access_token"]

        # Create HR code with only email
        r3 = client.post(
            "/admin/hr-codes",
            json={"employee_email": "minimal@example.com"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert r3.status_code == 201, r3.text
        data = r3.json()
        assert data["employee_email"] == "minimal@example.com"
        assert data["employee_name"] is None
        assert data["is_used"] is False


def test_create_hr_code_invalid_email(tmp_path, monkeypatch) -> None:
    """Test HR code creation with invalid email."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")

    with TestClient(app) as client:
        # Setup admin
        admin_email = "admin@example.com"
        pwd = "pass12345"
        client.post("/auth/register", json={"email": admin_email, "password": pwd})
        _promote_to_admin(admin_email)

        r2 = client.post(
            "/auth/token",
            data={"username": admin_email, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = r2.json()["access_token"]

        # Try to create with invalid email
        r3 = client.post(
            "/admin/hr-codes",
            json={
                "employee_email": "not-an-email",
                "expires_in_days": 7,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert r3.status_code == 422  # Validation error


def test_create_hr_code_deduplication(tmp_path, monkeypatch) -> None:
    """Test that creating code for same email returns existing code."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")

    with TestClient(app) as client:
        # Setup admin
        admin_email = "admin@example.com"
        pwd = "pass12345"
        client.post("/auth/register", json={"email": admin_email, "password": pwd})
        _promote_to_admin(admin_email)

        r2 = client.post(
            "/auth/token",
            data={"username": admin_email, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = r2.json()["access_token"]

        # Create first code
        employee_email = "dedup@example.com"
        r3 = client.post(
            "/admin/hr-codes",
            json={
                "employee_email": employee_email,
                "expires_in_days": 7,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r3.status_code == 201
        first_code = r3.json()["code"]

        # Create code for same email again - should return same code
        r4 = client.post(
            "/admin/hr-codes",
            json={
                "employee_email": employee_email,
                "expires_in_days": 7,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r4.status_code == 201
        second_code = r4.json()["code"]

        # Codes should be identical
        assert first_code == second_code


def test_create_hr_code_different_expiration(tmp_path, monkeypatch) -> None:
    """Test HR code creation with different expiration days."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")

    with TestClient(app) as client:
        # Setup admin
        admin_email = "admin@example.com"
        pwd = "pass12345"
        client.post("/auth/register", json={"email": admin_email, "password": pwd})
        _promote_to_admin(admin_email)

        r2 = client.post(
            "/auth/token",
            data={"username": admin_email, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = r2.json()["access_token"]

        # Test various expiration days
        for days in [1, 7, 14, 30]:
            r3 = client.post(
                "/admin/hr-codes",
                json={
                    "employee_email": f"exp{days}@example.com",
                    "expires_in_days": days,
                },
                headers={"Authorization": f"Bearer {token}"},
            )

            assert r3.status_code == 201, f"Failed for {days} days"
            data = r3.json()
            assert data["expires_at"] is not None


def test_create_hr_code_invalid_expiration_days(tmp_path, monkeypatch) -> None:
    """Test HR code creation with invalid expiration days."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")

    with TestClient(app) as client:
        # Setup admin
        admin_email = "admin@example.com"
        pwd = "pass12345"
        client.post("/auth/register", json={"email": admin_email, "password": pwd})
        _promote_to_admin(admin_email)

        r2 = client.post(
            "/auth/token",
            data={"username": admin_email, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = r2.json()["access_token"]

        # Test invalid expiration days
        for days in [0, -1, 31, 100]:
            r3 = client.post(
                "/admin/hr-codes",
                json={
                    "employee_email": f"invalid{days}@example.com",
                    "expires_in_days": days,
                },
                headers={"Authorization": f"Bearer {token}"},
            )

            assert r3.status_code == 422, f"Should fail for {days} days"


def test_list_hr_codes(tmp_path, monkeypatch) -> None:
    """Test listing HR codes."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")

    with TestClient(app) as client:
        # Setup admin
        admin_email = "admin@example.com"
        pwd = "pass12345"
        client.post("/auth/register", json={"email": admin_email, "password": pwd})
        _promote_to_admin(admin_email)

        r2 = client.post(
            "/auth/token",
            data={"username": admin_email, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = r2.json()["access_token"]

        # Create multiple codes
        for i in range(3):
            client.post(
                "/admin/hr-codes",
                json={
                    "employee_email": f"emp{i}@example.com",
                    "expires_in_days": 7,
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        # List codes
        r3 = client.get(
            "/admin/hr-codes",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert r3.status_code == 200
        data = r3.json()
        assert len(data) >= 3  # At least the 3 we created


def test_get_hr_code_qr_data(tmp_path, monkeypatch) -> None:
    """Test getting QR data for an HR code."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")

    with TestClient(app) as client:
        # Setup admin
        admin_email = "admin@example.com"
        pwd = "pass12345"
        client.post("/auth/register", json={"email": admin_email, "password": pwd})
        _promote_to_admin(admin_email)

        r2 = client.post(
            "/auth/token",
            data={"username": admin_email, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = r2.json()["access_token"]

        # Create code
        employee_email = "qrtest@example.com"
        r3 = client.post(
            "/admin/hr-codes",
            json={
                "employee_email": employee_email,
                "employee_name": "QR Test",
                "expires_in_days": 7,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r3.status_code == 201
        code_id = r3.json()["id"]

        # Get QR data
        r4 = client.get(
            f"/admin/hr-codes/{code_id}/qr-data",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert r4.status_code == 200, r4.text
        data = r4.json()
        assert data["hr_code"].startswith("EMPL-")
        assert data["employee_email"] == employee_email
        assert data["employee_name"] == "QR Test"
        assert "api_url" in data

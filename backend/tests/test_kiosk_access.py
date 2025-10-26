"""Tests for kiosk access control system."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.core.security import hash_password
from src.main import app
from src.models.kiosk import Kiosk
from src.models.kiosk_access import KioskAccess
from src.models.user import User
from src.services.access_control import check_kiosk_access, grant_kiosk_access

client = TestClient(app)


@pytest.fixture
def admin_user(test_session: Session) -> User:
    """Create an admin user."""
    admin = User(
        email="admin@example.com",
        hashed_password=hash_password("adminpass"),
        role="admin",
    )
    test_session.add(admin)
    test_session.commit()
    test_session.refresh(admin)
    return admin


@pytest.fixture
def regular_user(test_session: Session) -> User:
    """Create a regular user."""
    user = User(
        email="user@example.com",
        hashed_password=hash_password("userpass"),
        role="user",
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


@pytest.fixture
def public_kiosk(test_session: Session) -> Kiosk:
    """Create a public access kiosk."""
    kiosk = Kiosk(
        kiosk_name="Public-Kiosk",
        location="Main Entrance",
        device_fingerprint="public-device",
        api_key_hash=hash_password("public-key"),
        is_active=True,
        access_mode="public",
    )
    test_session.add(kiosk)
    test_session.commit()
    test_session.refresh(kiosk)
    return kiosk


@pytest.fixture
def whitelist_kiosk(test_session: Session) -> Kiosk:
    """Create a whitelist access kiosk."""
    kiosk = Kiosk(
        kiosk_name="Whitelist-Kiosk",
        location="Executive Floor",
        device_fingerprint="whitelist-device",
        api_key_hash=hash_password("whitelist-key"),
        is_active=True,
        access_mode="whitelist",
    )
    test_session.add(kiosk)
    test_session.commit()
    test_session.refresh(kiosk)
    return kiosk


@pytest.fixture
def blacklist_kiosk(test_session: Session) -> Kiosk:
    """Create a blacklist access kiosk."""
    kiosk = Kiosk(
        kiosk_name="Blacklist-Kiosk",
        location="General Area",
        device_fingerprint="blacklist-device",
        api_key_hash=hash_password("blacklist-key"),
        is_active=True,
        access_mode="blacklist",
    )
    test_session.add(kiosk)
    test_session.commit()
    test_session.refresh(kiosk)
    return kiosk


# Access control service tests


def test_public_kiosk_allows_everyone(
    test_session: Session, public_kiosk: Kiosk, regular_user: User
):
    """Test that public kiosks allow everyone."""
    authorized, reason = check_kiosk_access(
        regular_user.id, public_kiosk.id, test_session
    )
    assert authorized is True
    assert "public" in reason.lower()


def test_whitelist_kiosk_denies_unauthorized(
    test_session: Session, whitelist_kiosk: Kiosk, regular_user: User
):
    """Test that whitelist kiosks deny users without explicit permission."""
    authorized, reason = check_kiosk_access(
        regular_user.id, whitelist_kiosk.id, test_session
    )
    assert authorized is False
    assert "non autorisé" in reason.lower()


def test_whitelist_kiosk_allows_authorized(
    test_session: Session,
    whitelist_kiosk: Kiosk,
    regular_user: User,
    admin_user: User,
):
    """Test that whitelist kiosks allow explicitly authorized users."""
    # Grant access
    grant_kiosk_access(
        kiosk_id=whitelist_kiosk.id,
        user_id=regular_user.id,
        granted_by_admin_id=admin_user.id,
        expires_at=None,
        session=test_session,
    )

    # Check access
    authorized, reason = check_kiosk_access(
        regular_user.id, whitelist_kiosk.id, test_session
    )
    assert authorized is True
    assert "autorisé" in reason.lower()


def test_blacklist_kiosk_allows_non_blocked(
    test_session: Session, blacklist_kiosk: Kiosk, regular_user: User
):
    """Test that blacklist kiosks allow users not explicitly blocked."""
    authorized, reason = check_kiosk_access(
        regular_user.id, blacklist_kiosk.id, test_session
    )
    assert authorized is True
    assert "non bloqué" in reason.lower() or "autorisé" in reason.lower()


def test_blacklist_kiosk_denies_blocked(
    test_session: Session,
    blacklist_kiosk: Kiosk,
    regular_user: User,
    admin_user: User,
):
    """Test that blacklist kiosks deny explicitly blocked users."""
    # Block user
    access = KioskAccess(
        kiosk_id=blacklist_kiosk.id,
        user_id=regular_user.id,
        granted=False,  # Blocked
        granted_by_admin_id=admin_user.id,
    )
    test_session.add(access)
    test_session.commit()

    # Check access
    authorized, reason = check_kiosk_access(
        regular_user.id, blacklist_kiosk.id, test_session
    )
    assert authorized is False
    assert "bloqué" in reason.lower()


def test_inactive_kiosk_denies_all(
    test_session: Session, public_kiosk: Kiosk, regular_user: User
):
    """Test that inactive kiosks deny all access."""
    public_kiosk.is_active = False
    test_session.add(public_kiosk)
    test_session.commit()

    authorized, reason = check_kiosk_access(
        regular_user.id, public_kiosk.id, test_session
    )
    assert authorized is False
    assert "désactivé" in reason.lower()


# Admin API tests


def test_admin_can_change_kiosk_access_mode(
    test_session: Session, admin_user: User, public_kiosk: Kiosk
):
    """Test that admin can change kiosk access mode."""
    # Login as admin
    response = client.post(
        "/auth/token",
        data={"username": "admin@example.com", "password": "adminpass"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Change to whitelist mode
    response = client.patch(
        f"/admin/kiosks/{public_kiosk.id}/access-mode",
        json={"access_mode": "whitelist"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["kiosk"]["access_mode"] == "whitelist"

    # Verify in database
    test_session.refresh(public_kiosk)
    assert public_kiosk.access_mode == "whitelist"


def test_admin_can_grant_access(
    test_session: Session,
    admin_user: User,
    whitelist_kiosk: Kiosk,
    regular_user: User,
):
    """Test that admin can grant access to users."""
    # Login as admin
    response = client.post(
        "/auth/token",
        data={"username": "admin@example.com", "password": "adminpass"},
    )
    token = response.json()["access_token"]

    # Grant access
    response = client.post(
        f"/admin/kiosks/{whitelist_kiosk.id}/grant-access",
        json={"user_id": regular_user.id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify in database
    access = (
        test_session.query(KioskAccess)
        .filter(
            KioskAccess.kiosk_id == whitelist_kiosk.id,
            KioskAccess.user_id == regular_user.id,
        )
        .first()
    )
    assert access is not None
    assert access.granted is True


def test_admin_can_revoke_access(
    test_session: Session,
    admin_user: User,
    whitelist_kiosk: Kiosk,
    regular_user: User,
):
    """Test that admin can revoke access from users."""
    # Grant access first
    grant_kiosk_access(
        kiosk_id=whitelist_kiosk.id,
        user_id=regular_user.id,
        granted_by_admin_id=admin_user.id,
        expires_at=None,
        session=test_session,
    )

    # Login as admin
    response = client.post(
        "/auth/token",
        data={"username": "admin@example.com", "password": "adminpass"},
    )
    token = response.json()["access_token"]

    # Revoke access
    response = client.delete(
        f"/admin/kiosks/{whitelist_kiosk.id}/revoke-access/{regular_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify in database
    access = (
        test_session.query(KioskAccess)
        .filter(
            KioskAccess.kiosk_id == whitelist_kiosk.id,
            KioskAccess.user_id == regular_user.id,
        )
        .first()
    )
    assert access is None


def test_admin_can_get_kiosk_access_list(
    test_session: Session,
    admin_user: User,
    whitelist_kiosk: Kiosk,
    regular_user: User,
):
    """Test that admin can get list of users authorized for a kiosk."""
    # Grant access to user
    grant_kiosk_access(
        kiosk_id=whitelist_kiosk.id,
        user_id=regular_user.id,
        granted_by_admin_id=admin_user.id,
        expires_at=None,
        session=test_session,
    )

    # Login as admin
    response = client.post(
        "/auth/token",
        data={"username": "admin@example.com", "password": "adminpass"},
    )
    token = response.json()["access_token"]

    # Get access list
    response = client.get(
        f"/admin/kiosks/{whitelist_kiosk.id}/access",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["kiosk_id"] == whitelist_kiosk.id
    assert data["access_mode"] == "whitelist"
    assert len(data["authorized_users"]) == 1
    assert data["authorized_users"][0]["user_id"] == regular_user.id


def test_non_admin_cannot_manage_access(
    test_session: Session, regular_user: User, whitelist_kiosk: Kiosk
):
    """Test that non-admin users cannot manage kiosk access."""
    # Login as regular user
    response = client.post(
        "/auth/token",
        data={"username": "user@example.com", "password": "userpass"},
    )
    token = response.json()["access_token"]

    # Try to change access mode (should fail)
    response = client.patch(
        f"/admin/kiosks/{whitelist_kiosk.id}/access-mode",
        json={"access_mode": "public"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403  # Forbidden

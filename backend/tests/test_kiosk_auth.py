"""Tests for kiosk authentication."""

import pytest
from httpx import AsyncClient
from sqlmodel import select

from src.models.kiosk import Kiosk
from src.routers.kiosk_auth import generate_kiosk_api_key, hash_kiosk_api_key


@pytest.mark.asyncio
async def test_generate_kiosk_api_key():
    """Test API key generation produces unique random keys."""
    key1 = generate_kiosk_api_key()
    key2 = generate_kiosk_api_key()

    assert isinstance(key1, str)
    assert isinstance(key2, str)
    assert len(key1) > 32  # URL-safe base64 encoding adds padding
    assert key1 != key2  # Should be unique


@pytest.mark.asyncio
async def test_hash_and_verify_api_key():
    """Test API key hashing and verification."""
    from src.routers.kiosk_auth import verify_kiosk_api_key

    api_key = generate_kiosk_api_key()
    hashed = hash_kiosk_api_key(api_key)

    assert verify_kiosk_api_key(api_key, hashed) is True
    assert verify_kiosk_api_key("wrong-key", hashed) is False


@pytest.mark.asyncio
async def test_admin_generate_kiosk_api_key(
    async_client: AsyncClient, admin_headers: dict, test_db
):
    """Test admin endpoint to generate kiosk API key."""
    # Create a kiosk first
    from datetime import datetime, timezone

    kiosk = Kiosk(
        kiosk_name="Test-Kiosk-Auth",
        location="Test Location",
        device_fingerprint="test-fingerprint-auth",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    test_db.add(kiosk)
    await test_db.commit()
    await test_db.refresh(kiosk)

    # Generate API key
    response = await async_client.post(
        f"/admin/kiosks/{kiosk.id}/generate-api-key",
        headers=admin_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "api_key" in data
    assert "kiosk_id" in data
    assert data["kiosk_id"] == kiosk.id
    assert len(data["api_key"]) > 32

    # Verify the hash was stored in database
    await test_db.refresh(kiosk)
    assert kiosk.api_key_hash is not None


@pytest.mark.asyncio
async def test_punch_validate_requires_api_key(async_client: AsyncClient, test_db):
    """Test that /punch/validate requires API key."""
    response = await async_client.post(
        "/punch/validate",
        json={
            "qr_token": "fake-token",
            "kiosk_id": 1,
            "punch_type": "clock_in",
        },
    )

    assert response.status_code == 401
    assert "API key" in response.json()["detail"]


@pytest.mark.asyncio
async def test_punch_validate_with_invalid_api_key(async_client: AsyncClient, test_db):
    """Test that /punch/validate rejects invalid API key."""
    response = await async_client.post(
        "/punch/validate",
        json={
            "qr_token": "fake-token",
            "kiosk_id": 1,
            "punch_type": "clock_in",
        },
        headers={"X-Kiosk-API-Key": "invalid-key"},
    )

    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]


@pytest.mark.asyncio
async def test_punch_validate_with_inactive_kiosk(async_client: AsyncClient, test_db):
    """Test that /punch/validate rejects API key from inactive kiosk."""
    from datetime import datetime, timezone

    # Create kiosk with API key but inactive
    api_key = generate_kiosk_api_key()
    kiosk = Kiosk(
        kiosk_name="Inactive-Kiosk",
        location="Test",
        device_fingerprint="inactive-fingerprint",
        api_key_hash=hash_kiosk_api_key(api_key),
        is_active=False,  # Inactive
        created_at=datetime.now(timezone.utc),
    )
    test_db.add(kiosk)
    await test_db.commit()
    await test_db.refresh(kiosk)

    response = await async_client.post(
        "/punch/validate",
        json={
            "qr_token": "fake-token",
            "kiosk_id": kiosk.id,
            "punch_type": "clock_in",
        },
        headers={"X-Kiosk-API-Key": api_key},
    )

    assert response.status_code == 403
    assert "not active" in response.json()["detail"]


@pytest.mark.asyncio
async def test_punch_validate_kiosk_id_mismatch(
    async_client: AsyncClient, test_db, test_user, test_device
):
    """Test that kiosk_id in request must match authenticated kiosk."""
    from datetime import datetime, timezone

    from src.security import create_ephemeral_qr_token

    # Create two kiosks with API keys
    api_key_1 = generate_kiosk_api_key()
    kiosk_1 = Kiosk(
        kiosk_name="Kiosk-1",
        location="Location 1",
        device_fingerprint="fingerprint-1",
        api_key_hash=hash_kiosk_api_key(api_key_1),
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    api_key_2 = generate_kiosk_api_key()
    kiosk_2 = Kiosk(
        kiosk_name="Kiosk-2",
        location="Location 2",
        device_fingerprint="fingerprint-2",
        api_key_hash=hash_kiosk_api_key(api_key_2),
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    test_db.add(kiosk_1)
    test_db.add(kiosk_2)
    await test_db.commit()
    await test_db.refresh(kiosk_1)
    await test_db.refresh(kiosk_2)

    # Generate valid QR token
    qr_token, payload = create_ephemeral_qr_token(test_user.id, test_device.id)

    # Store token in tracking table (normally done by /punch/request-token)
    from src.models.token_tracking import TokenTracking

    token_tracking = TokenTracking(
        jti=payload["jti"],
        nonce=payload["nonce"],
        user_id=test_user.id,
        device_id=test_device.id,
        issued_at=payload["iat"],
        expires_at=payload["exp"],
        consumed_at=None,
        consumed_by_kiosk_id=None,
    )
    test_db.add(token_tracking)
    await test_db.commit()

    # Try to validate with kiosk_1's API key but kiosk_2's ID
    response = await async_client.post(
        "/punch/validate",
        json={
            "qr_token": qr_token,
            "kiosk_id": kiosk_2.id,  # Different kiosk ID
            "punch_type": "clock_in",
        },
        headers={"X-Kiosk-API-Key": api_key_1},  # Using kiosk_1's key
    )

    assert response.status_code == 403
    assert "does not match authenticated kiosk" in response.json()["detail"]

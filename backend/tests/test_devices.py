"""Tests for device management endpoints."""

import pytest
from fastapi import status
from httpx import AsyncClient

from src.main import app
from src.models.device import Device
from src.models.user import User


@pytest.mark.asyncio
async def test_register_device_success(async_client: AsyncClient, test_user: User, auth_headers: dict):
    """Test successful device registration."""
    device_data = {
        "device_fingerprint": "test-device-fp-12345",
        "device_name": "iPhone 14 Pro",
        "attestation_data": '{"nonce": "abc123", "timestamp": 1234567890}',
    }

    response = await async_client.post(
        "/devices/register",
        json=device_data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["device_fingerprint"] == device_data["device_fingerprint"]
    assert data["device_name"] == device_data["device_name"]
    assert data["user_id"] == test_user.id
    assert data["is_revoked"] is False
    assert "id" in data
    assert "registered_at" in data


@pytest.mark.asyncio
async def test_register_device_duplicate_fingerprint(
    async_client: AsyncClient, test_user: User, auth_headers: dict
):
    """Test that duplicate device fingerprints are rejected."""
    device_data = {
        "device_fingerprint": "duplicate-fp-67890",
        "device_name": "Test Device",
    }

    # Register first device
    response1 = await async_client.post(
        "/devices/register",
        json=device_data,
        headers=auth_headers,
    )
    assert response1.status_code == status.HTTP_201_CREATED

    # Try to register duplicate
    response2 = await async_client.post(
        "/devices/register",
        json=device_data,
        headers=auth_headers,
    )
    assert response2.status_code == status.HTTP_409_CONFLICT
    assert "already registered" in response2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_device_unauthorized(async_client: AsyncClient):
    """Test that device registration requires authentication."""
    device_data = {
        "device_fingerprint": "test-fp",
        "device_name": "Test Device",
    }

    response = await async_client.post("/devices/register", json=device_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_list_devices(async_client: AsyncClient, test_user: User, auth_headers: dict):
    """Test listing user's devices."""
    # Register two devices
    devices_data = [
        {"device_fingerprint": "fp-1", "device_name": "Device 1"},
        {"device_fingerprint": "fp-2", "device_name": "Device 2"},
    ]

    for device_data in devices_data:
        await async_client.post(
            "/devices/register",
            json=device_data,
            headers=auth_headers,
        )

    # List devices
    response = await async_client.get("/devices/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 2
    assert all(d["user_id"] == test_user.id for d in data)
    assert all(d["is_revoked"] is False for d in data)


@pytest.mark.asyncio
async def test_list_devices_exclude_revoked(
    async_client: AsyncClient, test_user: User, auth_headers: dict
):
    """Test that revoked devices are excluded by default."""
    # Register and revoke a device
    device_data = {"device_fingerprint": "fp-revoked", "device_name": "Revoked Device"}
    reg_response = await async_client.post(
        "/devices/register",
        json=device_data,
        headers=auth_headers,
    )
    device_id = reg_response.json()["id"]

    await async_client.post(
        f"/devices/{device_id}/revoke",
        headers=auth_headers,
    )

    # Register active device
    await async_client.post(
        "/devices/register",
        json={"device_fingerprint": "fp-active", "device_name": "Active Device"},
        headers=auth_headers,
    )

    # List devices (exclude revoked by default)
    response = await async_client.get("/devices/me", headers=auth_headers)
    data = response.json()
    assert len(data) == 1
    assert data[0]["device_name"] == "Active Device"

    # List devices including revoked
    response = await async_client.get(
        "/devices/me?include_revoked=true", headers=auth_headers
    )
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_revoke_device_success(
    async_client: AsyncClient, test_user: User, auth_headers: dict
):
    """Test successful device revocation."""
    # Register device
    device_data = {"device_fingerprint": "fp-to-revoke", "device_name": "Test Device"}
    reg_response = await async_client.post(
        "/devices/register",
        json=device_data,
        headers=auth_headers,
    )
    device_id = reg_response.json()["id"]

    # Revoke device
    response = await async_client.post(
        f"/devices/{device_id}/revoke",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == device_id
    assert data["is_revoked"] is True


@pytest.mark.asyncio
async def test_revoke_device_already_revoked(
    async_client: AsyncClient, test_user: User, auth_headers: dict
):
    """Test that revoking an already-revoked device fails."""
    # Register and revoke device
    device_data = {"device_fingerprint": "fp-revoked-2", "device_name": "Test Device"}
    reg_response = await async_client.post(
        "/devices/register",
        json=device_data,
        headers=auth_headers,
    )
    device_id = reg_response.json()["id"]

    await async_client.post(f"/devices/{device_id}/revoke", headers=auth_headers)

    # Try to revoke again
    response = await async_client.post(
        f"/devices/{device_id}/revoke",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already revoked" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_revoke_device_not_owned(
    async_client: AsyncClient, test_user: User, auth_headers: dict, test_db
):
    """Test that users cannot revoke devices they don't own."""
    # Create another user and their device
    from src.security import get_password_hash

    other_user = User(email="other@example.com", hashed_password=get_password_hash("password"))
    test_db.add(other_user)
    await test_db.commit()
    await test_db.refresh(other_user)

    other_device = Device(
        user_id=other_user.id,
        device_fingerprint="other-fp",
        device_name="Other Device",
    )
    test_db.add(other_device)
    await test_db.commit()
    await test_db.refresh(other_device)

    # Try to revoke other user's device
    response = await async_client.post(
        f"/devices/{other_device.id}/revoke",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_revoke_nonexistent_device(
    async_client: AsyncClient, auth_headers: dict
):
    """Test revoking a device that doesn't exist."""
    response = await async_client.post(
        "/devices/99999/revoke",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

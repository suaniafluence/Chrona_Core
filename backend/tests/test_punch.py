"""Tests for punch tracking endpoints."""

import pytest
from fastapi import status
from httpx import AsyncClient

from src.models.device import Device
from src.models.kiosk import Kiosk
from src.models.user import User


@pytest.mark.asyncio
async def test_request_qr_token_success(
    async_client: AsyncClient,
    test_user: User,
    test_device: Device,
    auth_headers: dict,
):
    """Test successful QR token request."""
    response = await async_client.post(
        "/punch/request-token",
        json={"device_id": test_device.id},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "qr_token" in data
    assert "expires_in" in data
    assert "expires_at" in data
    assert data["expires_in"] > 0
    assert len(data["qr_token"]) > 0


@pytest.mark.asyncio
async def test_request_qr_token_device_not_found(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test QR token request with non-existent device."""
    response = await async_client.post(
        "/punch/request-token",
        json={"device_id": 99999},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_request_qr_token_revoked_device(
    async_client: AsyncClient,
    test_device: Device,
    auth_headers: dict,
):
    """Test QR token request with revoked device."""
    # Revoke device first
    await async_client.post(
        f"/devices/{test_device.id}/revoke",
        headers=auth_headers,
    )

    # Try to request token
    response = await async_client.post(
        "/punch/request-token",
        json={"device_id": test_device.id},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "revoked" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_request_qr_token_unauthorized(
    async_client: AsyncClient,
    test_device: Device,
):
    """Test QR token request without authentication."""
    response = await async_client.post(
        "/punch/request-token",
        json={"device_id": test_device.id},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_validate_punch_success(
    async_client: AsyncClient,
    test_user: User,
    test_device: Device,
    test_kiosk: Kiosk,
    auth_headers: dict,
    kiosk_headers: dict,
):
    """Test successful punch validation."""
    # Request QR token
    token_response = await async_client.post(
        "/punch/request-token",
        json={"device_id": test_device.id},
        headers=auth_headers,
    )
    qr_token = token_response.json()["qr_token"]

    # Validate punch
    validate_response = await async_client.post(
        "/punch/validate",
        json={
            "qr_token": qr_token,
            "kiosk_id": test_kiosk.id,
            "punch_type": "clock_in",
        },
        headers=kiosk_headers,
    )

    assert validate_response.status_code == status.HTTP_200_OK
    data = validate_response.json()
    assert data["success"] is True
    assert data["user_id"] == test_user.id
    assert data["device_id"] == test_device.id
    assert "punch_id" in data
    assert "punched_at" in data


@pytest.mark.asyncio
async def test_validate_punch_invalid_token(
    async_client: AsyncClient,
    test_kiosk: Kiosk,
    kiosk_headers: dict,
):
    """Test punch validation with invalid JWT token."""
    response = await async_client.post(
        "/punch/validate",
        json={
            "qr_token": "invalid.jwt.token",
            "kiosk_id": test_kiosk.id,
            "punch_type": "clock_in",
        },
        headers=kiosk_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_validate_punch_replay_attack(
    async_client: AsyncClient,
    test_device: Device,
    test_kiosk: Kiosk,
    auth_headers: dict,
    kiosk_headers: dict,
):
    """Test that replay attacks are prevented."""
    # Request QR token
    token_response = await async_client.post(
        "/punch/request-token",
        json={"device_id": test_device.id},
        headers=auth_headers,
    )
    qr_token = token_response.json()["qr_token"]

    # First validation (should succeed)
    first_response = await async_client.post(
        "/punch/validate",
        json={
            "qr_token": qr_token,
            "kiosk_id": test_kiosk.id,
            "punch_type": "clock_in",
        },
        headers=kiosk_headers,
    )
    assert first_response.status_code == status.HTTP_200_OK

    # Second validation with same token (should fail - replay attack)
    second_response = await async_client.post(
        "/punch/validate",
        json={
            "qr_token": qr_token,
            "kiosk_id": test_kiosk.id,
            "punch_type": "clock_out",
        },
        headers=kiosk_headers,
    )

    assert second_response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already been used" in second_response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_validate_punch_inactive_kiosk(
    async_client: AsyncClient,
    test_device: Device,
    test_kiosk: Kiosk,
    test_db,
    auth_headers: dict,
    kiosk_headers: dict,
):
    """Test punch validation with inactive kiosk."""
    # Request QR token
    token_response = await async_client.post(
        "/punch/request-token",
        json={"device_id": test_device.id},
        headers=auth_headers,
    )
    qr_token = token_response.json()["qr_token"]

    # Deactivate kiosk
    test_kiosk.is_active = False
    test_db.add(test_kiosk)
    await test_db.commit()

    # Try to validate
    response = await async_client.post(
        "/punch/validate",
        json={
            "qr_token": qr_token,
            "kiosk_id": test_kiosk.id,
            "punch_type": "clock_in",
        },
        headers=kiosk_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "not active" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_validate_punch_revoked_device(
    async_client: AsyncClient,
    test_device: Device,
    test_kiosk: Kiosk,
    test_db,
    auth_headers: dict,
    kiosk_headers: dict,
):
    """Test punch validation with revoked device after token generation."""
    # Request QR token
    token_response = await async_client.post(
        "/punch/request-token",
        json={"device_id": test_device.id},
        headers=auth_headers,
    )
    qr_token = token_response.json()["qr_token"]

    # Revoke device
    test_device.is_revoked = True
    test_db.add(test_device)
    await test_db.commit()

    # Try to validate (should fail)
    response = await async_client.post(
        "/punch/validate",
        json={
            "qr_token": qr_token,
            "kiosk_id": test_kiosk.id,
            "punch_type": "clock_in",
        },
        headers=kiosk_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "revoked" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_punch_history_success(
    async_client: AsyncClient,
    test_user: User,
    test_device: Device,
    test_kiosk: Kiosk,
    auth_headers: dict,
    kiosk_headers: dict,
):
    """Test getting punch history."""
    # Create multiple punches
    for punch_type in ["clock_in", "clock_out", "clock_in"]:
        token_response = await async_client.post(
            "/punch/request-token",
            json={"device_id": test_device.id},
            headers=auth_headers,
        )
        qr_token = token_response.json()["qr_token"]

        await async_client.post(
            "/punch/validate",
            json={
                "qr_token": qr_token,
                "kiosk_id": test_kiosk.id,
                "punch_type": punch_type,
            },
        headers=kiosk_headers,
    )

    # Get history
    response = await async_client.get(
        "/punch/history",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    # Check that all punches belong to test_user
    assert all(p["user_id"] == test_user.id for p in data)
    # Check descending order by timestamp
    timestamps = [p["punched_at"] for p in data]
    assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.asyncio
async def test_get_punch_history_pagination(
    async_client: AsyncClient,
    test_device: Device,
    test_kiosk: Kiosk,
    auth_headers: dict,
    kiosk_headers: dict,
):
    """Test punch history pagination."""
    # Create 5 punches
    for i in range(5):
        token_response = await async_client.post(
            "/punch/request-token",
            json={"device_id": test_device.id},
            headers=auth_headers,
        )
        qr_token = token_response.json()["qr_token"]

        await async_client.post(
            "/punch/validate",
            json={
                "qr_token": qr_token,
                "kiosk_id": test_kiosk.id,
                "punch_type": "clock_in" if i % 2 == 0 else "clock_out",
            },
        headers=kiosk_headers,
    )

    # Get first 2 punches
    response1 = await async_client.get(
        "/punch/history?limit=2",
        headers=auth_headers,
    )
    assert len(response1.json()) == 2

    # Get next 2 punches (offset=2)
    response2 = await async_client.get(
        "/punch/history?limit=2&offset=2",
        headers=auth_headers,
    )
    assert len(response2.json()) == 2

    # Get remaining punch (offset=4)
    response3 = await async_client.get(
        "/punch/history?limit=2&offset=4",
        headers=auth_headers,
    )
    assert len(response3.json()) == 1


@pytest.mark.asyncio
async def test_get_punch_history_empty(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test punch history when no punches exist."""
    response = await async_client.get(
        "/punch/history",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_punch_history_unauthorized(
    async_client: AsyncClient,
):
    """Test punch history without authentication."""
    response = await async_client.get("/punch/history")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

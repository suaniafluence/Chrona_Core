"""Tests for admin kiosk management endpoints."""

import pytest
from fastapi import status
from httpx import AsyncClient

from src.models.kiosk import Kiosk


@pytest.mark.asyncio
async def test_admin_list_kiosks(
    async_client: AsyncClient,
    test_kiosk: Kiosk,
    admin_headers: dict,
):
    """Test admin can list all kiosks."""
    response = await async_client.get("/admin/kiosks", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(k["id"] == test_kiosk.id for k in data)


@pytest.mark.asyncio
async def test_admin_list_kiosks_filter_active(
    async_client: AsyncClient,
    test_kiosk: Kiosk,
    admin_headers: dict,
):
    """Test admin can filter kiosks by active status."""
    response = await async_client.get(
        "/admin/kiosks?is_active=true",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(k["is_active"] is True for k in data)


@pytest.mark.asyncio
async def test_admin_create_kiosk_success(
    async_client: AsyncClient,
    admin_headers: dict,
):
    """Test admin can create a new kiosk."""
    kiosk_data = {
        "kiosk_name": "New Kiosk",
        "location": "Main Lobby",
        "device_fingerprint": "new-kiosk-fp-789",
        "public_key": "-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----",
    }

    response = await async_client.post(
        "/admin/kiosks",
        json=kiosk_data,
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["kiosk_name"] == kiosk_data["kiosk_name"]
    assert data["location"] == kiosk_data["location"]
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    # Contract: creation does NOT return api_key
    assert "api_key" not in data


@pytest.mark.asyncio
async def test_admin_create_kiosk_duplicate_name(
    async_client: AsyncClient,
    test_kiosk: Kiosk,
    admin_headers: dict,
):
    """Test that duplicate kiosk names are rejected."""
    kiosk_data = {
        "kiosk_name": test_kiosk.kiosk_name,  # Duplicate
        "location": "Different Location",
        "device_fingerprint": "different-fp",
    }

    response = await async_client.post(
        "/admin/kiosks",
        json=kiosk_data,
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_admin_create_kiosk_duplicate_fingerprint(
    async_client: AsyncClient,
    test_kiosk: Kiosk,
    admin_headers: dict,
):
    """Test that duplicate kiosk fingerprints are rejected."""
    kiosk_data = {
        "kiosk_name": "Different Name",
        "location": "Different Location",
        "device_fingerprint": test_kiosk.device_fingerprint,  # Duplicate
    }

    response = await async_client.post(
        "/admin/kiosks",
        json=kiosk_data,
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_admin_update_kiosk_success(
    async_client: AsyncClient,
    test_kiosk: Kiosk,
    admin_headers: dict,
):
    """Test admin can update a kiosk."""
    update_data = {
        "location": "Updated Location",
        "is_active": False,
    }

    response = await async_client.patch(
        f"/admin/kiosks/{test_kiosk.id}",
        json=update_data,
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_kiosk.id
    assert data["location"] == update_data["location"]
    assert data["is_active"] == update_data["is_active"]


@pytest.mark.asyncio
async def test_admin_update_kiosk_partial(
    async_client: AsyncClient,
    test_kiosk: Kiosk,
    admin_headers: dict,
):
    """Test admin can partially update a kiosk."""
    update_data = {"is_active": False}

    response = await async_client.patch(
        f"/admin/kiosks/{test_kiosk.id}",
        json=update_data,
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_active"] is False
    # Other fields should remain unchanged
    assert data["kiosk_name"] == test_kiosk.kiosk_name
    assert data["location"] == test_kiosk.location


@pytest.mark.asyncio
async def test_admin_update_kiosk_not_found(
    async_client: AsyncClient,
    admin_headers: dict,
):
    """Test update with non-existent kiosk."""
    response = await async_client.patch(
        "/admin/kiosks/99999",
        json={"is_active": False},
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_admin_kiosks_requires_admin_role(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that kiosk admin endpoints require admin role."""
    # Test list
    response = await async_client.get("/admin/kiosks", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Test create
    response = await async_client.post(
        "/admin/kiosks",
        json={"kiosk_name": "Test", "location": "Test", "device_fingerprint": "test"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

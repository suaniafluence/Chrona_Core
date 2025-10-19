"""Tests for admin device management endpoints."""

import pytest
from fastapi import status
from httpx import AsyncClient

from src.models.device import Device
from src.models.user import User


@pytest.mark.asyncio
async def test_admin_list_all_devices(
    async_client: AsyncClient,
    test_admin: User,
    test_user: User,
    test_device: Device,
    admin_headers: dict,
):
    """Test admin can list all devices."""
    response = await async_client.get("/admin/devices", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(d["id"] == test_device.id for d in data)


@pytest.mark.asyncio
async def test_admin_list_devices_filter_by_user(
    async_client: AsyncClient,
    test_user: User,
    test_device: Device,
    admin_headers: dict,
):
    """Test admin can filter devices by user_id."""
    response = await async_client.get(
        f"/admin/devices?user_id={test_user.id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(d["user_id"] == test_user.id for d in data)


@pytest.mark.asyncio
async def test_admin_list_devices_filter_by_revoked(
    async_client: AsyncClient,
    test_device: Device,
    admin_headers: dict,
):
    """Test admin can filter devices by revocation status."""
    # Revoke the device first
    await async_client.post(
        f"/admin/devices/{test_device.id}/revoke",
        headers=admin_headers,
    )

    # Filter for revoked devices
    response = await async_client.get(
        "/admin/devices?is_revoked=true",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(d["is_revoked"] is True for d in data)


@pytest.mark.asyncio
async def test_admin_revoke_any_device(
    async_client: AsyncClient,
    test_device: Device,
    admin_headers: dict,
):
    """Test admin can revoke any device."""
    response = await async_client.post(
        f"/admin/devices/{test_device.id}/revoke",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_device.id
    assert data["is_revoked"] is True


@pytest.mark.asyncio
async def test_admin_revoke_device_not_found(
    async_client: AsyncClient,
    admin_headers: dict,
):
    """Test admin revoke with non-existent device."""
    response = await async_client.post(
        "/admin/devices/99999/revoke",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_admin_devices_requires_admin_role(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that device admin endpoints require admin role."""
    response = await async_client.get("/admin/devices", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

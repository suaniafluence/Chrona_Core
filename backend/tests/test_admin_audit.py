"""Tests for admin audit log endpoints."""

import pytest
from fastapi import status
from httpx import AsyncClient

from src.models.device import Device
from src.models.kiosk import Kiosk
from src.models.user import User


@pytest.mark.asyncio
async def test_admin_get_audit_logs(
    async_client: AsyncClient,
    test_user: User,
    test_device: Device,
    admin_headers: dict,
    auth_headers: dict,
):
    """Test admin can retrieve audit logs."""
    # Create some audit events by registering a device
    await async_client.post(
        "/devices/register",
        json={
            "device_fingerprint": "audit-test-fp",
            "device_name": "Audit Test Device",
        },
        headers=auth_headers,
    )

    # Get audit logs
    response = await async_client.get("/admin/audit-logs", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Should have at least the device_registered event
    assert len(data) > 0
    assert all("event_type" in log for log in data)
    assert all("created_at" in log for log in data)


@pytest.mark.asyncio
async def test_admin_filter_audit_logs_by_event_type(
    async_client: AsyncClient,
    test_device: Device,
    admin_headers: dict,
):
    """Test admin can filter audit logs by event type."""
    # Revoke device to create audit event
    await async_client.post(
        f"/admin/devices/{test_device.id}/revoke",
        headers=admin_headers,
    )

    # Filter for device_revoked events
    response = await async_client.get(
        "/admin/audit-logs?event_type=device_revoked",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(log["event_type"] == "device_revoked" for log in data)


@pytest.mark.asyncio
async def test_admin_filter_audit_logs_by_user_id(
    async_client: AsyncClient,
    test_user: User,
    test_device: Device,
    admin_headers: dict,
    auth_headers: dict,
):
    """Test admin can filter audit logs by user_id."""
    # Create audit event
    await async_client.post(
        "/devices/register",
        json={
            "device_fingerprint": "user-filter-fp",
            "device_name": "User Filter Device",
        },
        headers=auth_headers,
    )

    # Filter by user
    response = await async_client.get(
        f"/admin/audit-logs?user_id={test_user.id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(
        log["user_id"] == test_user.id or log["user_id"] is None for log in data
    )


@pytest.mark.asyncio
async def test_admin_filter_audit_logs_by_device_id(
    async_client: AsyncClient,
    test_device: Device,
    admin_headers: dict,
):
    """Test admin can filter audit logs by device_id."""
    # Revoke device to create audit event with device_id
    await async_client.post(
        f"/admin/devices/{test_device.id}/revoke",
        headers=admin_headers,
    )

    # Filter by device
    response = await async_client.get(
        f"/admin/audit-logs?device_id={test_device.id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(
        log["device_id"] == test_device.id or log["device_id"] is None
        for log in data
    )


@pytest.mark.asyncio
async def test_admin_audit_logs_pagination(
    async_client: AsyncClient,
    test_device: Device,
    admin_headers: dict,
    auth_headers: dict,
):
    """Test audit logs pagination."""
    # Create multiple audit events
    for i in range(5):
        await async_client.post(
            "/devices/register",
            json={
                "device_fingerprint": f"pagination-fp-{i}",
                "device_name": f"Pagination Device {i}",
            },
            headers=auth_headers,
        )

    # Get first page
    response1 = await async_client.get(
        "/admin/audit-logs?limit=3",
        headers=admin_headers,
    )
    assert response1.status_code == status.HTTP_200_OK
    page1 = response1.json()
    assert len(page1) <= 3

    # Get second page
    response2 = await async_client.get(
        "/admin/audit-logs?limit=3&offset=3",
        headers=admin_headers,
    )
    assert response2.status_code == status.HTTP_200_OK
    page2 = response2.json()

    # Pages should be different
    if len(page1) > 0 and len(page2) > 0:
        assert page1[0]["id"] != page2[0]["id"]


@pytest.mark.asyncio
async def test_admin_audit_logs_ordered_by_created_at(
    async_client: AsyncClient,
    admin_headers: dict,
):
    """Test that audit logs are ordered by created_at descending."""
    response = await async_client.get("/admin/audit-logs", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    if len(data) > 1:
        # Check descending order
        timestamps = [log["created_at"] for log in data]
        assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.asyncio
async def test_admin_audit_logs_requires_admin_role(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that audit log endpoint requires admin role."""
    response = await async_client.get("/admin/audit-logs", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_admin_audit_logs_combined_filters(
    async_client: AsyncClient,
    test_user: User,
    test_device: Device,
    admin_headers: dict,
):
    """Test combining multiple filters."""
    # Revoke device
    await async_client.post(
        f"/admin/devices/{test_device.id}/revoke",
        headers=admin_headers,
    )

    # Filter by event_type and device_id
    response = await async_client.get(
        f"/admin/audit-logs?event_type=device_revoked&device_id={test_device.id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    for log in data:
        assert log["event_type"] == "device_revoked"
        if log["device_id"] is not None:
            assert log["device_id"] == test_device.id

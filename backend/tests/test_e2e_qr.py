"""End-to-end test for QR punch flow (mobile -> kiosk)."""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_e2e_qr_flow(
    async_client: AsyncClient,
    test_user,
    test_device,
    test_kiosk,
    auth_headers: dict,
    admin_headers: dict,
    kiosk_headers: dict,
):
    """Validate the full QR flow: request -> validate -> replay blocked."""

    # 1) Mobile requests ephemeral QR token for its device
    req_payload = {"device_id": test_device.id}
    r = await async_client.post(
        "/punch/request-token", json=req_payload, headers=auth_headers
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert "qr_token" in data and data["qr_token"]
    assert data.get("expires_in", 0) > 0
    qr_token = data["qr_token"]

    # 2) Kiosk validates the QR token and records a punch
    val_payload = {
        "qr_token": qr_token,
        "kiosk_id": test_kiosk.id,
        "punch_type": "clock_in",
    }
    r2 = await async_client.post(
        "/punch/validate", json=val_payload, headers=kiosk_headers
    )
    assert r2.status_code == status.HTTP_200_OK
    v = r2.json()
    assert v.get("success") is True
    assert v.get("punch_id") is not None

    # 3) Replay attempt with same token must fail
    r3 = await async_client.post(
        "/punch/validate", json=val_payload, headers=kiosk_headers
    )
    assert r3.status_code == status.HTTP_400_BAD_REQUEST

    # 4) Admin can see audit log for punch_validated
    r4 = await async_client.get(
        f"/admin/audit-logs?event_type=punch_validated&user_id={test_user.id}",
        headers=admin_headers,
    )
    assert r4.status_code == status.HTTP_200_OK
    logs = r4.json()
    assert isinstance(logs, list)
    assert any(log.get("event_type") == "punch_validated" for log in logs)


@pytest.mark.asyncio
async def test_e2e_qr_flow_clock_out(
    async_client: AsyncClient,
    test_user,
    test_device,
    test_kiosk,
    auth_headers: dict,
    admin_headers: dict,
):
    """Validate QR flow for clock_out action."""

    # Request token
    r = await async_client.post(
        "/punch/request-token",
        json={"device_id": test_device.id},
        headers=auth_headers,
    )
    assert r.status_code == status.HTTP_200_OK
    qr = r.json()["qr_token"]

    # Validate as clock_out
    r2 = await async_client.post(
        "/punch/validate",
        json={
            "qr_token": qr,
            "kiosk_id": test_kiosk.id,
            "punch_type": "clock_out",
        },
    )
    assert r2.status_code == status.HTTP_200_OK
    data = r2.json()
    assert data.get("success") is True and data.get("punch_id")

    # Replay should fail
    r3 = await async_client.post(
        "/punch/validate",
        json={
            "qr_token": qr,
            "kiosk_id": test_kiosk.id,
            "punch_type": "clock_out",
        },
    )
    assert r3.status_code == status.HTTP_400_BAD_REQUEST

    # Audit log has punch_validated
    r4 = await async_client.get(
        f"/admin/audit-logs?event_type=punch_validated&user_id={test_user.id}",
        headers=admin_headers,
    )
    assert r4.status_code == status.HTTP_200_OK
    assert any(log.get("event_type") == "punch_validated" for log in r4.json())

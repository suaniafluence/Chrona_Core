"""End-to-end tests for kiosk creation + API key flow.

Covers the backoffice UX contract:
1) Admin creates a kiosk via POST /admin/kiosks
2) Admin immediately generates an API key via POST /admin/kiosks/{id}/generate-api-key
3) Listing kiosks never includes the plain api_key
"""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_kiosk_create_then_generate_key(
    async_client: AsyncClient, admin_headers: dict
):
    # 1) Create kiosk (no api_key in response)
    kiosk_payload = {
        "kiosk_name": "Backoffice-Flow-Kiosk",
        "location": "Reception",
        "device_fingerprint": "flow-kiosk-fp-001",
    }
    resp_create = await async_client.post(
        "/admin/kiosks", json=kiosk_payload, headers=admin_headers
    )
    assert resp_create.status_code == status.HTTP_201_CREATED
    created = resp_create.json()
    assert "api_key" not in created
    kiosk_id = created["id"]

    # 2) Generate API key (returned once)
    resp_key = await async_client.post(
        f"/admin/kiosks/{kiosk_id}/generate-api-key", headers=admin_headers
    )
    assert resp_key.status_code == status.HTTP_200_OK
    key_data = resp_key.json()
    assert key_data.get("kiosk_id") == kiosk_id
    assert isinstance(key_data.get("api_key"), str)
    assert len(key_data["api_key"]) > 16

    # 3) List kiosks - ensure no api_key is leaked
    resp_list = await async_client.get("/admin/kiosks", headers=admin_headers)
    assert resp_list.status_code == status.HTTP_200_OK
    items = resp_list.json()
    assert any(k["id"] == kiosk_id for k in items)
    assert all("api_key" not in k for k in items)


@pytest.mark.asyncio
async def test_generate_key_requires_admin(
    async_client: AsyncClient, admin_headers: dict, auth_headers: dict
):
    # Create kiosk as ADMIN (unique fingerprint to ensure 201)
    from uuid import uuid4

    fp = f"forbidden-flow-fp-{uuid4()}"
    create_resp = await async_client.post(
        "/admin/kiosks",
        json={
            "kiosk_name": "NonAdmin-Forbidden-Flow",
            "location": "Floor 2",
            "device_fingerprint": fp,
        },
        headers=admin_headers,
    )
    assert create_resp.status_code == status.HTTP_201_CREATED, create_resp.text
    kiosk_id = create_resp.json()["id"]

    # Attempt generate-key without admin role
    resp = await async_client.post(
        f"/admin/kiosks/{kiosk_id}/generate-api-key", headers=auth_headers
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

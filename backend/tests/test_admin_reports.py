"""Tests for /admin/reports/attendance export endpoint."""

import io
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.punch import Punch, PunchType
from src.models.device import Device
from src.models.kiosk import Kiosk
from src.models.user import User


async def _seed_punches(db: AsyncSession, user: User, device: Device, kiosk: Kiosk) -> list[Punch]:
  now = datetime.now(timezone.utc)
  punches = [
      Punch(
          user_id=user.id,
          device_id=device.id,
          kiosk_id=kiosk.id,
          punch_type=PunchType.CLOCK_IN,
          punched_at=now - timedelta(minutes=60),
          jwt_jti=f"test-jti-{uuid4()}",
      ),
      Punch(
          user_id=user.id,
          device_id=device.id,
          kiosk_id=kiosk.id,
          punch_type=PunchType.CLOCK_OUT,
          punched_at=now - timedelta(minutes=30),
          jwt_jti=f"test-jti-{uuid4()}",
      ),
  ]
  for p in punches:
      db.add(p)
  await db.commit()
  for p in punches:
      await db.refresh(p)
  return punches


@pytest.mark.asyncio
async def test_reports_json(async_client: AsyncClient, test_db: AsyncSession, test_admin: User, test_user: User, test_device: Device, test_kiosk: Kiosk, admin_headers: dict):
    await _seed_punches(test_db, test_user, test_device, test_kiosk)
    # Wide date range to include seeded punches
    today = datetime.now(timezone.utc).date()
    r = await async_client.get(
        f"/admin/reports/attendance?from={today.isoformat()}&to={today.isoformat()}&format=json",
        headers=admin_headers,
    )
    assert r.status_code == status.HTTP_200_OK, r.text
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    for item in data:
        # minimal fields expected
        assert "user_id" in item and "punch_type" in item


@pytest.mark.asyncio
async def test_reports_csv(async_client: AsyncClient, test_db: AsyncSession, test_admin: User, test_user: User, test_device: Device, test_kiosk: Kiosk, admin_headers: dict):
    await _seed_punches(test_db, test_user, test_device, test_kiosk)
    today = datetime.now(timezone.utc).date()
    r = await async_client.get(
        f"/admin/reports/attendance?from={today.isoformat()}&to={today.isoformat()}&format=csv",
        headers=admin_headers,
    )
    assert r.status_code == status.HTTP_200_OK, r.text
    assert r.headers.get("content-type", "").startswith("text/csv")
    cd = r.headers.get("content-disposition", "")
    assert "attachment" in cd and "attendance_" in cd
    content = r.content.decode("utf-8")
    lines = [ln for ln in content.splitlines() if ln.strip()]
    # header + at least two rows
    assert len(lines) >= 3
    assert lines[0].startswith("id,user_id,device_id,kiosk_id,punch_type,pu")


@pytest.mark.asyncio
async def test_reports_pdf(async_client: AsyncClient, test_db: AsyncSession, test_admin: User, test_user: User, test_device: Device, test_kiosk: Kiosk, admin_headers: dict):
    await _seed_punches(test_db, test_user, test_device, test_kiosk)
    today = datetime.now(timezone.utc).date()
    r = await async_client.get(
        f"/admin/reports/attendance?from={today.isoformat()}&to={today.isoformat()}&format=pdf",
        headers=admin_headers,
    )
    assert r.status_code == status.HTTP_200_OK, r.text
    assert r.headers.get("content-type", "").startswith("application/pdf")
    # Basic sanity: PDF files begin with %PDF
    assert r.content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_reports_validation_and_auth(async_client: AsyncClient, admin_headers: dict, auth_headers: dict):
    # invalid range (from > to)
    r_bad = await async_client.get(
        "/admin/reports/attendance?from=2030-01-02&to=2030-01-01&format=json",
        headers=admin_headers,
    )
    assert r_bad.status_code == status.HTTP_400_BAD_REQUEST
    assert r_bad.json().get("detail") in {"invalid_range", "invalid_datetime"}

    # non-admin forbidden
    r_forbidden = await async_client.get(
        "/admin/reports/attendance?from=2030-01-01&to=2030-01-02&format=json",
        headers=auth_headers,
    )
    assert r_forbidden.status_code == status.HTTP_403_FORBIDDEN


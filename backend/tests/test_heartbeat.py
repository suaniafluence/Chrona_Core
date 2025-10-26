"""Tests for kiosk heartbeat endpoints."""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.main import app
from src.models.kiosk import Kiosk

client = TestClient(app)


@pytest.fixture
def test_kiosk(test_session: Session) -> Kiosk:
    """Create a test kiosk with API key."""
    from src.core.security import hash_password

    kiosk = Kiosk(
        kiosk_name="Test-Heartbeat-Kiosk",
        location="Test Location",
        device_fingerprint="test-device-hb-123",
        api_key_hash=hash_password("test-heartbeat-key"),
        is_active=True,
    )
    test_session.add(kiosk)
    test_session.commit()
    test_session.refresh(kiosk)
    return kiosk


def test_send_heartbeat_success(test_session: Session, test_kiosk: Kiosk):
    """Test sending a heartbeat successfully."""
    # Send heartbeat
    response = client.post(
        "/kiosk/heartbeat",
        json={
            "app_version": "1.0.0",
            "device_info": "Android/11 - Samsung Galaxy Tab",
        },
        headers={"X-Kiosk-API-Key": "test-heartbeat-key"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["kiosk_id"] == test_kiosk.id
    assert "last_heartbeat_at" in data
    assert "server_time" in data

    # Verify database was updated
    test_session.expire(test_kiosk)
    updated_kiosk = test_session.get(Kiosk, test_kiosk.id)
    assert updated_kiosk.last_heartbeat_at is not None
    assert updated_kiosk.app_version == "1.0.0"
    assert updated_kiosk.device_info == "Android/11 - Samsung Galaxy Tab"


def test_send_heartbeat_without_auth(test_session: Session, test_kiosk: Kiosk):
    """Test that heartbeat requires authentication."""
    response = client.post(
        "/kiosk/heartbeat",
        json={
            "app_version": "1.0.0",
            "device_info": "Android/11 - Test Device",
        },
    )

    assert response.status_code == 401  # Unauthorized


def test_send_heartbeat_invalid_api_key(test_session: Session, test_kiosk: Kiosk):
    """Test heartbeat with invalid API key."""
    response = client.post(
        "/kiosk/heartbeat",
        json={
            "app_version": "1.0.0",
            "device_info": "Android/11 - Test Device",
        },
        headers={"X-Kiosk-API-Key": "invalid-key"},
    )

    assert response.status_code == 401  # Unauthorized


def test_get_kiosk_status_online(test_session: Session, test_kiosk: Kiosk):
    """Test getting status of an online kiosk."""
    # Update last_heartbeat_at to now (kiosk is online)
    test_kiosk.last_heartbeat_at = datetime.utcnow()
    test_kiosk.app_version = "1.0.0"
    test_kiosk.device_info = "Android/11 - Test"
    test_session.add(test_kiosk)
    test_session.commit()

    response = client.get(
        "/kiosk/status",
        headers={"X-Kiosk-API-Key": "test-heartbeat-key"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["kiosk_id"] == test_kiosk.id
    assert data["kiosk_name"] == "Test-Heartbeat-Kiosk"
    assert data["is_active"] is True
    assert data["is_online"] is True
    assert data["offline_duration_seconds"] is None
    assert data["app_version"] == "1.0.0"
    assert data["device_info"] == "Android/11 - Test"


def test_get_kiosk_status_offline(test_session: Session, test_kiosk: Kiosk):
    """Test getting status of an offline kiosk."""
    # Update last_heartbeat_at to 10 minutes ago (kiosk is offline)
    test_kiosk.last_heartbeat_at = datetime.utcnow() - timedelta(minutes=10)
    test_kiosk.app_version = "1.0.0"
    test_session.add(test_kiosk)
    test_session.commit()

    response = client.get(
        "/kiosk/status",
        headers={"X-Kiosk-API-Key": "test-heartbeat-key"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_online"] is False
    assert data["offline_duration_seconds"] is not None
    assert data["offline_duration_seconds"] >= 600  # At least 10 minutes


def test_get_kiosk_status_never_connected(test_session: Session, test_kiosk: Kiosk):
    """Test getting status of a kiosk that never sent a heartbeat."""
    # Ensure last_heartbeat_at is None
    test_kiosk.last_heartbeat_at = None
    test_session.add(test_kiosk)
    test_session.commit()

    response = client.get(
        "/kiosk/status",
        headers={"X-Kiosk-API-Key": "test-heartbeat-key"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_online"] is False
    assert data["last_heartbeat_at"] is None
    assert data["offline_duration_seconds"] is None


def test_get_all_kiosks_status(test_session: Session, test_kiosk: Kiosk):
    """Test getting status of all kiosks."""
    # Create another kiosk
    from src.core.security import hash_password

    kiosk2 = Kiosk(
        kiosk_name="Test-Kiosk-2",
        location="Test Location 2",
        device_fingerprint="test-device-hb-456",
        api_key_hash=hash_password("test-key-2"),
        is_active=True,
        last_heartbeat_at=datetime.utcnow(),
        app_version="1.1.0",
    )
    test_session.add(kiosk2)
    test_session.commit()

    # Get all status (TODO: Should require admin auth)
    response = client.get("/kiosk/all-status")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # Find our test kiosks
    test_kiosk_data = next((k for k in data if k["kiosk_id"] == test_kiosk.id), None)
    test_kiosk2_data = next((k for k in data if k["kiosk_id"] == kiosk2.id), None)

    assert test_kiosk_data is not None
    assert test_kiosk2_data is not None
    assert test_kiosk2_data["is_online"] is True


def test_heartbeat_updates_timestamp_each_time(
    test_session: Session, test_kiosk: Kiosk
):
    """Test that each heartbeat updates the timestamp."""
    # First heartbeat
    response1 = client.post(
        "/kiosk/heartbeat",
        json={
            "app_version": "1.0.0",
            "device_info": "Test Device",
        },
        headers={"X-Kiosk-API-Key": "test-heartbeat-key"},
    )
    assert response1.status_code == 200
    timestamp1 = response1.json()["last_heartbeat_at"]

    # Wait a bit
    import time

    time.sleep(1)

    # Second heartbeat
    response2 = client.post(
        "/kiosk/heartbeat",
        json={
            "app_version": "1.0.0",
            "device_info": "Test Device",
        },
        headers={"X-Kiosk-API-Key": "test-heartbeat-key"},
    )
    assert response2.status_code == 200
    timestamp2 = response2.json()["last_heartbeat_at"]

    # Timestamps should be different
    assert timestamp1 != timestamp2

"""
Test script to verify all main API endpoints are working.
Requires backend server to be running on http://localhost:8000
"""

from datetime import datetime

import requests

BASE_URL = "http://localhost:8000"

# Test user credentials
TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "testpass123"

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_success(msg):
    print(f"{GREEN}[OK]{RESET} {msg}")


def print_error(msg):
    print(f"{RED}[ERROR]{RESET} {msg}")


def print_info(msg):
    print(f"{BLUE}[INFO]{RESET} {msg}")


def test_health():
    """Test health check endpoint."""
    print_info("Testing GET /health")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed: {data}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check exception: {e}")
        return False


def test_login():
    """Test user login and return access token."""
    print_info("Testing POST /auth/token")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={"username": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            print_success(f"Login successful, token: {access_token[:20]}...")
            return access_token
        else:
            print_error(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_error(f"Login exception: {e}")
        return None


def test_devices_list(token):
    """Test listing user devices."""
    print_info("Testing GET /devices/me")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/devices/me", headers=headers)
        if response.status_code == 200:
            devices = response.json()
            print_success(f"Devices list: {len(devices)} device(s) found")
            if devices:
                print(
                    f"    First device: {devices[0].get('device_name')} (ID: {devices[0].get('id')})"
                )
            return devices
        else:
            print_error(f"Devices list failed: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Devices list exception: {e}")
        return None


def test_request_qr_token(token, device_id):
    """Test requesting ephemeral QR token."""
    print_info("Testing POST /punch/request-token")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"device_id": device_id}
        response = requests.post(
            f"{BASE_URL}/punch/request-token", json=payload, headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            qr_token = data.get("qr_token")
            expires_in = data.get("expires_in")
            print_success(f"QR token generated (expires in {expires_in}s)")
            print(f"    Token (first 50 chars): {qr_token[:50]}...")
            return qr_token
        else:
            print_error(
                f"QR token request failed: {response.status_code} - {response.text}"
            )
            return None
    except Exception as e:
        print_error(f"QR token request exception: {e}")
        return None


def test_validate_punch(qr_token, kiosk_id=1):
    """Test validating QR token and creating punch."""
    print_info("Testing POST /punch/validate")
    try:
        payload = {
            "qr_token": qr_token,
            "kiosk_id": kiosk_id,
            "punch_type": "clock_in",
        }
        response = requests.post(f"{BASE_URL}/punch/validate", json=payload)
        if response.status_code == 200:
            data = response.json()
            print_success("Punch validated successfully")
            print(f"    Punch ID: {data.get('punch_id')}")
            print(f"    User ID: {data.get('user_id')}")
            print(f"    Type: {data.get('punch_type')}")
            print(f"    Timestamp: {data.get('punched_at')}")
            return True
        else:
            print_error(
                f"Punch validation failed: {response.status_code} - {response.text}"
            )
            return False
    except Exception as e:
        print_error(f"Punch validation exception: {e}")
        return False


def test_punch_history(token):
    """Test retrieving punch history."""
    print_info("Testing GET /punch/history")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/punch/history", headers=headers)
        if response.status_code == 200:
            punches = response.json()
            print_success(f"Punch history: {len(punches)} punch(es) found")
            if punches:
                latest = punches[0]
                print(
                    f"    Latest: {latest.get('punch_type')} at {latest.get('punched_at')}"
                )
            return punches
        else:
            print_error(f"Punch history failed: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Punch history exception: {e}")
        return None


def test_admin_kiosks(token):
    """Test admin endpoint for listing kiosks."""
    print_info("Testing GET /admin/kiosks")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/admin/kiosks", headers=headers)
        if response.status_code == 200:
            kiosks = response.json()
            print_success(f"Admin kiosks list: {len(kiosks)} kiosk(s) found")
            if kiosks:
                print(
                    f"    First kiosk: {kiosks[0].get('kiosk_name')} (ID: {kiosks[0].get('id')})"
                )
            return kiosks
        else:
            print_error(
                f"Admin kiosks failed: {response.status_code} - {response.text}"
            )
            return None
    except Exception as e:
        print_error(f"Admin kiosks exception: {e}")
        return None


def main():
    """Run all API endpoint tests."""
    print("=" * 70)
    print("API ENDPOINT TESTS")
    print("=" * 70)
    print()

    # Test 1: Health check
    if not test_health():
        print_error("Server not responding, aborting tests")
        return
    print()

    # Test 2: Login
    token = test_login()
    if not token:
        print_error("Login failed, aborting tests")
        return
    print()

    # Test 3: List devices
    devices = test_devices_list(token)
    if not devices or len(devices) == 0:
        print_error("No devices found, some tests will be skipped")
        device_id = None
    else:
        device_id = devices[0]["id"]
    print()

    # Test 4: Request QR token
    if device_id:
        qr_token = test_request_qr_token(token, device_id)
        print()

        # Test 5: Validate punch
        if qr_token:
            test_validate_punch(qr_token)
            print()

    # Test 6: Punch history
    test_punch_history(token)
    print()

    # Test 7: Admin endpoints (optional - requires admin role)
    test_admin_kiosks(token)
    print()

    print("=" * 70)
    print("TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()


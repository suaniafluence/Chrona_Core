#!/usr/bin/env python3
"""
Smoke tests for Chrona deployment
Python version for cross-platform compatibility
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Optional

import requests

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
TIMEOUT = 5
VERBOSE = os.getenv("VERBOSE", "0") == "1"


class Colors:
    """ANSI color codes"""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color


class SmokeTestRunner:
    """Smoke test runner for Chrona API"""

    def __init__(self, api_url: str, timeout: int = 5):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.failed_tests = 0
        self.passed_tests = 0

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{text}")
        print("-" * len(text))

    def check_endpoint(
        self, endpoint: str, expected_status: int, description: str
    ) -> bool:
        """Check if endpoint returns expected status code"""
        print(f"Testing {description}... ", end="", flush=True)

        try:
            response = requests.get(
                f"{self.api_url}{endpoint}", timeout=self.timeout
            )
            status = response.status_code

            if status == expected_status:
                print(f"{Colors.GREEN}✓{Colors.NC} (HTTP {status})")
                self.passed_tests += 1
                return True
            else:
                print(
                    f"{Colors.RED}✗{Colors.NC} (Expected {expected_status}, got {status})"
                )
                self.failed_tests += 1
                return False
        except requests.exceptions.RequestException as e:
            print(f"{Colors.RED}✗{Colors.NC} (Error: {str(e)})")
            self.failed_tests += 1
            return False

    def check_json_key(
        self, endpoint: str, expected_key: str, description: str
    ) -> bool:
        """Check if JSON response contains expected key"""
        print(f"Testing {description}... ", end="", flush=True)

        try:
            response = requests.get(
                f"{self.api_url}{endpoint}", timeout=self.timeout
            )
            data = response.json()

            if expected_key in data:
                print(f"{Colors.GREEN}✓{Colors.NC}")
                self.passed_tests += 1
                return True
            else:
                print(
                    f"{Colors.RED}✗{Colors.NC} (Key '{expected_key}' not found)"
                )
                self.failed_tests += 1
                return False
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.NC} (Error: {str(e)})")
            self.failed_tests += 1
            return False

    def test_registration_login_flow(self) -> bool:
        """Test full registration and login flow"""
        self.print_header("🔄 Full Auth Flow")

        test_email = f"smoke-test-{int(time.time())}@test.com"
        test_password = "SmokeTest123!"

        # Register
        print("Registering test user... ", end="", flush=True)
        try:
            register_response = requests.post(
                f"{self.api_url}/auth/register",
                json={"email": test_email, "password": test_password},
                timeout=self.timeout,
            )

            if register_response.status_code == 201:
                print(f"{Colors.GREEN}✓{Colors.NC}")
                self.passed_tests += 1
            else:
                print(
                    f"{Colors.RED}✗{Colors.NC} (HTTP {register_response.status_code})"
                )
                self.failed_tests += 1
                return False
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.NC} (Error: {str(e)})")
            self.failed_tests += 1
            return False

        # Login
        print("Logging in... ", end="", flush=True)
        try:
            login_response = requests.post(
                f"{self.api_url}/auth/token",
                data={"username": test_email, "password": test_password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=self.timeout,
            )

            if login_response.status_code == 200:
                token = login_response.json().get("access_token")
                print(f"{Colors.GREEN}✓{Colors.NC}")
                self.passed_tests += 1
            else:
                print(
                    f"{Colors.RED}✗{Colors.NC} (HTTP {login_response.status_code})"
                )
                self.failed_tests += 1
                return False
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.NC} (Error: {str(e)})")
            self.failed_tests += 1
            return False

        # Access protected endpoint
        print("Accessing protected endpoint with token... ", end="", flush=True)
        try:
            me_response = requests.get(
                f"{self.api_url}/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=self.timeout,
            )

            if (
                me_response.status_code == 200
                and test_email in me_response.text
            ):
                print(f"{Colors.GREEN}✓{Colors.NC}")
                self.passed_tests += 1
                return True
            else:
                print(
                    f"{Colors.RED}✗{Colors.NC} (HTTP {me_response.status_code})"
                )
                self.failed_tests += 1
                return False
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.NC} (Error: {str(e)})")
            self.failed_tests += 1
            return False

    def run_all_tests(self):
        """Run all smoke tests"""
        print(f"🔍 Running Chrona Smoke Tests")
        print(f"Target: {self.api_url}")
        print("=" * 40)

        # Health checks
        self.print_header("🏥 Health Checks")
        self.check_endpoint("/", 200, "Root endpoint")
        self.check_endpoint("/docs", 200, "OpenAPI docs")
        self.check_endpoint("/openapi.json", 200, "OpenAPI spec")

        # Authentication endpoints
        self.print_header("🔐 Authentication")
        self.check_endpoint(
            "/auth/register", 422, "Register endpoint (without payload)"
        )
        self.check_endpoint(
            "/auth/token", 422, "Token endpoint (without payload)"
        )
        self.check_endpoint(
            "/auth/me", 403, "Protected endpoint (without auth)"
        )

        # Protected endpoints
        self.print_header("🛡️  Protected Endpoints")
        self.check_endpoint("/devices/me", 403, "Devices endpoint (no auth)")
        self.check_endpoint(
            "/punch/history", 403, "Punch history (no auth)"
        )

        # Admin endpoints
        self.print_header("👑 Admin Endpoints")
        self.check_endpoint(
            "/admin/users", 403, "Admin users endpoint (no auth)"
        )
        self.check_endpoint(
            "/admin/devices", 403, "Admin devices endpoint (no auth)"
        )

        # Full flow test
        self.test_registration_login_flow()

        # Summary
        total_tests = self.passed_tests + self.failed_tests
        print("\n" + "=" * 40)
        if self.failed_tests == 0:
            print(
                f"{Colors.GREEN}✅ All {total_tests} smoke tests passed!{Colors.NC}"
            )
            return 0
        else:
            print(
                f"{Colors.RED}❌ {self.failed_tests}/{total_tests} test(s) failed{Colors.NC}"
            )
            return 1


def main():
    """Main entry point"""
    runner = SmokeTestRunner(API_URL, TIMEOUT)
    exit_code = runner.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

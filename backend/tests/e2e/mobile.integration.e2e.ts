/**
 * E2E Integration Tests: Mobile App → Backend
 * Tests complete flow from mobile app through backend API
 *
 * Prerequisites:
 * - Backend running on API_URL
 * - Mobile app accessible for manual testing
 * - Test data: HR codes, test users
 */

import { test, expect } from '@playwright/test';

const API_BASE = process.env.API_URL || 'http://localhost:8000';

test.describe('Mobile App Integration E2E', () => {
  test.describe.configure({ mode: 'serial' });

  let accessToken: string;
  let deviceId: number;
  let qrToken: string;
  let punchId: number;

  const testUser = {
    email: `mobile-e2e-${Date.now()}@test.com`,
    password: 'MobileTest123!',
  };

  const testDevice = {
    fingerprint: `mobile-e2e-${Date.now()}`,
    name: 'E2E Test Phone',
    attestation: {
      manufacturer: 'TestManufacturer',
      model: 'TestPhone',
      os: 'iOS',
      os_version: '17.0',
      build_id: 'e2e-build',
      is_emulator: true,
      has_screen_lock: true,
      timestamp: new Date().toISOString(),
    },
  };

  test.describe('1. User Registration (Onboarding Level B)', () => {
    test('should register user via onboarding', async ({ request }) => {
      // Step 1: Register user (if not using HR code flow)
      const registerResponse = await request.post(
        `${API_BASE}/auth/register`,
        {
          data: {
            email: testUser.email,
            password: testUser.password,
          },
        }
      );

      expect(registerResponse.status()).toBe(201);

      const body = await registerResponse.json();
      expect(body).toHaveProperty('id');
      expect(body).toHaveProperty('email', testUser.email);
    });

    test('should handle HR code verification', async ({ request }) => {
      // In real onboarding, mobile sends HR code
      // Backend generates OTP and sends to email

      // Test: POST /onboarding/initiate
      const initiateResponse = await request.post(
        `${API_BASE}/onboarding/initiate`,
        {
          data: {
            hr_code: 'HR12345', // Test HR code
            email: testUser.email,
          },
        }
      );

      // Should return session token
      expect([200, 201]).toContain(initiateResponse.status());

      const body = await initiateResponse.json();
      expect(body).toHaveProperty('session_token');
      expect(body).toHaveProperty('success', true);
    });

    test('should verify OTP code', async ({ request }) => {
      // Simulate OTP verification
      // Backend sends OTP to email, mobile user enters it

      const sessionToken = 'test-session-token-from-initiate'; // Would come from previous response

      const verifyResponse = await request.post(
        `${API_BASE}/onboarding/verify-otp`,
        {
          data: {
            session_token: sessionToken,
            otp_code: '123456', // Test OTP
          },
        }
      );

      expect([200, 201]).toContain(verifyResponse.status());

      const body = await verifyResponse.json();
      expect(body).toHaveProperty('success', true);
    });

    test('should complete onboarding with device attestation', async ({
      request,
    }) => {
      const sessionToken = 'test-session-token'; // From OTP step

      const completeResponse = await request.post(
        `${API_BASE}/onboarding/complete`,
        {
          data: {
            session_token: sessionToken,
            password: testUser.password,
            device_fingerprint: testDevice.fingerprint,
            device_name: testDevice.name,
            attestation_data: JSON.stringify(testDevice.attestation),
          },
        }
      );

      expect([200, 201]).toContain(completeResponse.status());

      const body = await completeResponse.json();
      expect(body).toHaveProperty('success', true);
      expect(body).toHaveProperty('access_token');

      accessToken = body.access_token;
    });
  });

  test.describe('2. Device Registration', () => {
    test('should register second device for same user', async ({ request }) => {
      const registerResponse = await request.post(
        `${API_BASE}/devices/register`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          data: {
            device_fingerprint: `mobile-e2e-device-2-${Date.now()}`,
            device_name: 'E2E Test Device 2',
            attestation_data: JSON.stringify({
              ...testDevice.attestation,
              manufacturer: 'TestManufacturer2',
            }),
          },
        }
      );

      expect(registerResponse.status()).toBe(201);

      const body = await registerResponse.json();
      expect(body).toHaveProperty('id');
      deviceId = body.id;
    });

    test('should list registered devices', async ({ request }) => {
      const listResponse = await request.get(`${API_BASE}/devices/me`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      expect(listResponse.status()).toBe(200);

      const body = await listResponse.json();
      expect(Array.isArray(body)).toBe(true);
      expect(body.length).toBeGreaterThanOrEqual(1);

      // Find our test device
      const testDeviceRecord = body.find(
        (d: any) => d.device_name === 'E2E Test Device 2'
      );
      expect(testDeviceRecord).toBeDefined();
    });
  });

  test.describe('3. QR Token Generation', () => {
    test('should request QR token for punch', async ({ request }) => {
      const tokenResponse = await request.post(
        `${API_BASE}/punch/request-token`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          data: {
            device_id: deviceId,
          },
        }
      );

      expect(tokenResponse.status()).toBe(200);

      const body = await tokenResponse.json();
      expect(body).toHaveProperty('qr_token');
      expect(body).toHaveProperty('expires_in');
      expect(body.expires_in).toBeLessThanOrEqual(30); // Token expires in ≤30s

      // Verify JWT format
      const parts = body.qr_token.split('.');
      expect(parts.length).toBe(3); // header.payload.signature

      qrToken = body.qr_token;
    });

    test('should decode JWT payload correctly', async ({ request }) => {
      // Decode JWT without verifying (client-side decode)
      const parts = qrToken.split('.');
      const payload = JSON.parse(
        Buffer.from(parts[1], 'base64').toString('utf-8')
      );

      expect(payload).toHaveProperty('sub'); // user_id
      expect(payload).toHaveProperty('device_id', deviceId);
      expect(payload).toHaveProperty('nonce'); // Unique nonce for replay protection
      expect(payload).toHaveProperty('jti'); // JWT ID for single-use enforcement
      expect(payload).toHaveProperty('exp'); // Expiration time
      expect(payload).toHaveProperty('iat'); // Issued at
    });

    test('should reject request without authenticated user', async ({
      request,
    }) => {
      const tokenResponse = await request.post(
        `${API_BASE}/punch/request-token`,
        {
          // No Authorization header
          data: {
            device_id: deviceId,
          },
        }
      );

      expect(tokenResponse.status()).toBe(401);
    });

    test('should reject request with invalid device_id', async ({ request }) => {
      const tokenResponse = await request.post(
        `${API_BASE}/punch/request-token`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          data: {
            device_id: 99999, // Non-existent device
          },
        }
      );

      expect(tokenResponse.status()).toBe(404);
    });
  });

  test.describe('4. Punch Validation (Kiosk Scanning)', () => {
    test('should validate QR token from kiosk', async ({ request }) => {
      // Kiosk scans QR code and sends token to backend
      const validateResponse = await request.post(
        `${API_BASE}/punch/validate`,
        {
          headers: {
            'X-Kiosk-API-Key': process.env.TEST_KIOSK_API_KEY || 'test-key',
          },
          data: {
            qr_token: qrToken,
            kiosk_id: 1,
            punch_type: 'clock_in',
          },
        }
      );

      expect(validateResponse.status()).toBe(200);

      const body = await validateResponse.json();
      expect(body).toHaveProperty('success', true);
      expect(body).toHaveProperty('punch_id');
      expect(body).toHaveProperty('punched_at');
      expect(body).toHaveProperty('user_id');

      punchId = body.punch_id;
    });

    test('should prevent token replay attack', async ({ request }) => {
      // Try to use same token again (should be rejected)
      const replayResponse = await request.post(
        `${API_BASE}/punch/validate`,
        {
          headers: {
            'X-Kiosk-API-Key': process.env.TEST_KIOSK_API_KEY || 'test-key',
          },
          data: {
            qr_token: qrToken,
            kiosk_id: 1,
            punch_type: 'clock_out',
          },
        }
      );

      expect(replayResponse.status()).toBe(400);

      const body = await replayResponse.json();
      expect(String(body.detail)).toMatch(/already.*used|replay|consumed/i);
    });

    test('should reject expired token', async ({ request }) => {
      // Wait for token to expire (>30 seconds)
      // This test would take 30+ seconds
      // Skip in CI unless specifically enabled

      if (!process.env.TEST_SLOW) {
        test.skip();
      }

      // Wait 31 seconds for token to expire
      await new Promise((resolve) => setTimeout(resolve, 31000));

      // Try to validate expired token
      const expiredResponse = await request.post(
        `${API_BASE}/punch/validate`,
        {
          headers: {
            'X-Kiosk-API-Key': process.env.TEST_KIOSK_API_KEY || 'test-key',
          },
          data: {
            qr_token: qrToken,
            kiosk_id: 1,
            punch_type: 'clock_out',
          },
        }
      );

      expect(expiredResponse.status()).toBe(401);

      const body = await expiredResponse.json();
      expect(String(body.detail)).toMatch(/expired|invalid/i);
    });

    test('should require valid kiosk API key', async ({ request }) => {
      // Generate fresh token for this test
      const tokenResponse = await request.post(
        `${API_BASE}/punch/request-token`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          data: {
            device_id: deviceId,
          },
        }
      );

      const freshToken = (await tokenResponse.json()).qr_token;

      // Try to validate with invalid API key
      const invalidKeyResponse = await request.post(
        `${API_BASE}/punch/validate`,
        {
          headers: {
            'X-Kiosk-API-Key': 'invalid-kiosk-key',
          },
          data: {
            qr_token: freshToken,
            kiosk_id: 1,
            punch_type: 'clock_in',
          },
        }
      );

      expect(invalidKeyResponse.status()).toBe(401);
    });

    test('should reject validation without kiosk API key', async ({
      request,
    }) => {
      const tokenResponse = await request.post(
        `${API_BASE}/punch/request-token`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          data: {
            device_id: deviceId,
          },
        }
      );

      const freshToken = (await tokenResponse.json()).qr_token;

      // No X-Kiosk-API-Key header
      const noKeyResponse = await request.post(
        `${API_BASE}/punch/validate`,
        {
          data: {
            qr_token: freshToken,
            kiosk_id: 1,
            punch_type: 'clock_in',
          },
        }
      );

      expect(noKeyResponse.status()).toBe(401);
    });
  });

  test.describe('5. Punch History', () => {
    test('should list punch history for authenticated user', async ({
      request,
    }) => {
      const historyResponse = await request.get(`${API_BASE}/punch/history`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      expect(historyResponse.status()).toBe(200);

      const body = await historyResponse.json();
      expect(Array.isArray(body)).toBe(true);
      expect(body.length).toBeGreaterThanOrEqual(1);

      // Verify punch record
      const punch = body.find((p: any) => p.id === punchId);
      expect(punch).toBeDefined();
      expect(punch.punch_type).toBe('clock_in');
      expect(punch.device_id).toBe(deviceId);
    });

    test('should reject history request without authentication', async ({
      request,
    }) => {
      const historyResponse = await request.get(`${API_BASE}/punch/history`);

      expect(historyResponse.status()).toBe(401);
    });

    test('should paginate history results', async ({ request }) => {
      // Test pagination query params
      const historyResponse = await request.get(
        `${API_BASE}/punch/history?limit=5&offset=0`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      expect(historyResponse.status()).toBe(200);

      const body = await historyResponse.json();
      expect(Array.isArray(body)).toBe(true);
      expect(body.length).toBeLessThanOrEqual(5);
    });

    test('should filter history by date range', async ({ request }) => {
      const today = new Date().toISOString().split('T')[0];

      const historyResponse = await request.get(
        `${API_BASE}/punch/history?from=${today}&to=${today}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      expect(historyResponse.status()).toBe(200);

      const body = await historyResponse.json();
      expect(Array.isArray(body)).toBe(true);
    });
  });

  test.describe('6. Device Management', () => {
    test('should revoke device', async ({ request }) => {
      const revokeResponse = await request.post(
        `${API_BASE}/devices/${deviceId}/revoke`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      expect(revokeResponse.status()).toBe(200);
    });

    test('should prevent QR generation on revoked device', async ({
      request,
    }) => {
      // Try to request token for revoked device
      const tokenResponse = await request.post(
        `${API_BASE}/punch/request-token`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          data: {
            device_id: deviceId,
          },
        }
      );

      expect(tokenResponse.status()).toBe(400);

      const body = await tokenResponse.json();
      expect(String(body.detail)).toMatch(/revoked|disabled/i);
    });
  });

  test.describe('7. Security & Audit Logs', () => {
    test('should create audit log entries for key events', async ({
      request,
    }) => {
      // After punch validation, there should be audit logs
      // (User can only see their own, or admin can query)

      // For this test, we'd need admin access to check audit logs
      // Skip for now - tested in admin integration tests
    });

    test('should enforce rate limiting on token requests', async ({
      request,
    }) => {
      // Register new device first
      const registerResponse = await request.post(
        `${API_BASE}/devices/register`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          data: {
            device_fingerprint: `mobile-e2e-ratelimit-${Date.now()}`,
            device_name: 'RateLimit Test Device',
          },
        }
      );

      const newDeviceId = (await registerResponse.json()).id;

      // Make rapid requests (should hit rate limit)
      const requests = [];
      for (let i = 0; i < 10; i++) {
        const tokenResponse = request.post(
          `${API_BASE}/punch/request-token`,
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
            data: {
              device_id: newDeviceId,
            },
          }
        );
        requests.push(tokenResponse);
      }

      const responses = await Promise.all(requests);

      // Some requests should be rate limited
      const rateLimitedCount = responses.filter(
        (r) => r.status() === 429
      ).length;

      expect(rateLimitedCount).toBeGreaterThan(0);
    });
  });
});

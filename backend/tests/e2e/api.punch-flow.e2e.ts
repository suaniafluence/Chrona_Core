import { test, expect } from '@playwright/test';

/**
 * E2E test for complete punch flow:
 * 1. Register user
 * 2. Login
 * 3. Register device
 * 4. Request QR token
 * 5. Validate token (punch in)
 * 6. Check punch history
 */

const API_BASE = process.env.API_URL || 'http://localhost:8000';
const KIOSK_ID = Number(process.env.KIOSK_ID || '1');

test.describe('Complete Punch Flow E2E', () => {
  test.describe.configure({ mode: 'serial' });

  let accessToken: string;
  let kioskApiKey: string;
  let deviceId: number;
  let qrToken: string;

  const testUser = {
    email: `punch-e2e-${Date.now()}@test.com`,
    password: 'TestPassword123!',
  };

  test.beforeAll(async () => {
    // In a real scenario, kiosk API key would be pre-provisioned
    // For E2E, we'll use a mock or admin-created key
    kioskApiKey = process.env.TEST_KIOSK_API_KEY || '';
    if (!kioskApiKey) {
      console.warn('TEST_KIOSK_API_KEY missing; using fallback invalid key');
      kioskApiKey = 'invalid-test-kiosk-key';
    } else {
      console.log(`Using kiosk API key (len=${kioskApiKey.length})`);
    }
  });

  test('Step 1: Register user', async ({ request }) => {
    const response = await request.post(`${API_BASE}/auth/register`, {
      data: {
        email: testUser.email,
        password: testUser.password,
      },
    });

    expect(response.status()).toBe(201);
  });

  test('Step 2: Login user', async ({ request }) => {
    const response = await request.post(`${API_BASE}/auth/token`, {
      form: {
        username: testUser.email,
        password: testUser.password,
      },
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    accessToken = body.access_token;
  });

  test('Step 3: Register device', async ({ request }) => {
    const response = await request.post(`${API_BASE}/devices/register`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      data: {
        device_fingerprint: `e2e-device-${Date.now()}`,
        device_name: 'E2E Test Device',
        attestation_data: JSON.stringify({
          manufacturer: 'Playwright',
          model: 'E2E Runner',
          os: 'test',
        }),
      },
    });

    expect(response.status()).toBe(201);

    const body = await response.json();
    expect(body).toHaveProperty('id');
    deviceId = body.id;
  });

  test('Step 4: Request QR token', async ({ request }) => {
    const response = await request.post(`${API_BASE}/punch/request-token`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      data: {
        device_id: deviceId,
      },
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body).toHaveProperty('qr_token');
    expect(body).toHaveProperty('expires_in');
    expect(body).toHaveProperty('expires_at');

    qrToken = body.qr_token;

    // Verify token is JWT format
    const parts = qrToken.split('.');
    expect(parts.length).toBe(3); // header.payload.signature
  });

  test('Step 5: Validate QR token (punch in)', async ({ request }) => {
    const response = await request.post(`${API_BASE}/punch/validate`, {
      headers: {
        'X-Kiosk-API-Key': kioskApiKey,
      },
      data: {
        qr_token: qrToken,
        kiosk_id: KIOSK_ID,
        punch_type: 'clock_in',
      },
    });

    const status = response.status();
    const text = await response.text();
    expect(status, `Punch validate failed: ${status} ${text}`).toBe(200);

    const body = JSON.parse(text);
    expect(body).toHaveProperty('success', true);
    expect(body).toHaveProperty('punch_id');
    expect(body).toHaveProperty('punched_at');
    // Backend response includes user_id/device_id but not user_email
    expect(body).toHaveProperty('user_id');
  });

  test('Step 6: Verify token cannot be reused (replay protection)', async ({
    request,
  }) => {
    const response = await request.post(`${API_BASE}/punch/validate`, {
      headers: {
        'X-Kiosk-API-Key': kioskApiKey,
      },
      data: {
        qr_token: qrToken,
        kiosk_id: KIOSK_ID,
        punch_type: 'clock_out',
      },
    });

    // Should fail - token already consumed
    expect(response.status()).toBe(400);

    const body = await response.json();
    expect(body.detail).toContain('already been used');
  });

  test('Step 7: Check punch history', async ({ request }) => {
    const response = await request.get(`${API_BASE}/punch/history`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBeGreaterThanOrEqual(1);

    const lastPunch = body[0];
    expect(lastPunch).toHaveProperty('punch_type', 'clock_in');
    expect(lastPunch).toHaveProperty('device_id', deviceId);
  });

  test('Step 8: Request new token and punch out', async ({ request }) => {
    // Request new token
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
    const tokenBody = await tokenResponse.json();
    const newQrToken = tokenBody.qr_token;

    // Validate for clock out
    const punchResponse = await request.post(`${API_BASE}/punch/validate`, {
      headers: {
        'X-Kiosk-API-Key': kioskApiKey,
      },
      data: {
        qr_token: newQrToken,
        kiosk_id: KIOSK_ID,
        punch_type: 'clock_out',
      },
    });

    expect(punchResponse.status()).toBe(200);
  });

  test('Step 9: Verify both punches in history', async ({ request }) => {
    const response = await request.get(`${API_BASE}/punch/history`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body.length).toBeGreaterThanOrEqual(2);

    // Check we have both clock_in and clock_out
    const punchTypes = body.map((p: any) => p.punch_type);
    expect(punchTypes).toContain('clock_in');
    expect(punchTypes).toContain('clock_out');
  });
});

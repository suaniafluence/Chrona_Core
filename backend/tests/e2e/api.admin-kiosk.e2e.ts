import { test, expect } from '@playwright/test';

/**
 * E2E tests for admin kiosk management
 * Tests: POST /admin/kiosks, GET /admin/kiosks, PATCH /admin/kiosks/{id}
 */

const API_BASE = process.env.API_URL || 'http://localhost:8000';

test.describe('Admin Kiosk Management E2E', () => {
  test.describe.configure({ mode: 'serial' });

  let adminAccessToken: string;
  let kioskId: number;

  // Use the pre-created admin user from CI (see .github/workflows/ci.yml)
  const adminUser = {
    email: 'admin-e2e@local',
    password: 'Passw0rd!',
  };

  const kioskData = {
    kiosk_name: `E2E Kiosk ${Date.now()}`,
    location: 'E2E Test Location',
    device_fingerprint: `e2e-kiosk-fp-${Date.now()}`,
    public_key:
      '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA\n-----END PUBLIC KEY-----',
  };

  test.beforeAll(async ({ request }) => {
    // Login with pre-created admin user from CI
    const loginResponse = await request.post(`${API_BASE}/auth/token`, {
      form: {
        username: adminUser.email,
        password: adminUser.password,
      },
    });
    expect(loginResponse.status()).toBe(200);

    const body = await loginResponse.json();
    adminAccessToken = body.access_token;
  });

  test('should create a new kiosk successfully', async ({ request }) => {
    const response = await request.post(`${API_BASE}/admin/kiosks`, {
      headers: {
        Authorization: `Bearer ${adminAccessToken}`,
      },
      data: kioskData,
    });

    expect(response.status()).toBe(201);

    const body = await response.json();
    expect(body).toHaveProperty('id');
    expect(body).toHaveProperty('kiosk_name', kioskData.kiosk_name);
    expect(body).toHaveProperty('location', kioskData.location);
    expect(body).toHaveProperty('device_fingerprint', kioskData.device_fingerprint);
    expect(body).toHaveProperty('is_active', true);
    expect(body).toHaveProperty('created_at');
    // Verify created_at is a valid ISO 8601 datetime string
    expect(new Date(body.created_at).toISOString()).toBeTruthy();

    kioskId = body.id;
  });

  test('should reject duplicate kiosk name', async ({ request }) => {
    const duplicateData = {
      ...kioskData,
      device_fingerprint: `e2e-kiosk-fp-dup-${Date.now()}`, // Different fingerprint
    };

    const response = await request.post(`${API_BASE}/admin/kiosks`, {
      headers: {
        Authorization: `Bearer ${adminAccessToken}`,
      },
      data: duplicateData,
    });

    expect(response.status()).toBe(409);
    const body = await response.json();
    expect(String(body.detail).toLowerCase()).toContain('already exists');
  });

  test('should reject duplicate fingerprint', async ({ request }) => {
    const duplicateData = {
      ...kioskData,
      kiosk_name: `E2E Kiosk Dup ${Date.now()}`, // Different name
    };

    const response = await request.post(`${API_BASE}/admin/kiosks`, {
      headers: {
        Authorization: `Bearer ${adminAccessToken}`,
      },
      data: duplicateData,
    });

    expect(response.status()).toBe(409);
    const body = await response.json();
    expect(String(body.detail).toLowerCase()).toContain('already exists');
  });

  test('should list all kiosks', async ({ request }) => {
    const response = await request.get(`${API_BASE}/admin/kiosks`, {
      headers: {
        Authorization: `Bearer ${adminAccessToken}`,
      },
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBeGreaterThanOrEqual(1);

    // Find our created kiosk
    const createdKiosk = body.find((k: any) => k.id === kioskId);
    expect(createdKiosk).toBeDefined();
    expect(createdKiosk.kiosk_name).toBe(kioskData.kiosk_name);
  });

  test('should filter kiosks by active status', async ({ request }) => {
    const response = await request.get(
      `${API_BASE}/admin/kiosks?is_active=true`,
      {
        headers: {
          Authorization: `Bearer ${adminAccessToken}`,
        },
      },
    );

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
    // All returned kiosks should be active
    expect(body.every((k: any) => k.is_active === true)).toBe(true);
  });

  test('should update a kiosk successfully', async ({ request }) => {
    const updateData = {
      location: 'Updated E2E Location',
      is_active: false,
    };

    const response = await request.patch(
      `${API_BASE}/admin/kiosks/${kioskId}`,
      {
        headers: {
          Authorization: `Bearer ${adminAccessToken}`,
        },
        data: updateData,
      },
    );

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body).toHaveProperty('id', kioskId);
    expect(body).toHaveProperty('location', updateData.location);
    expect(body).toHaveProperty('is_active', updateData.is_active);
    // Other fields should remain unchanged
    expect(body).toHaveProperty('kiosk_name', kioskData.kiosk_name);
  });

  test('should return 404 for non-existent kiosk update', async ({
    request,
  }) => {
    const response = await request.patch(
      `${API_BASE}/admin/kiosks/999999`,
      {
        headers: {
          Authorization: `Bearer ${adminAccessToken}`,
        },
        data: { location: 'Test' },
      },
    );

    expect(response.status()).toBe(404);
  });

  test('should require admin role for kiosk creation', async ({
    request,
  }) => {
    // Create a regular user (not admin)
    const regularUser = {
      email: `regular-user-${Date.now()}@test.com`,
      password: 'UserPassword123!',
    };

    // Register regular user
    await request.post(`${API_BASE}/auth/register`, {
      data: regularUser,
    });

    // Login as regular user
    const loginResponse = await request.post(`${API_BASE}/auth/token`, {
      form: {
        username: regularUser.email,
        password: regularUser.password,
      },
    });
    const userToken = (await loginResponse.json()).access_token;

    // Try to create kiosk as regular user
    const createResponse = await request.post(`${API_BASE}/admin/kiosks`, {
      headers: {
        Authorization: `Bearer ${userToken}`,
      },
      data: {
        kiosk_name: 'Forbidden Kiosk',
        location: 'Test',
        device_fingerprint: 'test-fp',
      },
    });

    expect(createResponse.status()).toBe(403);
  });

  test('should require authentication for kiosk operations', async ({
    request,
  }) => {
    const response = await request.get(`${API_BASE}/admin/kiosks`);

    expect(response.status()).toBe(403);
  });
});

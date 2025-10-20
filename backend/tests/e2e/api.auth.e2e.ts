import { test, expect } from '@playwright/test';

/**
 * E2E tests for authentication endpoints
 * Tests: /auth/register, /auth/token, /auth/me
 */

const API_BASE = process.env.API_URL || 'http://localhost:8000';

test.describe('Authentication API E2E', () => {
  test.describe.configure({ mode: 'serial' });

  let accessToken: string;
  const testUser = {
    email: `e2e-${Date.now()}@test.com`,
    password: 'TestPassword123!',
  };

  test('should register a new user', async ({ request }) => {
    const response = await request.post(`${API_BASE}/auth/register`, {
      data: {
        email: testUser.email,
        password: testUser.password,
      },
    });

    expect(response.status()).toBe(201);

    const body = await response.json();
    expect(body).toHaveProperty('id');
    expect(body).toHaveProperty('email', testUser.email);
    expect(body).toHaveProperty('role', 'user');
    expect(body).not.toHaveProperty('hashed_password');
  });

  test('should not register duplicate email', async ({ request }) => {
    const response = await request.post(`${API_BASE}/auth/register`, {
      data: {
        email: testUser.email,
        password: testUser.password,
      },
    });

    expect(response.status()).toBe(400);

    const body = await response.json();
    expect(body.detail).toContain('already registered');
  });

  test('should login with valid credentials', async ({ request }) => {
    const response = await request.post(`${API_BASE}/auth/token`, {
      form: {
        username: testUser.email,
        password: testUser.password,
      },
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body).toHaveProperty('access_token');
    expect(body).toHaveProperty('token_type', 'bearer');

    accessToken = body.access_token;
  });

  test('should reject login with invalid password', async ({ request }) => {
    const response = await request.post(`${API_BASE}/auth/token`, {
      form: {
        username: testUser.email,
        password: 'WrongPassword',
      },
    });

    expect(response.status()).toBe(401);
  });

  test('should get current user with valid token', async ({ request }) => {
    const response = await request.get(`${API_BASE}/auth/me`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body).toHaveProperty('email', testUser.email);
    expect(body).toHaveProperty('role', 'user');
  });

  test('should reject /auth/me without token', async ({ request }) => {
    const response = await request.get(`${API_BASE}/auth/me`);

    expect(response.status()).toBe(403);
  });

  test('should reject /auth/me with invalid token', async ({ request }) => {
    const response = await request.get(`${API_BASE}/auth/me`, {
      headers: {
        Authorization: 'Bearer invalid-token-12345',
      },
    });

    expect(response.status()).toBe(401);
  });
});

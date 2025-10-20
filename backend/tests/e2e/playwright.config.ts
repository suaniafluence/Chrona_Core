import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for Chrona E2E tests
 * Tests backend API + kiosk web app
 */
export default defineConfig({
  testDir: './',
  testMatch: '**/*.e2e.ts',

  /* Maximum time one test can run for */
  timeout: 30 * 1000,

  /* Run tests in files in parallel */
  fullyParallel: true,

  /* Fail the build on CI if you accidentally left test.only in the source code */
  forbidOnly: !!process.env.CI,

  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,

  /* Opt out of parallel tests on CI */
  workers: process.env.CI ? 1 : undefined,

  /* Reporter to use */
  reporter: [
    ['html'],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['json', { outputFile: 'test-results/results.json' }],
  ],

  /* Shared settings for all the projects below */
  use: {
    /* Base URL for API tests */
    baseURL: process.env.API_URL || 'http://localhost:8000',

    /* Collect trace when retrying the failed test */
    trace: 'on-first-retry',

    /* Screenshot on failure */
    screenshot: 'only-on-failure',

    /* Video on failure */
    video: 'retain-on-failure',
  },

  /* Configure projects for major browsers (for kiosk UI tests) */
  projects: [
    {
      name: 'api-tests',
      testMatch: '**/api.*.e2e.ts',
      use: {
        ...devices['Desktop Chrome'],
      },
    },

    {
      name: 'kiosk-chrome',
      testMatch: '**/kiosk.*.e2e.ts',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
      },
    },

    {
      name: 'kiosk-firefox',
      testMatch: '**/kiosk.*.e2e.ts',
      use: {
        ...devices['Desktop Firefox'],
        viewport: { width: 1280, height: 720 },
      },
    },

    {
      name: 'kiosk-tablet',
      testMatch: '**/kiosk.*.e2e.ts',
      use: {
        ...devices['iPad Pro'],
      },
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: process.env.CI
    ? undefined
    : {
        command: 'cd ../../backend && uvicorn src.main:app --reload --port 8000',
        url: 'http://localhost:8000/docs',
        reuseExistingServer: !process.env.CI,
        timeout: 120 * 1000,
      },
});

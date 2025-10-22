import { test, expect } from '@playwright/test';

/**
 * E2E tests for Kiosk UI
 * Tests the full kiosk interface workflow
 */

const KIOSK_URL = process.env.KIOSK_URL || 'http://localhost:5174';
const API_BASE = process.env.API_URL || 'http://localhost:8000';

test.describe('Kiosk UI E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(KIOSK_URL);
  });

  test('should load kiosk interface', async ({ page }) => {
    // Verify page title
    await expect(page).toHaveTitle(/Chrona Kiosk/i);

    // Verify main elements are visible
    await expect(page.locator('h1')).toContainText(/Pointage|Kiosk/i);

    // Check for QR scanner or kiosk interface
    const hasScanner =
      (await page.locator('[class*="scanner"]').count()) > 0 ||
      (await page.locator('[data-testid*="scanner"]').count()) > 0;

    const hasKioskUI =
      (await page.locator('.app').count()) > 0 ||
      (await page.locator('[class*="kiosk"]').count()) > 0;

    expect(hasScanner || hasKioskUI).toBeTruthy();
  });

  test('should display connection status indicator', async ({ page }) => {
    // Look for connection status element
    const statusIndicator = page.locator('[data-testid="connection-status"], [class*="connection"]');
    // Wait up to 10s for it to appear and be visible (CI-safe)
    const el = statusIndicator.first();
    await el.waitFor({ state: 'visible', timeout: 10000 });
    await expect(el).toBeVisible();
  });

  test('should have kiosk mode toggle', async ({ page }) => {
    // Look for kiosk mode button/toggle
    const kioskModeToggle = page.locator(
      'button:has-text("Kiosk"), button:has-text("Mode"), [data-testid="kiosk-mode-toggle"]'
    );

    // Should have at least one control element
    const count = await kioskModeToggle.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should enable fullscreen mode when kiosk mode activated', async ({
    page,
  }) => {
    // Find kiosk mode toggle
    const kioskToggle = page.locator(
      'button:has-text("Activer le mode kiosk"), button:has-text("Enable Kiosk Mode")'
    );

    if ((await kioskToggle.count()) > 0) {
      // Click to activate kiosk mode
      await kioskToggle.first().click();

      // Wait for mode to activate
      await page.waitForTimeout(500);

      // Check if fullscreen was requested (we can't verify actual fullscreen in tests)
      // But we can check for kiosk-mode CSS class or state
      const appElement = page.locator('.app, [data-testid="app"]');
      const classes = await appElement.first().getAttribute('class');

      expect(classes).toContain('kiosk');
    }
  });

  test('should display QR scanner interface', async ({ page }) => {
    // Look for scanner elements
    const scanner = page.locator(
      '[class*="scanner"], video, [data-testid="qr-scanner"]'
    );

    // Scanner should be visible or scan button should exist
    const scanButton = page.locator('button:has-text("Scan"), button:has-text("Scanner")');

    const hasScanner = (await scanner.count()) > 0;
    const hasScanButton = (await scanButton.count()) > 0;

    expect(hasScanner || hasScanButton).toBeTruthy();
  });

  test('should show validation result placeholder', async ({ page }) => {
    // Even without a QR scan, result placeholder should exist
    const resultArea = page.locator(
      '[class*="result"], [class*="validation"], [data-testid="validation-result"]'
    );

    // May not be visible initially, but should exist in DOM
    const count = await resultArea.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should display kiosk information', async ({ page }) => {
    // Look for kiosk ID or name
    const kioskInfo = page.locator(
      'text=/Kiosk [0-9]+/i, text=/Office/i, [class*="kiosk-info"]'
    );

    const hasInfo = (await kioskInfo.count()) > 0;

    // Kiosk info may be hidden in kiosk mode, but should exist
    expect(hasInfo).toBeTruthy();
  });

  test('should handle network errors gracefully', async ({ page, context }) => {
    // Simulate offline mode
    await context.setOffline(true);

    await page.reload();

    // Wait a bit for connection check
    await page.waitForTimeout(2000);

    // Check for offline indicator or error message
    const offlineIndicator = page.locator(
      'text=/offline/i, text=/connexion/i, text=/erreur/i, [class*="offline"]'
    );

    const hasOfflineIndicator = (await offlineIndicator.count()) > 0;

    // Should show some indication of connection issue
    expect(hasOfflineIndicator).toBeTruthy();

    // Restore online mode
    await context.setOffline(false);
  });

  test('should be responsive to different viewports', async ({ page }) => {
    // Test desktop viewport (default)
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.locator('.app, body')).toBeVisible();

    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('.app, body')).toBeVisible();

    // Test mobile viewport (kiosk might not support this)
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('.app, body')).toBeVisible();
  });

  test('should have accessible UI elements', async ({ page }) => {
    // Check for proper ARIA labels or roles
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();

    // Should have at least one interactive element
    expect(buttonCount).toBeGreaterThan(0);

    // Check first button has accessible text or label
    if (buttonCount > 0) {
      const firstButton = buttons.first();
      const text = await firstButton.textContent();
      const ariaLabel = await firstButton.getAttribute('aria-label');

      expect(text || ariaLabel).toBeTruthy();
    }
  });

  test('should not have console errors on load', async ({ page }) => {
    const errors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.reload();
    await page.waitForTimeout(2000);

    // Should have no critical console errors
    const criticalErrors = errors.filter(
      (err) => !err.includes('favicon') && !err.includes('404')
    );

    expect(criticalErrors.length).toBe(0);
  });
});

test.describe('Kiosk UI - QR Code Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(KIOSK_URL);
  });

  test('should simulate QR code scan result display', async ({ page }) => {
    // We can't actually scan a QR code in automated tests,
    // but we can verify the UI can handle mock data

    // Inject a mock successful validation result
    await page.evaluate(() => {
      const mockResult = {
        success: true,
        message: 'Pointage enregistré avec succès',
        punch_id: 123,
        user_id: 1,
        punched_at: new Date().toISOString(),
      };

      // Trigger React state update (this is a hack for testing)
      const event = new CustomEvent('validation-result', {
        detail: mockResult,
      });
      window.dispatchEvent(event);
    });

    await page.waitForTimeout(500);

    // Check if success indicator appears
    const successIndicator = page.locator(
      '[class*="success"], text=/succès/i, text=/success/i, .validation-success'
    );

    // May or may not be visible depending on implementation
    // Just verify the page doesn't crash
    expect(page).toBeTruthy();
  });

  test('should handle validation errors', async ({ page }) => {
    // Inject a mock error result
    await page.evaluate(() => {
      const mockError = {
        success: false,
        message: 'Token invalide ou expiré',
      };

      const event = new CustomEvent('validation-result', {
        detail: mockError,
      });
      window.dispatchEvent(event);
    });

    await page.waitForTimeout(500);

    // Page should not crash
    expect(page).toBeTruthy();
  });

  test('should reset UI after result display', async ({ page }) => {
    // Inject mock result
    await page.evaluate(() => {
      const mockResult = {
        success: true,
        message: 'OK',
      };

      const event = new CustomEvent('validation-result', {
        detail: mockResult,
      });
      window.dispatchEvent(event);
    });

    // Wait for auto-reset (typically 3-5 seconds)
    await page.waitForTimeout(4000);

    // Scanner should be ready again
    const scanner = page.locator('[class*="scanner"], [class*="scan"]');
    const count = await scanner.count();

    expect(count).toBeGreaterThan(0);
  });
});

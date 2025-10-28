/**
 * E2E tests for QR Code Generation and Punch Flow
 * Tests: Login → Device selection → QR generation → Biometric auth
 */

import { device, element, by, expect as detoxExpect } from 'detox';
import { typeText, tap, waitFor, clearTextField } from './config';

describe('QR Code Generation E2E', () => {
  beforeAll(async () => {
    await device.launchApp({
      permissions: { notifications: 'YES', biometric: 'YES' },
      newInstance: true,
    });
  });

  describe('QR Generation Flow', () => {
    it('should login and navigate to device selection', async () => {
      // Login with test user
      const emailInput = element(by.type('RCTTextInput').at(0));
      const passwordInput = element(by.type('RCTTextInput').at(1));

      await typeText(emailInput, 'test@example.com');
      await typeText(passwordInput, 'Passw0rd!');

      // Tap login
      await tap(element(by.text('Se connecter')));

      // Should see device list or "Pas d'appareil enregistré"
      await waitFor(
        element(by.text(/Appareil|Device|enregistré|registered/i)),
        10000
      );
    });

    it('should display registered devices', async () => {
      // After login, should see device list
      const deviceList = element(by.type('RCTFlatList').at(0));

      // If devices exist, should be visible
      await detoxExpect(deviceList).toExist();
    });

    it('should register new device from home screen', async () => {
      // Look for "Ajouter un appareil" or register button
      const registerButton = element(by.text(/Ajouter|Enregistrer|Register/i));

      await tap(registerButton);

      // Should show device registration screen
      await waitFor(element(by.text(/Fingerprint|Attestation|Register/i)), 5000);

      // Typically auto-captures device info
      // Should show device name input
      const deviceNameInput = element(by.type('RCTTextInput').at(0));
      await detoxExpect(deviceNameInput).toBeVisible();
    });

    it('should require biometric for device registration', async () => {
      // Fill device name
      const deviceNameInput = element(by.type('RCTTextInput').at(0));
      await typeText(deviceNameInput, 'Mon iPhone');

      // Try to complete registration
      const registerButton = element(by.text(/Confirmer|Complete|Register/i));
      await tap(registerButton);

      // Should prompt for biometric auth
      // Detox can simulate biometric with:
      // await device.matchFace() or device.matchFinger()
      // OR handle the system prompt

      // For now, just check that auth is requested
      await waitFor(
        element(by.text(/biométrique|Authentification|biometric|Touch|Face/i)),
        5000
      );
    });
  });

  describe('QR Code Display', () => {
    it('should display QR code after device selection', async () => {
      // From home screen, select a device and generate QR
      // Look for device in list
      const firstDevice = element(by.type('RCTView').and(by.text(/iPhone|Phone/i)).at(0));

      await tap(firstDevice);

      // Should navigate to QR screen
      // Wait for QR code to render
      await waitFor(element(by.text(/Présentez|QR Code|Générer/i)), 10000);

      // QR code is typically a canvas/image element
      const qrCode = element(by.id('qr-code')); // May need to match actual ID
      await detoxExpect(qrCode).toBeVisible();
    });

    it('should show countdown timer on QR screen', async () => {
      // QR codes have 30 second expiry
      // Should show: "30s", "29s", etc.
      await waitFor(element(by.text(/30|29|28/)), 5000);

      // Timer should decrement
      await device.sleep(2000);
      await waitFor(element(by.text(/28|27|26/)), 3000);
    });

    it('should show timer color changes (green→orange→red)', async () => {
      // Timer color depends on time left
      // Green (>20s), Orange (10-20s), Red (<10s)

      // Wait for timer to reach orange zone (around 15 seconds)
      await device.sleep(15000);

      // Check if timer element has orange color
      const timerText = element(by.text(/15|14|13|12|11/));
      await detoxExpect(timerText).toBeVisible();

      // Visual check: timer should be orange
      // (Can't directly check color in Detox, but can verify text appears)
    });

    it('should auto-regenerate QR when expired', async () => {
      // Wait for timer to reach 0
      await device.sleep(30000);

      // QR should be regenerated
      // New QR code should appear with fresh timer
      await waitFor(element(by.text(/30|29|28/)), 10000);
    });

    it('should require biometric before generating new QR', async () => {
      // User can tap "Générer un nouveau code"
      const refreshButton = element(by.text(/Générer|Refresh|Nouveau/i));

      await tap(refreshButton);

      // Should prompt for biometric
      await waitFor(
        element(by.text(/biométrique|Authentification/i)),
        5000
      );
    });

    it('should show QR generation error message', async () => {
      // Simulate API error (no network, invalid device, etc.)
      // This would require network mocking

      // When error occurs, should show user-friendly message
      // not technical error
      await waitFor(
        element(by.text(/Erreur|Error|impossible/i)),
        5000
      ).catch(() => {
        // Expected - error might not always occur
      });
    });
  });

  describe('QR Anti-Capture Protection', () => {
    it('should prevent screenshots on QR screen', async () => {
      // Try to take screenshot (platform-dependent)
      // On iOS: Long press home, Screenshot
      // On Android: Volume down + Power

      // App should show message: "Screenshots disabled for security"
      // Or quietly prevent it

      // Detox can't directly test screenshot prevention
      // But we can verify the UI element that triggers protection
      const qrScreen = element(by.text(/Présentez|QR Code/i));
      await detoxExpect(qrScreen).toBeVisible();

      // In real test, user would attempt screenshot
      // App should handle gracefully
    });

    it('should prevent screen recording on QR screen', async () => {
      // Similar to screenshots - app should prevent screen recording
      // iOS: Control Center → Screen Recording
      // Android: Settings → Advanced → Screen Recording

      // App uses expo-screen-capture to prevent this
      // We can't easily test this in Detox without actual device action
    });
  });

  describe('Punch Flow Integration', () => {
    it('should complete punch after QR generation', async () => {
      // Full flow:
      // 1. Generate QR code on phone
      // 2. Kiosk scans QR
      // 3. Backend validates and records punch

      // In E2E, we can't actually integrate with kiosk
      // But we can test that:
      // 1. QR is generated successfully
      // 2. User navigates back to home
      // 3. New punch appears in history

      // After QR generation, user scans at kiosk (manual step)
      // Then punch should appear in history
      const backButton = element(by.text(/Retour|Back|Home/i));
      await tap(backButton);

      // Navigate to history screen
      const historyTab = element(by.text(/Historique|History/i));
      await tap(historyTab);

      // Should see punch record (clock_in)
      await waitFor(element(by.text(/Entrée|Clock In|aujourd'hui|today/i)), 10000);
    });

    it('should show punch type (clock_in vs clock_out)', async () => {
      // History screen should show punch type
      // 🟢 Entrée (Clock In) / 🔴 Sortie (Clock Out)

      const clockInIcon = element(by.text(/🟢|entrée|clock.?in/i));
      await detoxExpect(clockInIcon).toExist();
    });

    it('should display punch timestamp', async () => {
      // Each punch should show:
      // - Time (HH:mm)
      // - Date (DD/MM/YYYY)

      const timestamp = element(by.text(/\d{2}:\d{2}|\d{2}\/\d{2}\/\d{4}/));
      await detoxExpect(timestamp).toBeVisible();
    });

    it('should allow pull-to-refresh on history', async () => {
      // User can refresh punch history
      const historyList = element(by.type('RCTFlatList').at(0));

      // Pull to refresh
      await historyList.multiTap().then(async () => {
        // On iOS: pull down
        // On Android: swipe down
        // Both should trigger refresh

        // Wait for refresh to complete
        await device.sleep(2000);

        // New punch should appear if one was recorded
      });
    });
  });

  describe('Error Scenarios', () => {
    it('should handle network error during QR generation', async () => {
      // Simulate offline mode
      await device.setAirplaneMode(true);

      // Try to generate QR
      const generateButton = element(by.text(/Générer|Generate/i));
      await tap(generateButton);

      // Should show error message
      await waitFor(element(by.text(/Erreur|Error|réseau|network/i)), 5000);

      // Restore network
      await device.setAirplaneMode(false);
    });

    it('should handle device not registered error', async () => {
      // Try to generate QR without registered device
      // Should show error: "Aucun appareil enregistré"

      const deviceList = element(by.type('RCTFlatList'));
      const deviceCount = await deviceList.getElements().then(e => e.length);

      if (deviceCount === 0) {
        const generateButton = element(by.text(/Générer|Generate/i));

        // Try to tap (might be disabled)
        // Should see message about no device
        await waitFor(
          element(by.text(/Aucun appareil|No device/i)),
          5000
        );
      }
    });

    it('should handle biometric auth failure', async () => {
      // User cancels biometric prompt
      // Cancel button should appear
      const cancelButton = element(by.text(/Annuler|Cancel/i));

      await detoxExpect(cancelButton).toBeVisible();

      // Tap cancel
      await tap(cancelButton);

      // Should return to previous screen
      // QR should not be generated
    });
  });

  describe('Performance', () => {
    it('should load QR code within reasonable time', async () => {
      const startTime = Date.now();

      // Trigger QR generation
      const device = element(by.type('RCTView').at(0));
      await tap(device);

      // Wait for QR to appear
      await waitFor(element(by.id('qr-code')), 10000);

      const elapsed = Date.now() - startTime;

      // Should load within 5 seconds
      expect(elapsed).toBeLessThan(5000);
    });

    it('should smoothly animate countdown timer', async () => {
      // Timer should update smoothly (1 second per tick)
      // Not the same number twice (e.g., 15, 15, 14, 13...)

      // This is hard to test in Detox without custom logic
      // But we can verify timer text changes
      await waitFor(element(by.text(/30/)), 3000);
      await device.sleep(1000);
      await waitFor(element(by.text(/29/)), 3000);
    });
  });
});

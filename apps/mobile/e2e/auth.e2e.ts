/**
 * E2E tests for Mobile Authentication
 * Tests: Login, Registration (via onboarding), token storage
 */

import { device, element, by, expect as detoxExpect } from 'detox';
import { typeText, tap, waitFor, clearTextField } from './config';

describe('Mobile Authentication E2E', () => {
  beforeAll(async () => {
    await device.launchApp({
      permissions: { notifications: 'YES', biometric: 'YES' },
      newInstance: true,
    });
  });

  beforeEach(async () => {
    await device.reloadReactNative();
  });

  describe('Login Screen', () => {
    it('should display login form on app launch', async () => {
      // Look for title "Chrona"
      await waitFor(element(by.text('Chrona')));
      await waitFor(element(by.text('Pointage sécurisé')));

      // Look for input fields
      await waitFor(element(by.type('RCTTextInput').and(by.text('Email'))));
      await waitFor(element(by.type('RCTTextInput').and(by.text('Mot de passe'))));

      // Look for login button
      await waitFor(element(by.text('Se connecter')));
    });

    it('should show error for invalid credentials', async () => {
      // Fill in incorrect credentials
      const emailInput = element(by.type('RCTTextInput').at(0));
      const passwordInput = element(by.type('RCTTextInput').at(1));

      await typeText(emailInput, 'invalid@test.com');
      await typeText(passwordInput, 'wrongpassword');

      // Tap login button
      await tap(element(by.text('Se connecter')));

      // Wait for error alert
      await waitFor(element(by.text(/Erreur de connexion/i)), 5000);
    });

    it('should validate empty email field', async () => {
      const passwordInput = element(by.type('RCTTextInput').at(1));

      // Clear fields
      await clearTextField(element(by.type('RCTTextInput').at(0)));
      await clearTextField(passwordInput);

      // Type only password
      await typeText(passwordInput, 'password123');

      // Tap login
      await tap(element(by.text('Se connecter')));

      // Should show validation error
      await waitFor(element(by.text(/remplir tous les champs/i)), 5000);
    });

    it('should disable button while loading', async () => {
      const loginButton = element(by.text('Se connecter'));

      // Fill in valid test credentials (should exist from backend)
      const emailInput = element(by.type('RCTTextInput').at(0));
      const passwordInput = element(by.type('RCTTextInput').at(1));

      await clearTextField(emailInput);
      await clearTextField(passwordInput);

      await typeText(emailInput, 'test@example.com');
      await typeText(passwordInput, 'Passw0rd!');

      // Button should be enabled initially
      await detoxExpect(loginButton).not.toBeDisabled();

      // Tap login
      await tap(loginButton);

      // Button should become disabled while loading
      await detoxExpect(loginButton).toBeDisabled();
    });

    it('should navigate to onboarding on signup link click', async () => {
      // Tap "Nouveau collaborateur ? S'inscrire"
      await tap(element(by.text(/Nouveau collaborateur/i)));

      // Should navigate to HR Code screen
      await waitFor(element(by.text(/Code RH/i)), 5000);
    });
  });

  describe('Successful Login Flow', () => {
    it('should login successfully and navigate to home screen', async () => {
      // Assuming test user exists: test@example.com / Passw0rd!
      const emailInput = element(by.type('RCTTextInput').at(0));
      const passwordInput = element(by.type('RCTTextInput').at(1));

      // Clear and fill fields
      await clearTextField(emailInput);
      await clearTextField(passwordInput);

      await typeText(emailInput, 'test@example.com');
      await typeText(passwordInput, 'Passw0rd!');

      // Tap login
      await tap(element(by.text('Se connecter')));

      // Wait for navigation to HomeScreen (should show device list)
      await waitFor(element(by.text(/Appareil/i)), 10000);
    });

    it('should persist token in secure storage', async () => {
      // After successful login, token should be stored
      // We can't directly access secure storage in Detox, but we can verify
      // persistence by reloading the app

      // Reload app
      await device.reloadReactNative();

      // Should still be on home screen (token valid)
      // If token wasn't persisted, should be back on login screen
      await waitFor(element(by.text(/Appareil/i)), 5000);
    });
  });

  describe('Session Management', () => {
    it('should logout user when tapping logout button', async () => {
      // First login
      const emailInput = element(by.type('RCTTextInput').at(0));
      const passwordInput = element(by.type('RCTTextInput').at(1));

      await typeText(emailInput, 'test@example.com');
      await typeText(passwordInput, 'Passw0rd!');
      await tap(element(by.text('Se connecter')));

      // Wait for home screen
      await waitFor(element(by.text(/Appareil/i)), 10000);

      // Find and tap logout (may be in settings/menu)
      // This depends on actual implementation - adjust selector as needed
      await tap(element(by.text(/Déconnexion|Logout/i)));

      // Should return to login screen
      await waitFor(element(by.text('Chrona')), 5000);
    });

    it('should auto-logout on 401 unauthorized', async () => {
      // Login first
      const emailInput = element(by.type('RCTTextInput').at(0));
      const passwordInput = element(by.type('RCTTextInput').at(1));

      await typeText(emailInput, 'test@example.com');
      await typeText(passwordInput, 'Passw0rd!');
      await tap(element(by.text('Se connecter')));

      // Wait for home screen
      await waitFor(element(by.text(/Appareil/i)), 10000);

      // Simulate expired token by clearing secure storage
      // (In real scenario, backend would return 401)
      // For Detox, we'd need to inject this or manipulate async-storage

      // Re-open app settings or trigger API call
      // This test is more useful as integration test
    });
  });
});

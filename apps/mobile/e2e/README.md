# Mobile E2E Tests

End-to-end tests for Chrona mobile app using Detox and Jest.

## 📁 Files

- **config.ts** - Detox configuration and helper functions
- **auth.e2e.ts** - Authentication and login tests (8 tests)
- **onboarding.e2e.ts** - Level B onboarding flow (14 tests)
- **qr-punch.e2e.ts** - QR generation and punch flow (18 tests)

## 🚀 Quick Start

```bash
# Install dependencies (from apps/mobile)
npm install

# Build test framework
npm run build:e2e

# Run tests on iOS simulator
npm run e2e:ios

# Or Android emulator
npm run e2e:android

# Debug mode
npm run e2e:debug
```

## 🎯 Test Coverage

### Authentication (auth.e2e.ts)
- ✅ Login form display
- ✅ Invalid credentials error
- ✅ Empty field validation
- ✅ Loading state during login
- ✅ Navigation to signup
- ✅ Successful login & navigation to home
- ✅ Token persistence
- ✅ Auto-logout on 401

**Run:**
```bash
detox test auth.e2e.ts --configuration ios
```

### Onboarding Level B (onboarding.e2e.ts)
- ✅ HR code screen display
- ✅ HR code validation
- ✅ OTP screen after HR code
- ✅ OTP format validation
- ✅ OTP resend functionality
- ✅ Device attestation form
- ✅ Device fingerprint display
- ✅ Biometric auth requirement
- ✅ Password strength indicator
- ✅ Back navigation
- ✅ Error handling
- ✅ Network error handling
- ✅ Session clearing on cancel

**Run:**
```bash
detox test onboarding.e2e.ts --configuration ios
```

### QR Generation & Punch (qr-punch.e2e.ts)
- ✅ Device selection & listing
- ✅ Device registration flow
- ✅ QR code display
- ✅ 30-second countdown timer
- ✅ Timer color changes (green→orange→red)
- ✅ Auto-regeneration on expiry
- ✅ Biometric auth for QR generation
- ✅ Anti-screenshot protection
- ✅ Error handling (network, invalid device)
- ✅ Punch history integration
- ✅ Pull-to-refresh on history
- ✅ Punch timestamp display
- ✅ Performance checks

**Run:**
```bash
detox test qr-punch.e2e.ts --configuration ios
```

## 🔧 Prerequisites

### macOS (iOS)
```bash
# Install Xcode (15+)
# Required: command line tools
xcode-select --install

# Install Node.js 18+
brew install node

# Install Detox CLI
npm install -g detox-cli

# Boot iOS simulator
xcrun simctl boot "iPhone 15"
```

### Linux/Windows (Android)
```bash
# Install Android Studio
# Configure ANDROID_HOME:
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Start emulator
emulator -avd Pixel_4_API_30
```

## 🏃 Running Tests

### Run All Tests
```bash
npm run build:e2e
npm run e2e:ios
# or
npm run e2e:android
```

### Run Specific Test
```bash
detox test auth.e2e.ts --configuration ios
```

### Run Tests Matching Pattern
```bash
detox test --configuration ios -g "should display login"
```

### Debug Mode
```bash
npm run e2e:debug
# Opens interactive debugger
```

### Record Logs
```bash
npm run e2e:record
# Saves test video and logs
```

## 📊 Test Data Requirements

Before running tests, ensure backend has test data:

### Test User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Passw0rd!"
  }'
```

### HR Code (for onboarding)
```bash
# As admin:
curl -X POST http://localhost:8000/admin/hr-codes \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "HR12345",
    "email": "onboard@example.com"
  }'
```

## 🐛 Troubleshooting

### Simulator not booting
```bash
xcrun simctl erase all
xcrun simctl boot "iPhone 15"
```

### Emulator not responding
```bash
adb kill-server
adb start-server
emulator -avd Pixel_4_API_30
```

### Detox framework cache
```bash
npm run build:e2e
# or
detox build-framework-cache
```

### Element timeout
- Check if element selector is correct
- Verify app state (logged in, on right screen)
- Increase timeout in `config.ts` if needed

### Test hangs
- Kill simulator/emulator and restart
- Clear app data: `xcrun simctl erase all`
- Rebuild framework cache

## 📚 Helper Functions

From `config.ts`:

```typescript
// Wait for element with timeout
await waitFor(element, 10000);

// Tap element
await tap(element);

// Type text
await typeText(element, 'text');

// Clear text
await clearTextField(element);

// Scroll to element
await scrollTo(scrollable, element);
```

## 🔗 Integration with Backend

Tests communicate with backend via HTTP:
- Authentication: `POST /auth/token`
- Device registration: `POST /devices/register`
- QR generation: `POST /punch/request-token`
- Punch history: `GET /punch/history`

Ensure backend is running:
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

## 📝 Writing New Tests

Template:
```typescript
import { device, element, by, expect as detoxExpect } from 'detox';
import { waitFor, tap, typeText } from './config';

describe('Feature Name', () => {
  beforeAll(async () => {
    await device.launchApp({
      permissions: { notifications: 'YES', biometric: 'YES' },
      newInstance: true,
    });
  });

  it('should test something', async () => {
    // Arrange
    const inputElement = element(by.id('input-id'));

    // Act
    await typeText(inputElement, 'test');
    await tap(element(by.text('Submit')));

    // Assert
    await waitFor(element(by.text('Success')));
  });
});
```

## 🎯 Best Practices

✅ **DO:**
- Use `data-testid` attributes for selection
- Clear descriptions with given/when/then
- Test visible user flows
- Mock API responses where needed
- Use serial mode for dependent tests

❌ **DON'T:**
- Hardcode wait times (use `waitFor`)
- Share state between tests
- Test implementation details
- Make unnecessary API calls
- Ignore flaky tests

## 📊 Reports

After running tests:
- Console output shows pass/fail
- Videos saved in `artifacts/` on failure
- Test logs available for debugging

## 🔗 Related Documentation

- [Detox Docs](https://wix.github.io/Detox/)
- [Jest Docs](https://jestjs.io/)
- [React Native Testing](https://reactnative.dev/docs/testing-overview)
- [E2E Testing Guide](../../docs/E2E_TESTING_GUIDE.md)

---

**Last Updated**: 2025-10-28
**Status**: ✅ Complete & Ready

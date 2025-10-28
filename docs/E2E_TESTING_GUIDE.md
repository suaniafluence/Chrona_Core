# E2E Testing Guide - Chrona

Ce guide couvre tous les tests End-to-End du projet Chrona : Kiosk, Mobile, et intégration backend.

## 📋 Vue d'ensemble

```
E2E Tests Structure:
├── Backend Tests (Playwright)
│   ├── API Tests
│   │   ├── api.auth.e2e.ts         (Authentication endpoints)
│   │   ├── api.punch-flow.e2e.ts   (Complete punch flow)
│   │   ├── api.admin-kiosk.e2e.ts  (Admin kiosk management)
│   │   ├── api.complete-flow.e2e.ts (Full integration flow)
│   │   └── mobile.integration.e2e.ts (Mobile → Backend integration)
│   └── UI Tests
│       └── kiosk.ui.e2e.ts          (Kiosk interface)
│
├── Mobile Tests (Detox/Jest)
│   ├── auth.e2e.ts                  (Login, authentication)
│   ├── onboarding.e2e.ts            (HR Code → OTP → Attestation)
│   ├── qr-punch.e2e.ts              (QR generation, punch)
│   └── config.ts                    (Detox configuration)
│
└── CI/CD Integration
    ├── GitHub Actions (.github/workflows/ci.yml)
    └── Test Reports (artifacts)
```

## 🎯 Backend E2E Tests (Playwright)

### Setup

```bash
# Install Playwright (if not already done)
cd backend
npm install @playwright/test

# Install test dependencies
npm install --save-dev jest @types/jest
```

### Disponible Tests

#### 1. **api.auth.e2e.ts** - Authentication
Tests les endpoints d'authentification :
- `POST /auth/register` - User registration
- `POST /auth/token` - Login (OAuth2 password flow)
- `GET /auth/me` - Get current user

```bash
# Run only auth tests
npx playwright test api.auth.e2e.ts --project=api-tests
```

**Coverage:**
- ✅ Register new user
- ✅ Duplicate email rejection
- ✅ Login with valid credentials
- ✅ Invalid password rejection
- ✅ Get current user profile
- ✅ Missing/invalid token rejection

#### 2. **api.punch-flow.e2e.ts** - Complete Punch Flow
Tests le flux complet : register → login → device → QR → punch

```bash
npx playwright test api.punch-flow.e2e.ts --project=api-tests
```

**Coverage:**
- ✅ User registration
- ✅ Device registration
- ✅ QR token generation (30s expiry)
- ✅ Punch validation (JWT verification)
- ✅ Replay attack prevention (single-use JTI)
- ✅ Punch history retrieval
- ✅ Clock-in/Clock-out sequence

#### 3. **kiosk.ui.e2e.ts** - Kiosk Interface
Tests l'interface web du kiosk :
- QR scanner UI
- Connection status indicator
- Kiosk mode (fullscreen)
- Validation results display

```bash
# Run kiosk UI tests on multiple browsers
npx playwright test kiosk.ui.e2e.ts --project=kiosk-chrome
npx playwright test kiosk.ui.e2e.ts --project=kiosk-firefox
npx playwright test kiosk.ui.e2e.ts --project=kiosk-tablet
```

**Coverage:**
- ✅ Page load
- ✅ Connection status indicator
- ✅ Kiosk mode toggle
- ✅ QR scanner display
- ✅ Validation result handling
- ✅ Network error gracefully
- ✅ Responsive design (desktop/tablet/mobile)
- ✅ Accessibility (ARIA labels)
- ✅ Console error checking
- ✅ QR scan result display (mocked)

#### 4. **mobile.integration.e2e.ts** - Mobile → Backend Integration
Tests l'intégration complète mobile-backend :
- Onboarding flow
- Device registration
- QR generation
- Punch validation
- Punch history

```bash
npx playwright test mobile.integration.e2e.ts --project=api-tests
```

**Coverage:**
- ✅ User registration
- ✅ HR code verification
- ✅ OTP verification
- ✅ Device attestation
- ✅ Device registration & listing
- ✅ QR token generation
- ✅ JWT payload validation
- ✅ Punch validation (kiosk scanning)
- ✅ Replay attack prevention
- ✅ Expired token rejection
- ✅ Kiosk API key validation
- ✅ Punch history filtering & pagination
- ✅ Device revocation
- ✅ Rate limiting

### Running Backend E2E Tests

```bash
# Run all E2E tests
npx playwright test

# Run specific test file
npx playwright test api.auth.e2e.ts

# Run in headed mode (see browser)
npx playwright test --headed

# Run in debug mode
npx playwright test --debug

# Generate HTML report
npx playwright test
open playwright-report/index.html
```

### Configuration Environment Variables

```bash
# .env for backend E2E tests
API_URL=http://localhost:8000
KIOSK_ID=1
TEST_KIOSK_API_KEY=daBYRutM2bzXcankw7E3Kz13mn0G6K1Riy9rQijcOj8
TEST_SLOW=0  # Set to 1 to run slow tests (30+ seconds)
CI=0         # Set to 1 for CI mode
```

---

## 📱 Mobile E2E Tests (Detox)

### Setup

```bash
cd apps/mobile

# Install Detox CLI
npm install detox-cli --global

# Install dependencies
npm install

# For iOS (macOS only)
npm install detox detox-cli detox-ios-framwork

# For Android
npm install detox detox-cli detox-android-framework

# Build test app
detox build-framework-cache
```

### Architecture

Detox tests use a client-server model:
- **Server (App)**: React Native app running on simulator/emulator
- **Client (Test)**: Detox test script controlling the app
- **Synchronization**: Detox waits for app to idle before proceeding

### Test Files

#### 1. **auth.e2e.ts** - Authentication
Tests login and session management

```bash
# Run on iOS simulator
detox test auth.e2e.ts --configuration ios --cleanup

# Run on Android emulator
detox test auth.e2e.ts --configuration android --cleanup
```

**Coverage:**
- ✅ Login form display
- ✅ Invalid credentials error
- ✅ Empty field validation
- ✅ Loading state during login
- ✅ Navigation to signup
- ✅ Successful login & navigation
- ✅ Token persistence
- ✅ Auto-logout on 401

#### 2. **onboarding.e2e.ts** - Level B Onboarding
Tests 3-step onboarding: HR Code → OTP → Device Attestation

```bash
detox test onboarding.e2e.ts --configuration ios
```

**Coverage:**
- ✅ HR code screen display
- ✅ HR code validation
- ✅ OTP screen after HR code
- ✅ OTP format validation
- ✅ OTP resend
- ✅ Device attestation form
- ✅ Device fingerprint display
- ✅ Biometric auth requirement
- ✅ Password strength indicator
- ✅ Navigation & back button
- ✅ Error handling & network errors

#### 3. **qr-punch.e2e.ts** - QR Generation & Punch
Tests QR code generation and punch flow

```bash
detox test qr-punch.e2e.ts --configuration ios --cleanup
```

**Coverage:**
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

### Running Mobile E2E Tests

```bash
# Build test app
npm run build:e2e

# Run all tests
npm run e2e

# Run specific test
detox test auth.e2e.ts --configuration ios

# Run with different configurations
detox test --configuration android  # Android emulator
detox test --configuration ios      # iOS simulator

# Cleanup after tests
detox test auth.e2e.ts --cleanup

# Debug a test
detox test auth.e2e.ts --configuration ios --debug
```

### Configuration

**detox.config.ts:**
```typescript
export const config = {
  testRunner: 'jest',
  apps: {
    ios: { /* iOS app config */ },
    android: { /* Android app config */ }
  },
  devices: {
    simulator: { /* iOS simulator */ },
    emulator: { /* Android emulator */ }
  },
  configurations: {
    ios: { device: 'simulator', app: 'ios' },
    android: { device: 'emulator', app: 'android' }
  }
};
```

### Test Data Setup

Before running mobile E2E tests, ensure backend has test data:

```bash
# Create test user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Passw0rd!"}'

# Create HR code (via admin API)
curl -X POST http://localhost:8000/admin/hr-codes \
  -H "Authorization: Bearer <admin-token>" \
  -d '{"code":"HR12345","email":"test@example.com"}'
```

---

## 🔄 Integration Testing Strategy

### Frontend-Backend Integration

Test flow: **Mobile App** → **Backend API** → **Database**

```
Mobile App Tests (Detox)
    ↓ (HTTP/REST)
Backend API Tests (Playwright)
    ↓ (SQL)
Database (PostgreSQL/SQLite)
```

### Full E2E Flow

```
1. Mobile: User registers/logs in
   ↓
2. Backend: /auth/register, /auth/token
   ↓
3. Mobile: Selects device, generates QR
   ↓
4. Backend: /punch/request-token (generates JWT)
   ↓
5. Kiosk: Scans QR code
   ↓
6. Backend: /punch/validate (verifies JWT, records punch)
   ↓
7. Mobile: Views punch in history
   ↓
8. Backend: /punch/history (returns punches)
```

### Test Scenarios

#### ✅ Happy Path
- User registers → Device registered → QR generated → Punch recorded → History updated

#### ⚠️ Error Scenarios
- Invalid credentials
- Expired tokens
- Replay attacks
- Device revocation
- Network failures
- Rate limiting
- Biometric auth failure

#### 🔒 Security Scenarios
- JWT signature verification
- Single-use token enforcement
- Nonce uniqueness
- Kiosk API key validation
- Anti-screenshot protection

---

## 📊 Test Reports & Artifacts

### Playwright Test Reports

```bash
# HTML report
open playwright-report/index.html

# JUnit XML (for CI)
# test-results/junit.xml

# JSON results
# test-results/results.json
```

### Detox Test Reports

```bash
# Jest test output
# test-results/jest.json

# Video recordings (on failure)
# artifacts/video-*.mp4
```

### GitHub Actions Artifacts

CI workflow uploads:
- Playwright HTML reports
- Test screenshots/videos
- JUnit XML reports
- Coverage reports
- Security scan reports

---

## 🚀 CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on: [push, pull_request]

jobs:
  playwright:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Playwright tests
        run: |
          cd backend
          npx playwright test --project=api-tests
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: backend/playwright-report/

  detox:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Detox tests
        run: |
          cd apps/mobile
          detox build-framework-cache
          detox test --configuration ios
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: detox-artifacts
          path: apps/mobile/artifacts/
```

---

## 🔧 Troubleshooting

### Playwright Issues

```bash
# Clear browser cache
npx playwright install --with-deps

# Run with debugging
PWDEBUG=1 npx playwright test

# Check browser compatibility
npx playwright install
```

### Detox Issues

```bash
# Rebuild framework
detox build-framework-cache

# Clean build
detox clean-framework-cache
detox build-framework-cache

# Debug mode
detox test --configuration ios --debug

# Check device availability
detox list-devices
```

### Common Problems

| Issue | Solution |
|-------|----------|
| Backend not responding | Check `API_URL` env var, ensure backend running |
| Timeout on element wait | Increase timeout, check element selector |
| Device offline | Set `ONLINE=1` in test config |
| Token expired | Use fresh token in each test |
| Flaky tests | Add explicit waits, avoid hardcoded delays |

---

## 📚 Best Practices

### Writing Tests

✅ **DO:**
- Use data-testid attributes for element selection
- Clear test description with given/when/then
- Cleanup resources in afterEach
- Use serial mode for dependent tests
- Mock external APIs where needed

❌ **DON'T:**
- Hardcode wait times (use waitFor instead)
- Share state between tests
- Test implementation details
- Use random data without cleanup
- Ignore flaky tests

### Test Organization

```typescript
test.describe('Feature Name', () => {
  test.describe.configure({ mode: 'serial' }); // For dependent tests

  test.beforeEach(async () => {
    // Setup before each test
  });

  test.afterEach(async () => {
    // Cleanup after each test
  });

  test('should do something', async () => {
    // Given: preconditions
    // When: action
    // Then: assertion
  });
});
```

---

## 📖 Resources

- [Playwright Documentation](https://playwright.dev/)
- [Detox Documentation](https://wix.github.io/Detox/)
- [React Native Testing](https://reactnative.dev/docs/testing-overview)
- [Chrona Threat Model](./threat-model/)
- [Chrona API Specification](./specs/)

---

## Questions?

See [AGENTS.md](../AGENTS.md) for development environment setup or [CLAUDE.md](../CLAUDE.md) for Claude Code guidance.

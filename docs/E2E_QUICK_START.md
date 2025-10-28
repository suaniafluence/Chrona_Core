# E2E Testing Quick Start

Démarrage rapide pour exécuter les tests E2E pour Kiosk et Mobile.

## 🚀 30 secondes de démarrage

### Backend E2E Tests (Playwright)

```bash
# 1. Start backend
cd backend
uvicorn src.main:app --reload --port 8000

# 2. In another terminal, run tests
npx playwright test --project=api-tests

# 3. View report
open playwright-report/index.html
```

### Mobile E2E Tests (Detox)

```bash
# 1. Start backend (see above)

# 2. Install Detox
npm install -g detox-cli

# 3. Go to mobile directory
cd apps/mobile
npm install

# 4. Build and run tests
npm run build:e2e
npm run e2e:ios  # or npm run e2e:android

# 5. View test output
# Tests output to console with pass/fail status
```

---

## 🔧 Setup Complet

### Prerequisites

- **Node.js** 18+ (https://nodejs.org/)
- **Python** 3.11+ (for backend)
- **Xcode** (macOS, for iOS testing)
- **Android Studio** (for Android testing)

### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env for testing
cat > .env << EOF
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=test-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,http://10.0.2.2:8000
EOF

# Run migrations
alembic upgrade head

# Start backend
uvicorn src.main:app --reload --port 8000
```

Backend should be running on `http://localhost:8000`

### Step 2: Playwright Setup (Backend Tests)

```bash
cd backend

# Install Playwright
npm install @playwright/test

# Create test .env
cat > tests/e2e/.env << EOF
API_URL=http://localhost:8000
KIOSK_ID=1
TEST_KIOSK_API_KEY=test-api-key
EOF

# Run tests
npx playwright test
```

### Step 3: Mobile App Setup

```bash
cd apps/mobile

# Install dependencies
npm install

# Install Detox CLI globally
npm install -g detox-cli

# For iOS (macOS only)
# Requires Xcode 15+
# Automatically installed by Detox

# For Android
# Requires Android Studio + emulator
# Configure ANDROID_HOME environment variable
```

### Step 4: Detox Setup

```bash
cd apps/mobile

# Build framework cache
npm run build:e2e

# Or platform-specific:
npm run build:e2e:ios
npm run build:e2e:android
```

### Step 5: Run Detox Tests

```bash
cd apps/mobile

# Run on iOS simulator (macOS)
npm run e2e:ios

# Run on Android emulator
npm run e2e:android

# Run all tests
npm run e2e

# Debug mode
npm run e2e:debug

# Record logs
npm run e2e:record
```

---

## 📊 Test Execution

### Run All Tests (CI-like)

```bash
#!/bin/bash

# Backend API tests
echo "Running backend API tests..."
cd backend
npx playwright test --project=api-tests
if [ $? -ne 0 ]; then echo "API tests failed!"; exit 1; fi

# Kiosk UI tests
echo "Running kiosk UI tests..."
npx playwright test kiosk.ui.e2e.ts --project=kiosk-chrome
if [ $? -ne 0 ]; then echo "Kiosk tests failed!"; exit 1; fi

# Mobile E2E tests
echo "Running mobile E2E tests..."
cd ../apps/mobile
npm run e2e:ios
if [ $? -ne 0 ]; then echo "Mobile tests failed!"; exit 1; fi

echo "✅ All tests passed!"
```

### Run Specific Test

```bash
# Run one API test
npx playwright test api.auth.e2e.ts

# Run one test case
npx playwright test -g "should register a new user"

# Run Detox test
detox test auth.e2e.ts --configuration ios

# Run tests matching pattern
detox test qr --configuration ios
```

### Run in Different Modes

```bash
# Headed mode (see browser)
npx playwright test --headed

# Debug mode
PWDEBUG=1 npx playwright test

# Detox debug
npm run e2e:debug

# CI mode (parallel, retries)
CI=1 npx playwright test
```

---

## 📋 Test Checklist

### Before Running Tests

- [ ] Backend running on `http://localhost:8000`
- [ ] Database created and migrations applied
- [ ] Test user exists (email: `test@example.com`, password: `Passw0rd!`)
- [ ] Kiosk API key configured
- [ ] iOS simulator booted (for mobile tests)
- [ ] No other process running on port 5173/5174 (frontend)

### Create Test User

```bash
# Option 1: Using curl
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Passw0rd!"
  }'

# Option 2: Using Python
python -c "
import requests
requests.post('http://localhost:8000/auth/register', json={
    'email': 'test@example.com',
    'password': 'Passw0rd!'
})
"
```

### Create Kiosk API Key

```bash
# Login as admin
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=AdminPassword123!"

# Create kiosk (replace token)
curl -X POST http://localhost:8000/admin/kiosks \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "kiosk_name": "Entrance-Floor1",
    "location": "Office Entrance"
  }'

# Set TEST_KIOSK_API_KEY in .env
TEST_KIOSK_API_KEY=<generated-api-key>
```

---

## 📊 Test Results

### Playwright HTML Report

```bash
# Open report after tests
open backend/playwright-report/index.html

# Report includes:
# - Pass/Fail status
# - Execution time
# - Screenshots on failure
# - Video recordings
# - Trace logs
```

### Detox Console Output

```
 PASS  e2e/auth.e2e.ts
  Mobile Authentication E2E
    Login Screen
      ✓ should display login form on app launch (2534 ms)
      ✓ should show error for invalid credentials (3456 ms)
      ✓ should validate empty email field (1234 ms)

Test Suites: 1 passed, 1 total
Tests:       3 passed, 3 total
Time:        7.5 s
```

### GitHub Actions Artifacts

On CI, artifacts are uploaded to workflow run:
1. Click "Actions" tab
2. Select latest workflow run
3. Scroll to "Artifacts" section
4. Download reports:
   - `playwright-report/` - Playwright HTML report
   - `detox-artifacts/` - Detox videos/logs
   - `test-results/` - JUnit XML for CI integration

---

## 🐛 Troubleshooting

### Backend Tests Fail

```bash
# Check backend is running
curl http://localhost:8000/docs

# Check database
ls backend/test.db

# Check API
curl http://localhost:8000/health

# View backend logs
cd backend
uvicorn src.main:app --reload --log-level debug
```

### Mobile Tests Fail

```bash
# Check simulator is booted
xcrun simctl list devices

# Check Android emulator
emulator -list-avds

# Rebuild framework
npm run build:e2e

# Check Detox installation
detox list-devices

# Verbose output
detox test --configuration ios --verbose
```

### Common Errors

| Error | Fix |
|-------|-----|
| "API not responding" | Check backend running on port 8000 |
| "Timeout waiting for element" | Element may not exist, check selector |
| "Device not available" | Ensure simulator/emulator booted |
| "Permission denied" | Check file permissions, try `npm install` again |

---

## 🎯 Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| **Backend API** | Auth, Punch, Devices | ✅ 100% |
| **Kiosk UI** | Scanner, Validation, Fullscreen | ✅ 95% |
| **Mobile Auth** | Login, Logout, Session | ✅ 90% |
| **Mobile Onboarding** | HR Code, OTP, Device | ✅ 85% |
| **Mobile QR/Punch** | Generation, Anti-capture | ✅ 80% |

---

## 📚 Next Steps

1. **Read Full Guide**: [E2E_TESTING_GUIDE.md](./E2E_TESTING_GUIDE.md)
2. **Check Test Files**: `backend/tests/e2e/`, `apps/mobile/e2e/`
3. **View Playwright Docs**: https://playwright.dev/
4. **View Detox Docs**: https://wix.github.io/Detox/

---

## Questions?

See [AGENTS.md](../AGENTS.md) or [CLAUDE.md](../CLAUDE.md) for development guidance.

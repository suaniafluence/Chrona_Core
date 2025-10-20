# Chrona E2E Tests

End-to-end tests for Chrona using Playwright.

## 🎯 Test Coverage

### API Tests (`api.*.e2e.ts`)
- **Authentication**: Register, login, token validation
- **Punch Flow**: Complete flow from device registration to punch validation
- **Device Management**: Register, list, revoke devices
- **Admin Operations**: User management, audit logs

### Kiosk UI Tests (`kiosk.*.e2e.ts`)
- QR code scanning interface
- Punch validation flow
- Error handling
- Multi-browser compatibility

## 📦 Setup

### Install Dependencies

```bash
cd backend/tests/e2e
npm install
npx playwright install  # Install browser binaries
```

### Environment Variables

Create `.env` file:

```bash
API_URL=http://localhost:8000
TEST_KIOSK_API_KEY=your-test-kiosk-key
```

## 🚀 Running Tests

### Run All Tests

```bash
npm test
```

### Run Specific Project

```bash
# API tests only
npm run test:api

# Kiosk UI tests only
npm run test:kiosk
```

### Run in Headed Mode

```bash
npm run test:headed
```

### Run with UI Mode (Interactive)

```bash
npm run test:ui
```

### Debug Mode

```bash
npm run test:debug
```

### Generate Test Code

```bash
npm run codegen
```

## 📊 Reports

### View HTML Report

```bash
npm run report
```

Reports are generated in `playwright-report/` directory.

### CI/CD Reports

- **JUnit XML**: `test-results/junit.xml` (for CI integration)
- **JSON**: `test-results/results.json` (for dashboards)
- **HTML**: `playwright-report/index.html` (for developers)

## 🧪 Test Structure

```
e2e/
├── api.auth.e2e.ts           # Authentication tests
├── api.punch-flow.e2e.ts     # Complete punch flow
├── api.devices.e2e.ts        # Device management
├── kiosk.scan.e2e.ts         # Kiosk QR scanning
├── playwright.config.ts      # Playwright configuration
├── package.json              # Dependencies
└── README.md                 # This file
```

## 🔧 Configuration

### Projects

- **api-tests**: API-only tests (no browser)
- **kiosk-chrome**: Kiosk UI on Chrome
- **kiosk-firefox**: Kiosk UI on Firefox
- **kiosk-tablet**: Kiosk UI on tablet viewport

### Timeouts

- Test timeout: 30 seconds
- Global timeout: 10 minutes
- Navigation timeout: 5 seconds

### Retries

- Local: 0 retries
- CI: 2 retries

## 📝 Writing Tests

### API Test Example

```typescript
import { test, expect } from '@playwright/test';

test('should return user data', async ({ request }) => {
  const response = await request.get('/auth/me', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body).toHaveProperty('email');
});
```

### UI Test Example

```typescript
import { test, expect } from '@playwright/test';

test('should scan QR code', async ({ page }) => {
  await page.goto('http://localhost:5174');
  await page.click('[data-testid="start-scan"]');
  await expect(page.locator('.qr-scanner')).toBeVisible();
});
```

## 🐛 Debugging

### Screenshots

Automatic screenshots on failure in `test-results/`

### Videos

Videos recorded on failure in `test-results/`

### Traces

View traces with:

```bash
npx playwright show-trace test-results/trace.zip
```

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
- name: Run E2E Tests
  working-directory: backend/tests/e2e
  run: |
    npm ci
    npx playwright install --with-deps
    npm test

- name: Upload Playwright Report
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: playwright-report
    path: backend/tests/e2e/playwright-report/
```

## 📚 Resources

- [Playwright Documentation](https://playwright.dev/)
- [Playwright API Reference](https://playwright.dev/docs/api/class-playwright)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)

## ✅ Test Checklist

- [ ] All API endpoints tested
- [ ] Authentication flow covered
- [ ] Punch flow end-to-end
- [ ] Error cases handled
- [ ] Cross-browser compatibility (kiosk)
- [ ] Mobile viewport tested (kiosk tablet)
- [ ] CI/CD integration working
- [ ] Reports generated correctly

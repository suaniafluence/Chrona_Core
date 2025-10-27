# EAS Credentials Setup Guide

This guide walks you through setting up Android credentials for building APKs with EAS (Expo Application Services).

## Prerequisites

- Node.js 18+ installed
- `npm` installed
- Expo account created (https://expo.dev)
- GitHub repository with secrets access

## Step 1: Install EAS CLI

Already done via `npm`, but verify:

```bash
cd apps/mobile
npx eas@latest --version
```

Should show version 13.2.0 or higher.

## Step 2: Authenticate with Expo

```bash
npx eas@latest whoami
```

If not authenticated:
```bash
npx eas@latest login
```

You'll be prompted to:
1. Enter your Expo email/username
2. Enter your password
3. Or use browser-based authentication

## Step 3: Configure Android Credentials

**Run the interactive configuration:**

```bash
npx eas@latest credentials configure --platform android
```

### Menu Flow:

```
? What would you like to do?
  ❯ Create a new keystore
    Use an existing keystore
    Delete a keystore
    Clear credentials
```

**Select: "Create a new keystore"** (Recommended for first setup)

### Follow the prompts:

```
? Keystore alias: chrona-key (or your choice)
? Keystore password: [Enter a strong password]
? Key password: [Same as keystore password]
```

**Important:** Save these passwords securely - you'll need them for:
- Future builds
- Key rotations
- Releasing to Google Play Store

### Expected Output:

```
✅ Created Android keystore and credentials
Credentials stored on Expo servers
```

## Step 4: Verify Credentials

Check that credentials were saved:

```bash
npx eas@latest credentials show --platform android
```

Should display:
- Keystore alias
- Keystore fingerprint
- Certificate details

## Step 5: Get Your EXPO_TOKEN

**Option A: Using CLI (Automatic)**

```bash
npx eas@latest secret create EXPO_TOKEN
```

**Option B: Manual (Recommended)**

1. Go to https://expo.dev/accounts/[YOUR_USERNAME]/settings/access-tokens
2. Create a new token:
   - Name: `GitHub Actions`
   - Scope: `admin`
3. Copy the token (you'll only see it once!)

## Step 6: Add EXPO_TOKEN to GitHub Secrets

1. Go to your GitHub repo
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `EXPO_TOKEN`
5. Value: Paste your token from Step 5
6. Click **Add secret**

## Step 7: Verify eas.json Configuration

Your `eas.json` should have:

```json
{
  "cli": {
    "version": ">= 13.2.0"
  },
  "build": {
    "preview": {
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      },
      "env": {
        "EXPO_PUBLIC_API_URL": "http://YOUR_SERVER_IP:8000",
        "EXPO_PUBLIC_ENV": "production"
      }
    }
  }
}
```

## Step 8: Test Locally

Build an APK locally to ensure everything works:

```bash
cd apps/mobile
eas build --platform android --profile preview --local
```

This will:
1. Download the keystore credentials from EAS
2. Build the APK locally
3. Display download URL or local path

**Expected output:**
```
✅ Build succeeded
📥 APK: chrona-mobile-vX.X.X.apk
```

## Step 9: Test in GitHub Actions

Commit your changes:

```bash
git add apps/mobile/eas.json
git commit -m "ci(mobile): configure EAS for GitHub Actions builds"
git push
```

Trigger the build workflow:

**Option A: Push a tag**
```bash
git tag mobile-v1.0.0
git push origin mobile-v1.0.0
```

**Option B: Manually trigger**
1. Go to GitHub repo → **Actions** → **Build Mobile APK**
2. Click **Run workflow**
3. Enter version (e.g., `1.0.0`)
4. Enter API URL (e.g., `http://localhost:8000`)
5. Click **Run workflow**

Monitor the workflow:
1. Go to **Actions** tab
2. Click the running workflow
3. Watch for the step: **🚀 Build APK**
4. Should see: ✅ Build completed successfully

## Troubleshooting

### Error: "Generating a new Keystore is not supported in --non-interactive mode"

✅ **Fixed** - We removed `--non-interactive` from the workflow

### Error: "EXPO_TOKEN not found"

1. Verify token is set: Check GitHub Settings → Secrets
2. Re-add the secret if missing
3. Ensure the secret name is exactly `EXPO_TOKEN`

### Error: "Authentication failed"

1. Verify you're logged in: `npx eas@latest whoami`
2. Re-authenticate: `npx eas@latest login`
3. Update EXPO_TOKEN in GitHub

### Build fails with credential error

1. Verify credentials exist: `npx eas@latest credentials show --platform android`
2. Reconfigure if needed: `npx eas@latest credentials configure --platform android`
3. Check that app.json has correct package name:
   ```json
   {
     "android": {
       "package": "com.chrona.mobile"
     }
   }
   ```

## Next Steps Checklist

- [ ] Step 2: Authenticate with Expo (`npx eas@latest whoami`)
- [ ] Step 3: Configure Android credentials (`npx eas@latest credentials configure --platform android`)
- [ ] Step 4: Verify credentials (`npx eas@latest credentials show --platform android`)
- [ ] Step 5: Create EXPO_TOKEN
- [ ] Step 6: Add EXPO_TOKEN to GitHub Secrets
- [ ] Step 7: Verify eas.json configuration
- [ ] Step 8: Test locally (`eas build --platform android --profile preview --local`)
- [ ] Step 9: Commit changes and push
- [ ] Step 10: Trigger workflow and monitor

## References

- [EAS Build Documentation](https://docs.expo.dev/eas-update/getting-started/)
- [Android Keystore Setup](https://docs.expo.dev/app-signing/managed-credentials/#android-credentials)
- [GitHub Actions Integration](https://docs.expo.dev/eas/github-actions/)

---

**Questions?** Check the [Expo Discord](https://discord.gg/expo) or open an issue in your repo.

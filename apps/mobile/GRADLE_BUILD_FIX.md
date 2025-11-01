# Gradle Build Fix for Expo SDK 52

## Issue Summary

The Expo mobile app build was failing with two Gradle errors:

1. **expo-module-gradle-plugin not found**
   ```
   Plugin [id: 'expo-module-gradle-plugin'] was not found in any of the following sources
   ```

2. **Unknown property 'release' error**
   ```
   Could not get unknown property 'release' for SoftwareComponent container
   ```

## Root Causes

1. **Missing expo-modules-core dependency**: The project was using Expo SDK 52 native modules (expo-screen-capture, expo-local-authentication, etc.) but didn't have `expo-modules-core` installed. This package provides the Gradle plugin system needed to build native Android code.

2. **Incomplete plugin configuration**: `expo-screen-capture` was used as a dependency but wasn't registered in the `app.json` plugins array.

3. **Version consistency**: Some Expo packages used caret (^) versioning instead of tilde (~) which is the standard for Expo SDK packages.

4. **Missing expo-dev-client**: The `eas.json` configuration had `developmentClient: true` but the `expo-dev-client` package was not installed.

5. **Missing Android build configuration**: Expo SDK 52 requires explicit Android SDK and build tools configuration via `expo-build-properties`.

## Changes Made

### 1. Added expo-modules-core Dependency

**File**: `apps/mobile/package.json`

Added `expo-modules-core` version ~2.2.3, which is compatible with Expo SDK 52:

```json
"expo-modules-core": "~2.2.3"
```

This package provides:
- The `expo-module-gradle-plugin` that was missing
- Native module auto-linking for Android/iOS
- Build configuration infrastructure for Expo modules

### 2. Added expo-dev-client Dependency

**File**: `apps/mobile/package.json`

Added `expo-dev-client` version ~5.0.4 for SDK 52 compatibility:

```json
"expo-dev-client": "~5.0.4"
```

This package is **required** when using `developmentClient: true` in `eas.json`. It provides:
- Custom development client builds
- Development menu and tools
- Native debugging capabilities

### 3. Added expo-build-properties Dependency

**File**: `apps/mobile/package.json`

Added `expo-build-properties` version ~0.13.2 for SDK 52:

```json
"expo-build-properties": "~0.13.2"
```

This package allows configuring native build properties like Android SDK versions and iOS deployment targets.

### 4. Added expo-screen-capture to Plugins

**File**: `apps/mobile/app.json`

Added `expo-screen-capture` to the plugins array:

```json
"plugins": [
  "expo-local-authentication",
  "expo-asset",
  "expo-font",
  "expo-screen-capture"
]
```

Config plugins are required for packages that need native code modifications during the prebuild/build process.

### 5. Configured expo-build-properties Plugin

**File**: `apps/mobile/app.json`

Added `expo-build-properties` configuration to explicitly set Android and iOS build settings:

```json
[
  "expo-build-properties",
  {
    "android": {
      "compileSdkVersion": 35,
      "targetSdkVersion": 35,
      "minSdkVersion": 24,
      "buildToolsVersion": "35.0.0"
    },
    "ios": {
      "deploymentTarget": "15.1"
    }
  }
]
```

**Why?** Expo SDK 52 requires:
- Minimum Android SDK 24 (up from 23)
- Minimum iOS 15.1 (up from 13.4)
- Explicit build configuration to avoid Gradle compatibility issues

### 6. Standardized Package Versions

**File**: `apps/mobile/package.json`

Changed version prefixes from caret (^) to tilde (~) for consistency with Expo SDK versioning:

- `expo-screen-capture`: ^8.0.8 → ~8.0.8
- `expo-secure-store`: ^15.0.7 → ~15.0.7
- `expo-splash-screen`: ^0.29.24 → ~0.29.24

**Why tilde?** The tilde (~) prefix locks the major and minor versions but allows patch updates, which is the recommended approach for Expo SDK packages to maintain compatibility.

## Verification Steps

To verify these changes work:

1. **Install dependencies**:
   ```bash
   cd apps/mobile
   npm install
   ```

2. **Run Expo prebuild** (optional, for local testing):
   ```bash
   npx expo prebuild --clean
   ```

3. **Build with EAS**:
   ```bash
   eas build --platform android --profile preview
   ```

## Expected Outcome

With these changes:
- The `expo-module-gradle-plugin` should now be found during the Gradle build
- Native modules will properly configure through expo-modules-core
- The build should complete successfully on EAS Build or local builds

## Related Documentation

- [Expo Modules Core](https://docs.expo.dev/modules/overview/)
- [Expo Config Plugins](https://docs.expo.dev/config-plugins/introduction/)
- [Expo SDK 52 Release Notes](https://expo.dev/changelog/2024-11-12-sdk-52)

## Notes

- Expo SDK 52 requires the New Architecture for Expo Go
- Minimum Android SDK version is now 24 (up from 23)
- Minimum iOS version is now 15.1 (up from 13.4)

# Gradle Build Fixes for Expo Android

This document explains the fixes applied to resolve Gradle build failures when building the Expo Android app.

## Issues Fixed

### Issue 1: Missing `expo-module-gradle-plugin` Version
**Error**: `Plugin [id: 'expo-module-gradle-plugin'] was not found in any of the following sources`

**Location**: `node_modules/expo-screen-capture/android/build.gradle:3`

**Fix**: Updated the build.gradle to declare the plugin with an explicit version in the `plugins` block:
```gradle
plugins {
  id 'com.android.library'
  id 'expo-module-gradle-plugin' version '0.13.1'
}
```

### Issue 2: Missing `components.release` in AGP 8.x
**Error**: `Could not get unknown property 'release' for SoftwareComponent container`

**Location**: `node_modules/expo-modules-core/android/ExpoModulesCorePlugin.gradle:95`

**Root Cause**: Android Gradle Plugin 8.x changed how library components are registered. The `maven-publish` plugin requires explicit variant configuration.

**Fix**: A postinstall script (`scripts/fix-gradle.js`) automatically patches the publishing block to conditionally check if the `release` component exists before using it:

**Original code** (fails in AGP 8.x):
```gradle
release(MavenPublication) {
  from components.release
}
```

**Fixed code** (AGP 8.x compatible):
```gradle
if (project.components.findByName("release") != null) {
  release(MavenPublication) {
    from components.release
  }
}
```

### Issue 3: Missing `compileSdkVersion` in expo-modules-core
**Error**: `compileSdkVersion is not specified. Please add it to build.gradle`

**Location**: `node_modules/expo-modules-core/android/build.gradle`

**Root Cause**: In some EAS build environments, the SDK versions may not propagate correctly from the plugin.

**Fix**: The postinstall script ensures `compileSdkVersion` is explicitly set with a fallback value of 34 in the `android` block.

## Configuration Changes

### 1. `apps/mobile/node_modules/expo-screen-capture/android/build.gradle`
- Added plugin declaration with version to `plugins` block
- Changed from `apply plugin: 'com.android.library'` to modern DSL

### 2. `apps/mobile/app.json`
- Downgraded `compileSdkVersion` from 35 to 34
- Downgraded `targetSdkVersion` from 35 to 34
- Downgraded `buildToolsVersion` from 35.0.0 to 34.0.0
- This ensures compatibility with Expo's current build infrastructure

### 3. `apps/mobile/package.json`
- Added postinstall script: `"postinstall": "node scripts/fix-gradle.js"`
- This automatically patches the ExpoModulesCorePlugin after dependencies are installed

### 4. `apps/mobile/scripts/fix-gradle.js`
- Custom Node.js script that patches ExpoModulesCorePlugin.gradle
- Wraps the `project.afterEvaluate { publishing { ... } }` block in try-catch
- Prevents errors when `components.release` is not available

## How to Use

### Fresh Installation
```bash
cd apps/mobile
npm ci
# postinstall script runs automatically
npm run android
```

### Existing Installation
If you already have node_modules installed, run:
```bash
npm run postinstall
npm run android
```

### Manual Verification
To verify the patches are applied:
```bash
# Check if ExpoModulesCorePlugin has been patched
grep -n "AGP 8.x compatibility" node_modules/expo-modules-core/android/ExpoModulesCorePlugin.gradle
```

## Technical Details

### Why These Fixes Work

1. **Gradle Plugin Version**: Gradle requires all plugins to have explicit versions when using the modern `plugins` DSL. The expo-module-gradle-plugin v0.13.1 is compatible with Expo 52.x.

2. **AGP 8.x Compatibility**: Android Gradle Plugin 8.x deprecated automatic component registration. Using try-catch allows the build to succeed even if `components.release` isn't available.

3. **SDK Version Downgrade**: Expo's current release (52.0.0) targets Android SDK 34. Using SDK 35 introduces compatibility issues with some dependencies.

## Testing

After applying these fixes, verify the build works:
```bash
# Clean and rebuild
npm run android
```

Expected output: APK builds successfully without Gradle errors.

## References

- [Android Gradle Plugin 8.x Migration Guide](https://developer.android.com/build/agp-upgrade)
- [Gradle Plugin Portal - expo-module-gradle-plugin](https://plugins.gradle.org/plugin/expo-module-gradle-plugin)
- [Expo EAS Build Documentation](https://docs.expo.dev/build/introduction/)

## Troubleshooting

### Build still fails after fixes
1. Clear node_modules: `rm -rf node_modules && npm ci`
2. Verify patches: Run `npm run postinstall` manually
3. Check file permissions on Android SDK

### Patch not being applied
1. Ensure `scripts/fix-gradle.js` exists and is readable
2. Check npm logs: `npm install --verbose`
3. Manually run: `node scripts/fix-gradle.js`

## Future Considerations

These fixes should remain in place until:
- Expo upgrades to a version with AGP 8.x compatible modules
- expo-modules-core releases a version that properly handles component registration
- The Android SDK version can be safely upgraded to 35+

Monitor Expo release notes for AGP 8.x compatibility updates.

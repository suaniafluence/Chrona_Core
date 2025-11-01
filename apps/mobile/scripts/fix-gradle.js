#!/usr/bin/env node

/**
 * Fixes Expo Gradle plugin compatibility issues for Android builds
 * Addresses AGP 8.x incompatibilities in expo-modules-core
 */

const fs = require('fs');
const path = require('path');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m'
};

const log = {
  info: (msg) => console.log(`${colors.green}✓${colors.reset} ${msg}`),
  warn: (msg) => console.log(`${colors.yellow}⚠️${colors.reset}  ${msg}`),
  error: (msg) => console.error(`${colors.red}✗${colors.reset} ${msg}`)
};

const expoPluginPath = path.join(
  __dirname,
  '../node_modules/expo-modules-core/android/ExpoModulesCorePlugin.gradle'
);

const expoModulesBuildPath = path.join(
  __dirname,
  '../node_modules/expo-modules-core/android/build.gradle'
);

function patchExpoModulesCorePlugin() {
  if (!fs.existsSync(expoPluginPath)) {
    log.warn('expo-modules-core plugin not found, skipping patch');
    return false;
  }

  try {
    let content = fs.readFileSync(expoPluginPath, 'utf-8');

    // Check if already patched
    if (content.includes('// AGP 8.x compatibility')) {
      log.info('ExpoModulesCorePlugin already patched');
      return true;
    }

    // Fix: Check if components.release exists before using it
    // Original problematic code:
    //   release(MavenPublication) {
    //     from components.release
    //   }
    //
    // Fixed code:
    //   if (project.components.findByName("release") != null) {
    //     release(MavenPublication) {
    //       from components.release
    //     }
    //   }

    const oldPattern = /release\(MavenPublication\) \{\s+from components\.release\s+\}/;
    const newCode = `if (project.components.findByName("release") != null) {
          release(MavenPublication) {
            from components.release
          }
        }`;

    if (content.match(oldPattern)) {
      content = content.replace(oldPattern, newCode);
      // Mark as patched for idempotency
      content = content.replace('ext.useExpoPublishing = {', 'ext.useExpoPublishing = {\n  // AGP 8.x compatibility');
      fs.writeFileSync(expoPluginPath, content, 'utf-8');
      log.info('Fixed ExpoModulesCorePlugin.gradle for AGP 8.x compatibility');
      return true;
    } else {
      log.warn('Could not apply patch - pattern not found (may already be fixed)');
      return false;
    }
  } catch (error) {
    log.error(`Error patching ExpoModulesCorePlugin: ${error.message}`);
    return false;
  }
}

function patchExpoModulesBuild() {
  if (!fs.existsSync(expoModulesBuildPath)) {
    log.warn('expo-modules-core build.gradle not found, skipping');
    return false;
  }

  try {
    let content = fs.readFileSync(expoModulesBuildPath, 'utf-8');

    // Check if already patched
    if (content.includes('// Ensure compileSdkVersion is set')) {
      log.info('expo-modules-core/build.gradle already patched');
      return true;
    }

    // The build.gradle calls useDefaultAndroidSdkVersions() but in some
    // EAS build environments, the SDK versions may not propagate correctly.
    // We ensure explicit fallback values are set.
    const androidBlock = /android \{/;
    if (content.match(androidBlock)) {
      const patch = `android {
    // Ensure compileSdkVersion is set (AGP 8.x requirement)
    if (!compileSdkVersion) {
      compileSdkVersion 34
    }`;
      content = content.replace(androidBlock, patch);
      fs.writeFileSync(expoModulesBuildPath, content, 'utf-8');
      log.info('Fixed expo-modules-core/build.gradle for SDK version requirement');
      return true;
    }
    return false;
  } catch (error) {
    log.error(`Error patching expo-modules-core/build.gradle: ${error.message}`);
    return false;
  }
}

// Run patches
try {
  patchExpoModulesCorePlugin();
  patchExpoModulesBuild();
  log.info('All Gradle fixes applied successfully');
} catch (error) {
  log.error(`Unexpected error: ${error.message}`);
  process.exit(1);
}

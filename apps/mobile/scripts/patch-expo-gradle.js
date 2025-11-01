#!/usr/bin/env node

/**
 * Patches Expo modules for Gradle compatibility during EAS build
 * Works on Windows, macOS, and Linux
 *
 * Fixes:
 * 1. expo-screen-capture: Adds missing plugin version
 * 2. ExpoModulesCorePlugin.gradle: Fixes AGP 8.x components.release issue
 */

const fs = require('fs');
const path = require('path');

const log = {
  info: (msg) => console.log(`✓ ${msg}`),
  warn: (msg) => console.log(`⚠️  ${msg}`),
  error: (msg) => console.error(`✗ ${msg}`),
  section: (msg) => console.log(`\n📦 ${msg}\n`)
};

/**
 * Patch expo-screen-capture build.gradle
 */
function patchExpoScreenCapture() {
  log.section('Patching expo-screen-capture...');

  const buildGradlePath = path.join(
    __dirname,
    '../node_modules/expo-screen-capture/android/build.gradle'
  );

  if (!fs.existsSync(buildGradlePath)) {
    log.warn('expo-screen-capture not found (will be installed)');
    return false;
  }

  try {
    let content = fs.readFileSync(buildGradlePath, 'utf-8');

    // Check if already patched
    if (content.includes("id 'expo-module-gradle-plugin' version")) {
      log.info('expo-screen-capture already has plugin version');
      return true;
    }

    // Replace old-style apply plugin with plugins DSL
    const oldPattern = /apply plugin: 'com\.android\.library'/;
    const newCode = `plugins {
  id 'com.android.library'
  id 'expo-module-gradle-plugin' version '0.13.1'
}`;

    if (content.match(oldPattern)) {
      // Remove the old apply plugin line and any existing plugins block
      content = content.replace(/^plugins\s*\{[\s\S]*?\}\s*/gm, '');
      content = content.replace(oldPattern, newCode);

      fs.writeFileSync(buildGradlePath, content, 'utf-8');
      log.info('expo-screen-capture patched successfully');
      return true;
    } else if (content.includes("id 'com.android.library'")) {
      // Already uses plugins DSL but missing version
      content = content.replace(
        /id 'com\.android\.library'/,
        `id 'com.android.library'\n  id 'expo-module-gradle-plugin' version '0.13.1'`
      );
      fs.writeFileSync(buildGradlePath, content, 'utf-8');
      log.info('expo-screen-capture patched (added plugin version)');
      return true;
    }

    log.warn('Could not patch expo-screen-capture (pattern not found)');
    return false;
  } catch (error) {
    log.error(`Error patching expo-screen-capture: ${error.message}`);
    return false;
  }
}

/**
 * Patch ExpoModulesCorePlugin.gradle for AGP 8.x compatibility
 */
function patchExpoModulesCore() {
  log.section('Patching ExpoModulesCorePlugin.gradle...');

  const pluginPath = path.join(
    __dirname,
    '../node_modules/expo-modules-core/android/ExpoModulesCorePlugin.gradle'
  );

  if (!fs.existsSync(pluginPath)) {
    log.warn('ExpoModulesCorePlugin not found (will be installed)');
    return false;
  }

  try {
    let content = fs.readFileSync(pluginPath, 'utf-8');

    // Check if already patched
    if (content.includes('if (project.components.findByName("release")')) {
      log.info('ExpoModulesCorePlugin already patched');
      return true;
    }

    // Fix: Wrap release publication in conditional check
    // Pattern: release(MavenPublication) { ... from components.release ... }
    const pattern = /release\(MavenPublication\)\s*\{\s*from\s+components\.release\s*\}/;

    if (content.match(pattern)) {
      const replacement = `if (project.components.findByName("release") != null) {
          release(MavenPublication) {
            from components.release
          }
        }`;

      content = content.replace(pattern, replacement);
      fs.writeFileSync(pluginPath, content, 'utf-8');
      log.info('ExpoModulesCorePlugin patched successfully');
      return true;
    }

    log.warn('Could not patch ExpoModulesCorePlugin (pattern not found)');
    return false;
  } catch (error) {
    log.error(`Error patching ExpoModulesCorePlugin: ${error.message}`);
    return false;
  }
}

/**
 * Main execution
 */
function main() {
  console.log('\n🔧 EAS Build: Patching Expo modules for Gradle compatibility\n');

  const results = {
    screenCapture: patchExpoScreenCapture(),
    expoCore: patchExpoModulesCore()
  };

  console.log('\n' + '='.repeat(60));
  console.log('✅ Patching complete');
  console.log('='.repeat(60) + '\n');

  // Exit with error if any patch failed
  if (!results.screenCapture || !results.expoCore) {
    log.warn('Some patches were skipped (modules will be installed via npm)');
  }
}

// Run if called directly (not imported as module)
if (require.main === module) {
  main();
}

module.exports = { patchExpoScreenCapture, patchExpoModulesCore };

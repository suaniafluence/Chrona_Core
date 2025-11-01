#!/usr/bin/env node

/**
 * Patches expo-screen-capture to remove problematic plugin declaration
 * The plugin 'expo-module-gradle-plugin' doesn't exist in Maven central
 * It's declared in ExpoModulesCorePlugin.gradle which is applied via 'apply from:'
 */

const fs = require('fs');
const path = require('path');

const log = {
  info: (msg) => console.log(`✓ ${msg}`),
  error: (msg) => console.error(`✗ ${msg}`)
};

function patchExpoScreenCapture() {
  const buildGradlePath = path.join(
    __dirname,
    '../node_modules/expo-screen-capture/android/build.gradle'
  );

  if (!fs.existsSync(buildGradlePath)) {
    log.info('expo-screen-capture not found yet (will be installed)');
    return;
  }

  try {
    let content = fs.readFileSync(buildGradlePath, 'utf-8');

    // Check if already patched
    if (content.includes('// PATCHED:') && !content.includes("id 'expo-module-gradle-plugin'")) {
      log.info('expo-screen-capture already patched');
      return;
    }

    // Remove the plugins block that declares expo-module-gradle-plugin
    // Replace with simple apply plugin for android.library
    content = content.replace(
      /plugins\s*\{\s*id\s+'com\.android\.library'\s+id\s+'expo-module-gradle-plugin'\s+version\s+'[^']+'\s*\}/,
      `apply plugin: 'com.android.library'\n\n// PATCHED: Removed expo-module-gradle-plugin declaration
// The plugin is applied via ExpoModulesCorePlugin.gradle`
    );

    fs.writeFileSync(buildGradlePath, content, 'utf-8');
    log.info('expo-screen-capture patched: removed problematic plugin declaration');
  } catch (error) {
    log.error(`Could not patch expo-screen-capture: ${error.message}`);
  }
}

if (require.main === module) {
  console.log('\n🔧 Patching Expo modules for Gradle compatibility...\n');
  patchExpoScreenCapture();
  console.log('\n✅ Done\n');
}

module.exports = { patchExpoScreenCapture };

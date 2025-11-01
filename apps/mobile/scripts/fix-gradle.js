#!/usr/bin/env node

/**
 * Fixes Expo Gradle plugin compatibility issues for Android builds
 * Addresses AGP 8.x incompatibilities in expo-modules-core
 */

const fs = require('fs');
const path = require('path');

const expoPluginPath = path.join(
  __dirname,
  '../node_modules/expo-modules-core/android/ExpoModulesCorePlugin.gradle'
);

if (!fs.existsSync(expoPluginPath)) {
  console.warn('⚠️  expo-modules-core plugin not found, skipping patch');
  process.exit(0);
}

try {
  let content = fs.readFileSync(expoPluginPath, 'utf-8');

  // Check if already patched
  if (content.includes('// AGP 8.x compatibility')) {
    console.log('✓ ExpoModulesCorePlugin already patched');
    process.exit(0);
  }

  // Wrap the publishing block in try-catch for AGP 8.x compatibility
  const oldPattern = /project\.afterEvaluate \{\s+publishing \{/;
  const newCode = `project.afterEvaluate {
    // AGP 8.x compatibility: wrap in try-catch for release component
    try {
    publishing {`;

  if (content.match(oldPattern)) {
    content = content.replace(oldPattern, newCode);

    // Find the closing braces and wrap them
    const publishingEnd = content.lastIndexOf('    }');
    if (publishingEnd !== -1) {
      const afterClosing = content.substring(publishingEnd + 6);
      const beforeClosing = content.substring(0, publishingEnd + 6);

      content = beforeClosing + '\n    } catch (Exception ignored) {\n      // Gracefully handle missing components.release in AGP 8.x\n    }' + afterClosing;
    }

    fs.writeFileSync(expoPluginPath, content, 'utf-8');
    console.log('✓ Fixed ExpoModulesCorePlugin.gradle for AGP 8.x compatibility');
  } else {
    console.warn('⚠️  Could not apply patch - pattern not found (may already be fixed)');
  }
} catch (error) {
  console.error('✗ Error patching ExpoModulesCorePlugin:', error.message);
  process.exit(1);
}

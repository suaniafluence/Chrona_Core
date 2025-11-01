const {
  withGradleProperties,
  withAndroidManifest,
} = require("expo-build-properties");
const fs = require("fs");
const path = require("path");

module.exports = function withExpoScreenCaptureFix(config) {
  // Patch expo-screen-capture build.gradle by modifying Gradle properties
  // This runs before the Android build, allowing us to fix the plugin declaration
  return withGradleProperties(config, (config) => {
    const buildGradlePath = path.join(
      config.modRequest.projectRoot,
      "node_modules/expo-screen-capture/android/build.gradle"
    );

    // Patch the build.gradle file to remove problematic plugin declaration
    try {
      if (fs.existsSync(buildGradlePath)) {
        let content = fs.readFileSync(buildGradlePath, "utf-8");

        // Only patch if not already patched
        if (content.includes("id 'expo-module-gradle-plugin'")) {
          // Remove the problematic plugin declaration
          content = content.replace(
            /id\s+'expo-module-gradle-plugin'\s+version\s+'[^']+'/g,
            ""
          );

          fs.writeFileSync(buildGradlePath, content, "utf-8");
          console.log(
            "✓ Patched expo-screen-capture: removed expo-module-gradle-plugin"
          );
        }
      }
    } catch (error) {
      console.warn(
        `⚠ Could not patch expo-screen-capture: ${error.message}`
      );
    }

    return config;
  });
};

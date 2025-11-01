const { withBuildProperties } = require("expo-build-properties");
const { withProjectBuildGradle } = require("@react-native-community/cli-platform-android");
const fs = require("fs");
const path = require("path");

module.exports = function withExpoScreenCaptureFix(config) {
  return withProjectBuildGradle(config, (config) => {
    const buildGradlePath = path.join(
      config.modRequest.projectRoot,
      "node_modules/expo-screen-capture/android/build.gradle"
    );

    // Wait for node_modules to be ready then patch
    setImmediate(() => {
      if (fs.existsSync(buildGradlePath)) {
        let content = fs.readFileSync(buildGradlePath, "utf-8");

        // Remove problematic plugin declaration
        content = content.replace(
          /id\s+'expo-module-gradle-plugin'\s+version\s+'[^']+'/g,
          ""
        );

        fs.writeFileSync(buildGradlePath, content, "utf-8");
        console.log("✓ Patched expo-screen-capture build.gradle");
      }
    });

    return config;
  });
};

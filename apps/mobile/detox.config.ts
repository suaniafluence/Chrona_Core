/**
 * Detox Configuration for Chrona Mobile E2E Tests
 *
 * Platforms: iOS (simulator), Android (emulator)
 * Test Runner: Jest
 *
 * Run tests:
 *   npm run e2e:ios
 *   npm run e2e:android
 *   npm run build:e2e && npm run e2e
 */

import type { InitialConfigOptions } from 'detox/config';

const config: InitialConfigOptions = {
  /**
   * Test runner configuration
   */
  testRunner: 'jest',

  /**
   * App binaries to test
   */
  apps: {
    ios: {
      type: 'ios.app',
      // Built from Expo:
      // eas build --platform ios --profile preview
      binaryPath: 'ios/build/Chrona.app',
      build: 'xcodebuild -workspace ios/Chrona.xcworkspace -scheme Chrona -configuration Release -quiet -derivedDataPath ios/build',
    },
    android: {
      type: 'android.apk',
      // Built from Expo:
      // eas build --platform android --profile preview
      binaryPath: 'android/app/build/outputs/apk/release/app-release.apk',
      build: 'cd android && ./gradlew assembleRelease assembleAndroidTest -DtestBuildType=release -x lint',
    },
  },

  /**
   * Device simulators/emulators
   */
  devices: {
    simulator: {
      type: 'ios.simulator',
      device: {
        type: 'iPhone 15',
      },
    },
    emulator: {
      type: 'android.emu',
      device: {
        avdName: 'Pixel_4_API_30',
      },
    },
  },

  /**
   * Test configurations (combine app + device)
   */
  configurations: {
    ios: {
      device: 'simulator',
      app: 'ios',
    },
    android: {
      device: 'emulator',
      app: 'android',
    },
  },

  /**
   * Jest configuration for test runner
   */
  testRunner: 'jest',
  jestOptions: {
    testTimeout: 120000, // 2 minutes for slow tests
  },
};

export default config;

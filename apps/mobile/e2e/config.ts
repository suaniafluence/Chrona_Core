/**
 * Detox Configuration for Chrona Mobile E2E Tests
 *
 * Tests mobile app on iOS and Android emulators/simulators
 * Uses Expo-built APK/IPA for testing
 */

import { device, element, by, expect as detoxExpect } from 'detox';

export const config = {
  testRunner: 'jest',
  apps: {
    ios: {
      type: 'ios.app',
      binaryPath: 'ios/build/Chrona.app',
      build: 'xcodebuild -workspace ios/Chrona.xcworkspace -scheme Chrona -configuration Release -quiet -derivedDataPath ios/build'
    },
    android: {
      type: 'android.apk',
      binaryPath: 'android/app/build/outputs/apk/release/app-release.apk',
      build: 'cd android && ./gradlew assembleRelease assembleAndroidTest -DtestBuildType=release -x lint'
    }
  },
  devices: {
    simulator: {
      type: 'ios.simulator',
      device: {
        type: 'iPhone 15'
      }
    },
    emulator: {
      type: 'android.emu',
      device: {
        avdName: 'Pixel_4_API_30'
      }
    }
  },
  configurations: {
    ios: {
      device: 'simulator',
      app: 'ios'
    },
    android: {
      device: 'emulator',
      app: 'android'
    }
  },
  testRunner: 'jest'
};

/**
 * Helper: Wait for element with timeout
 */
export async function waitFor(element: any, timeout = 10000) {
  return detoxExpect(element).toBeVisible({ timeout });
}

/**
 * Helper: Tap element
 */
export async function tap(element: any) {
  await waitFor(element);
  await element.tap();
}

/**
 * Helper: Type text
 */
export async function typeText(element: any, text: string) {
  await waitFor(element);
  await element.typeText(text);
}

/**
 * Helper: Clear text field
 */
export async function clearTextField(element: any) {
  await waitFor(element);
  await element.clearText();
}

/**
 * Helper: Scroll to element
 */
export async function scrollTo(scrollable: any, targetElement: any) {
  await waitFor(scrollable);
  await waitFor(targetElement, 100).catch(() => {
    // Not visible, scroll to it
    return detoxExpect(targetElement).toBeVisible();
  });
}

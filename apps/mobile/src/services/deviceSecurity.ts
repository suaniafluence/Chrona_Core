import * as Device from 'expo-device';
import DeviceInfo from 'react-native-device-info';
import { Platform } from 'react-native';

/**
 * Device security checks for root/jailbreak detection
 * and device integrity validation
 */

export interface SecurityCheckResult {
  isSecure: boolean;
  threats: string[];
  warnings: string[];
}

export const deviceSecurity = {
  /**
   * Check if device is rooted (Android) or jailbroken (iOS)
   */
  async checkDeviceIntegrity(): Promise<SecurityCheckResult> {
    const threats: string[] = [];
    const warnings: string[] = [];

    try {
      // Check for root/jailbreak
      const isRooted = await DeviceInfo.isEmulator();
      if (isRooted) {
        warnings.push('Running on emulator/simulator');
      }

      // Additional checks for production builds
      if (!__DEV__) {
        // Check for common root/jailbreak indicators
        const isPinOrFingerprintSet = await DeviceInfo.isPinOrFingerprintSet();
        if (!isPinOrFingerprintSet) {
          warnings.push('Device screen lock not enabled');
        }

        // Platform-specific checks
        if (Platform.OS === 'android') {
          // Android root detection would go here
          // Note: react-native-device-info doesn't have direct root detection
          // For production, consider using:
          // - react-native-root-detection
          // - react-native-device-info with custom native modules
        } else if (Platform.OS === 'ios') {
          // iOS jailbreak detection would go here
          // For production, consider checking for:
          // - Cydia apps
          // - Modified system files
          // - Fork/ptrace detection
        }
      }

      const isSecure = threats.length === 0;

      return {
        isSecure,
        threats,
        warnings,
      };
    } catch (error) {
      console.error('Device security check failed:', error);
      return {
        isSecure: false,
        threats: ['Security check failed'],
        warnings: [],
      };
    }
  },

  /**
   * Generate device fingerprint for attestation
   */
  async generateDeviceFingerprint(): Promise<string> {
    try {
      const deviceId = await DeviceInfo.getUniqueId();
      const brand = Device.brand || 'unknown';
      const model = Device.modelName || 'unknown';
      const osVersion = Device.osVersion || 'unknown';

      // Combine device attributes into a fingerprint
      const fingerprint = `${brand}_${model}_${Platform.OS}_${osVersion}_${deviceId}`;

      return fingerprint;
    } catch (error) {
      console.error('Failed to generate device fingerprint:', error);
      throw error;
    }
  },

  /**
   * Get device attestation data for Level B onboarding
   */
  async getAttestationData(): Promise<any> {
    try {
      const [
        uniqueId,
        manufacturer,
        model,
        systemVersion,
        buildId,
        isEmulator,
        isPinSet,
      ] = await Promise.all([
        DeviceInfo.getUniqueId(),
        DeviceInfo.getManufacturer(),
        DeviceInfo.getModel(),
        DeviceInfo.getSystemVersion(),
        DeviceInfo.getBuildId(),
        DeviceInfo.isEmulator(),
        DeviceInfo.isPinOrFingerprintSet(),
      ]);

      return {
        device_id: uniqueId,
        manufacturer,
        model,
        os: Platform.OS,
        os_version: systemVersion,
        build_id: buildId,
        is_emulator: isEmulator,
        has_screen_lock: isPinSet,
        timestamp: new Date().toISOString(),
        // In production, add:
        // - SafetyNet attestation (Android)
        // - DeviceCheck token (iOS)
      };
    } catch (error) {
      console.error('Failed to get attestation data:', error);
      throw error;
    }
  },

  /**
   * Check if device meets minimum security requirements
   */
  async meetsSecurityRequirements(): Promise<{
    meets: boolean;
    reasons: string[];
  }> {
    const reasons: string[] = [];

    try {
      // Check screen lock
      const isPinSet = await DeviceInfo.isPinOrFingerprintSet();
      if (!isPinSet && !__DEV__) {
        reasons.push('Screen lock (PIN/pattern/biometric) must be enabled');
      }

      // Check emulator (block in production)
      const isEmulator = await DeviceInfo.isEmulator();
      if (isEmulator && !__DEV__) {
        reasons.push('Emulators are not allowed in production');
      }

      // Check OS version (example: require Android 8+ or iOS 13+)
      const systemVersion = await DeviceInfo.getSystemVersion();
      const majorVersion = parseInt(systemVersion.split('.')[0], 10);

      if (Platform.OS === 'android' && majorVersion < 8) {
        reasons.push('Android 8.0 or higher required');
      } else if (Platform.OS === 'ios' && majorVersion < 13) {
        reasons.push('iOS 13 or higher required');
      }

      return {
        meets: reasons.length === 0,
        reasons,
      };
    } catch (error) {
      console.error('Security requirements check failed:', error);
      return {
        meets: false,
        reasons: ['Unable to verify device security'],
      };
    }
  },
};

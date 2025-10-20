import * as LocalAuthentication from 'expo-local-authentication';
import { Platform } from 'react-native';

export interface BiometricCapability {
  isAvailable: boolean;
  biometricType: string;
  isEnrolled: boolean;
}

export const biometricAuth = {
  /**
   * Check if biometric authentication is available on the device
   */
  async checkCapability(): Promise<BiometricCapability> {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      const supportedTypes =
        await LocalAuthentication.supportedAuthenticationTypesAsync();

      let biometricType = 'None';
      if (supportedTypes.length > 0) {
        // Map Expo types to readable strings
        if (
          supportedTypes.includes(
            LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION
          )
        ) {
          biometricType = Platform.OS === 'ios' ? 'Face ID' : 'Face Recognition';
        } else if (
          supportedTypes.includes(
            LocalAuthentication.AuthenticationType.FINGERPRINT
          )
        ) {
          biometricType =
            Platform.OS === 'ios' ? 'Touch ID' : 'Fingerprint';
        } else if (
          supportedTypes.includes(
            LocalAuthentication.AuthenticationType.IRIS
          )
        ) {
          biometricType = 'Iris Recognition';
        }
      }

      return {
        isAvailable: hasHardware && isEnrolled,
        biometricType,
        isEnrolled,
      };
    } catch (error) {
      console.error('Failed to check biometric capability:', error);
      return {
        isAvailable: false,
        biometricType: 'None',
        isEnrolled: false,
      };
    }
  },

  /**
   * Authenticate user with biometrics
   */
  async authenticate(
    promptMessage: string = 'Authentifiez-vous pour continuer'
  ): Promise<{ success: boolean; error?: string }> {
    try {
      const capability = await this.checkCapability();

      if (!capability.isAvailable) {
        return {
          success: false,
          error: 'Authentification biométrique non disponible',
        };
      }

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage,
        fallbackLabel: 'Utiliser le code',
        cancelLabel: 'Annuler',
        disableDeviceFallback: false, // Allow PIN/pattern fallback
      });

      if (result.success) {
        return { success: true };
      } else {
        return {
          success: false,
          error: result.error || 'Authentification échouée',
        };
      }
    } catch (error: any) {
      console.error('Biometric authentication error:', error);
      return {
        success: false,
        error: error.message || 'Erreur d\'authentification',
      };
    }
  },

  /**
   * Authenticate for sensitive operations (e.g., generating QR code)
   */
  async authenticateForQRGeneration(): Promise<boolean> {
    const result = await this.authenticate(
      'Authentifiez-vous pour générer un QR code'
    );
    return result.success;
  },

  /**
   * Authenticate for device registration
   */
  async authenticateForDeviceRegistration(): Promise<boolean> {
    const result = await this.authenticate(
      'Authentifiez-vous pour enregistrer cet appareil'
    );
    return result.success;
  },

  /**
   * Optional: Authenticate on app launch
   */
  async authenticateOnLaunch(): Promise<boolean> {
    const capability = await this.checkCapability();

    // Only require biometric on launch if it's available
    if (!capability.isAvailable) {
      return true; // Skip if not available
    }

    const result = await this.authenticate('Déverrouillez Chrona');
    return result.success;
  },
};

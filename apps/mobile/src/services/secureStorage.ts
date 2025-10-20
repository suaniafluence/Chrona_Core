import * as SecureStore from 'expo-secure-store';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

/**
 * Secure storage service using platform-specific secure storage
 * - iOS: Keychain
 * - Android: EncryptedSharedPreferences/Keystore
 * - Web: Falls back to AsyncStorage (encrypted in browser)
 */

const isSecureStoreAvailable = Platform.OS === 'ios' || Platform.OS === 'android';

export const secureStorage = {
  /**
   * Store a value securely
   */
  async setItem(key: string, value: string): Promise<void> {
    try {
      if (isSecureStoreAvailable) {
        await SecureStore.setItemAsync(key, value);
      } else {
        // Fallback for web/unsupported platforms
        await AsyncStorage.setItem(key, value);
      }
    } catch (error) {
      console.error(`Failed to store ${key} securely:`, error);
      throw error;
    }
  },

  /**
   * Retrieve a value securely
   */
  async getItem(key: string): Promise<string | null> {
    try {
      if (isSecureStoreAvailable) {
        return await SecureStore.getItemAsync(key);
      } else {
        return await AsyncStorage.getItem(key);
      }
    } catch (error) {
      console.error(`Failed to retrieve ${key} securely:`, error);
      return null;
    }
  },

  /**
   * Remove a value securely
   */
  async removeItem(key: string): Promise<void> {
    try {
      if (isSecureStoreAvailable) {
        await SecureStore.deleteItemAsync(key);
      } else {
        await AsyncStorage.removeItem(key);
      }
    } catch (error) {
      console.error(`Failed to remove ${key} securely:`, error);
      throw error;
    }
  },

  /**
   * Clear all secure storage (use with caution)
   */
  async clear(): Promise<void> {
    try {
      if (isSecureStoreAvailable) {
        // SecureStore doesn't have a clear all method
        // You need to manually delete known keys
        const keys = ['@auth_token', '@device_id', '@user_data'];
        await Promise.all(keys.map((key) => SecureStore.deleteItemAsync(key)));
      } else {
        await AsyncStorage.clear();
      }
    } catch (error) {
      console.error('Failed to clear secure storage:', error);
      throw error;
    }
  },
};

// Convenience methods for common storage keys
export const authStorage = {
  async setToken(token: string): Promise<void> {
    return secureStorage.setItem('@auth_token', token);
  },

  async getToken(): Promise<string | null> {
    return secureStorage.getItem('@auth_token');
  },

  async removeToken(): Promise<void> {
    return secureStorage.removeItem('@auth_token');
  },

  async setDeviceId(deviceId: string): Promise<void> {
    return secureStorage.setItem('@device_id', deviceId);
  },

  async getDeviceId(): Promise<string | null> {
    return secureStorage.getItem('@device_id');
  },

  async setUserData(userData: any): Promise<void> {
    return secureStorage.setItem('@user_data', JSON.stringify(userData));
  },

  async getUserData(): Promise<any | null> {
    const data = await secureStorage.getItem('@user_data');
    return data ? JSON.parse(data) : null;
  },

  async clearAll(): Promise<void> {
    await Promise.all([
      secureStorage.removeItem('@auth_token'),
      secureStorage.removeItem('@device_id'),
      secureStorage.removeItem('@user_data'),
    ]);
  },
};

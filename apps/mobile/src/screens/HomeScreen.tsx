import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Device from 'expo-device';
import { deviceService } from '../services/api';

export default function HomeScreen({ navigation }: any) {
  const [device, setDevice] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDevice();
  }, []);

  const loadDevice = async () => {
    try {
      const devices = await deviceService.getMyDevices();
      if (devices.length > 0) {
        setDevice(devices[0]);
      }
    } catch (error) {
      console.error('Failed to load device:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateQR = () => {
    if (!device) {
      Alert.alert(
        'Aucun appareil',
        'Vous devez d\'abord enregistrer cet appareil',
        [
          {
            text: 'Enregistrer',
            onPress: registerDevice,
          },
          { text: 'Annuler' },
        ]
      );
      return;
    }

    navigation.navigate('QRCode', { deviceId: device.id });
  };

  const registerDevice = async () => {
    try {
      setIsLoading(true);
      const fingerprint = `${Device.modelName}-${Device.osName}-${Date.now()}`;
      const deviceName = `${Device.modelName} (${Device.osName})`;

      const newDevice = await deviceService.registerDevice({
        device_fingerprint: fingerprint,
        device_name: deviceName,
      });

      setDevice(newDevice);
      Alert.alert('Succès', 'Appareil enregistré avec succès');
    } catch (error: any) {
      console.error('Device registration error:', error);
      Alert.alert(
        'Erreur',
        error.response?.data?.detail || 'Impossible d\'enregistrer l\'appareil'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      'Déconnexion',
      'Êtes-vous sûr de vouloir vous déconnecter ?',
      [
        {
          text: 'Annuler',
          style: 'cancel',
        },
        {
          text: 'Déconnexion',
          style: 'destructive',
          onPress: async () => {
            await AsyncStorage.removeItem('@auth_token');
            navigation.replace('Login');
          },
        },
      ]
    );
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#667eea" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.welcome}>Bienvenue !</Text>

        {device && (
          <View style={styles.deviceInfo}>
            <Text style={styles.deviceLabel}>Appareil enregistré:</Text>
            <Text style={styles.deviceName}>{device.device_name}</Text>
          </View>
        )}

        <TouchableOpacity
          style={styles.primaryButton}
          onPress={handleGenerateQR}
        >
          <Text style={styles.primaryButtonText}>
            📱 Générer QR Code
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.secondaryButton}
          onPress={() => navigation.navigate('History')}
        >
          <Text style={styles.secondaryButtonText}>
            📋 Historique
          </Text>
        </TouchableOpacity>

        {!device && (
          <TouchableOpacity
            style={styles.registerButton}
            onPress={registerDevice}
          >
            <Text style={styles.registerButtonText}>
              ✓ Enregistrer cet appareil
            </Text>
          </TouchableOpacity>
        )}
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>Déconnexion</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  welcome: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 32,
    textAlign: 'center',
  },
  deviceInfo: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  deviceLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  deviceName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  primaryButton: {
    backgroundColor: '#667eea',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    marginBottom: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '600',
  },
  secondaryButton: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#667eea',
  },
  secondaryButtonText: {
    color: '#667eea',
    fontSize: 18,
    fontWeight: '600',
  },
  registerButton: {
    backgroundColor: '#4CAF50',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 16,
  },
  registerButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  logoutButton: {
    padding: 20,
    alignItems: 'center',
  },
  logoutText: {
    color: '#f44336',
    fontSize: 16,
    fontWeight: '600',
  },
});

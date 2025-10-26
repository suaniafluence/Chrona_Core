import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { CameraView, useCameraPermissions, BarcodeScanningResult } from 'expo-camera';
import { KioskConfig } from '../services/api';

interface ConfigQRScannerProps {
  onConfigured: () => void;
  onCancel: () => void;
}

interface KioskConfigData {
  apiBaseUrl: string;
  kioskId: number;
  kioskApiKey: string;
  kioskName?: string;
  location?: string;
  punchType?: 'clock_in' | 'clock_out';
}

export default function ConfigQRScanner({ onConfigured, onCancel }: ConfigQRScannerProps) {
  const [permission, requestPermission] = useCameraPermissions();
  const [isProcessing, setIsProcessing] = useState(false);
  const config = KioskConfig.getInstance();

  const validateConfigData = (data: any): data is KioskConfigData => {
    if (!data || typeof data !== 'object') {
      return false;
    }

    // Required fields
    if (!data.apiBaseUrl || typeof data.apiBaseUrl !== 'string') {
      return false;
    }

    if (!data.kioskId || typeof data.kioskId !== 'number') {
      return false;
    }

    if (!data.kioskApiKey || typeof data.kioskApiKey !== 'string') {
      return false;
    }

    // Optional fields validation
    if (data.punchType && !['clock_in', 'clock_out'].includes(data.punchType)) {
      return false;
    }

    return true;
  };

  const handleBarCodeScanned = async ({ data }: BarcodeScanningResult) => {
    if (isProcessing) {
      return;
    }

    setIsProcessing(true);

    try {
      console.log('QR Code scanned:', data);

      // Parse JSON data
      let configData: any;
      try {
        configData = JSON.parse(data);
      } catch (error) {
        Alert.alert(
          'Erreur',
          'QR code invalide. Le format doit être JSON.',
          [{ text: 'OK', onPress: () => setIsProcessing(false) }]
        );
        return;
      }

      // Validate config data
      if (!validateConfigData(configData)) {
        Alert.alert(
          'Erreur',
          'Configuration invalide. Vérifiez que le QR code contient tous les champs requis.',
          [{ text: 'OK', onPress: () => setIsProcessing(false) }]
        );
        return;
      }

      // Show confirmation with config details
      Alert.alert(
        'Configuration détectée',
        `Nom: ${configData.kioskName || 'Non spécifié'}\nID: ${configData.kioskId}\nServeur: ${configData.apiBaseUrl}\n\nVoulez-vous appliquer cette configuration ?`,
        [
          {
            text: 'Annuler',
            style: 'cancel',
            onPress: () => setIsProcessing(false),
          },
          {
            text: 'Appliquer',
            onPress: async () => {
              try {
                // Save configuration
                await config.saveConfig({
                  apiBaseUrl: configData.apiBaseUrl,
                  kioskId: configData.kioskId,
                  kioskApiKey: configData.kioskApiKey,
                  punchType: configData.punchType || 'clock_in',
                });

                Alert.alert(
                  'Succès',
                  'Configuration enregistrée avec succès !',
                  [{ text: 'OK', onPress: onConfigured }]
                );
              } catch (error) {
                console.error('Failed to save config:', error);
                Alert.alert(
                  'Erreur',
                  "Impossible d'enregistrer la configuration",
                  [{ text: 'OK', onPress: () => setIsProcessing(false) }]
                );
              }
            },
          },
        ]
      );
    } catch (error) {
      console.error('Error processing QR code:', error);
      Alert.alert(
        'Erreur',
        'Erreur lors du traitement du QR code',
        [{ text: 'OK', onPress: () => setIsProcessing(false) }]
      );
    }
  };

  if (!permission) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>Chargement de la caméra...</Text>
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Accès à la caméra requis</Text>
        <TouchableOpacity style={styles.button} onPress={requestPermission}>
          <Text style={styles.buttonText}>Autoriser la caméra</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.button, styles.cancelButton]} onPress={onCancel}>
          <Text style={styles.buttonText}>Annuler</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <CameraView
        style={styles.camera}
        facing="back"
        onBarcodeScanned={!isProcessing ? handleBarCodeScanned : undefined}
        barcodeScannerSettings={{
          barcodeTypes: ['qr'],
        }}
      >
        <View style={styles.overlay}>
          <Text style={styles.title}>Scanner le QR de configuration</Text>

          <View style={styles.scanFrame}>
            <View style={[styles.corner, styles.topLeft]} />
            <View style={[styles.corner, styles.topRight]} />
            <View style={[styles.corner, styles.bottomLeft]} />
            <View style={[styles.corner, styles.bottomRight]} />
          </View>

          <View style={styles.instructions}>
            <Text style={styles.instructionText}>
              Scannez le QR code généré depuis le back-office
            </Text>
            <Text style={styles.instructionSubtext}>
              Contient: API URL, Kiosk ID, Clé API
            </Text>
          </View>

          <TouchableOpacity style={styles.cancelButtonBottom} onPress={onCancel}>
            <Text style={styles.cancelButtonText}>Annuler</Text>
          </TouchableOpacity>
        </View>
      </CameraView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
  },
  camera: {
    flex: 1,
    width: '100%',
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 40,
    textAlign: 'center',
  },
  scanFrame: {
    width: 300,
    height: 300,
    position: 'relative',
    marginBottom: 40,
  },
  corner: {
    position: 'absolute',
    width: 50,
    height: 50,
    borderColor: '#1a73e8',
    borderWidth: 5,
  },
  topLeft: {
    top: 0,
    left: 0,
    borderBottomWidth: 0,
    borderRightWidth: 0,
  },
  topRight: {
    top: 0,
    right: 0,
    borderBottomWidth: 0,
    borderLeftWidth: 0,
  },
  bottomLeft: {
    bottom: 0,
    left: 0,
    borderTopWidth: 0,
    borderRightWidth: 0,
  },
  bottomRight: {
    bottom: 0,
    right: 0,
    borderTopWidth: 0,
    borderLeftWidth: 0,
  },
  instructions: {
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
  },
  instructionText: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 8,
  },
  instructionSubtext: {
    color: '#aaa',
    fontSize: 14,
    textAlign: 'center',
  },
  cancelButtonBottom: {
    backgroundColor: 'rgba(244, 67, 54, 0.9)',
    paddingVertical: 14,
    paddingHorizontal: 40,
    borderRadius: 8,
  },
  cancelButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  message: {
    color: '#fff',
    fontSize: 16,
  },
  errorText: {
    color: '#f44336',
    fontSize: 18,
    marginBottom: 20,
    textAlign: 'center',
  },
  button: {
    backgroundColor: '#1a73e8',
    paddingVertical: 14,
    paddingHorizontal: 40,
    borderRadius: 8,
    marginBottom: 12,
  },
  cancelButton: {
    backgroundColor: '#666',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

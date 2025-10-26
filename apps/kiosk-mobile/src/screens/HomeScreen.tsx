import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Modal } from 'react-native';
import QRScanner from '../components/QRScanner';
import ValidationResult from '../components/ValidationResult';
import ConnectionStatus from '../components/ConnectionStatus';
import SettingsScreen from './SettingsScreen';
import { PunchValidateResponse } from '../services/api';

export default function HomeScreen() {
  const [result, setResult] = useState<PunchValidateResponse | null>(null);
  const [isScanning, setIsScanning] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  const handleScanSuccess = (validationResult: PunchValidateResponse) => {
    setResult(validationResult);
    setIsScanning(false);

    // Reset after 3 seconds
    setTimeout(() => {
      setResult(null);
      setIsScanning(true);
    }, 3000);
  };

  const handleScanError = (error: string) => {
    setResult({
      success: false,
      message: error,
    });
    setIsScanning(false);

    // Reset after 3 seconds
    setTimeout(() => {
      setResult(null);
      setIsScanning(true);
    }, 3000);
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Chrona Kiosk</Text>
          <Text style={styles.subtitle}>Scanner le QR code pour pointer</Text>
        </View>
        <View style={styles.headerRight}>
          <ConnectionStatus />
          <TouchableOpacity
            style={styles.settingsButton}
            onPress={() => setShowSettings(true)}
          >
            <Text style={styles.settingsIcon}>⚙️</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Main Content */}
      <View style={styles.content}>
        {isScanning ? (
          <QRScanner onScanSuccess={handleScanSuccess} onScanError={handleScanError} />
        ) : (
          <ValidationResult result={result} />
        )}
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          © 2025 Chrona - Système de pointage sécurisé
        </Text>
      </View>

      {/* Settings Modal */}
      <Modal
        visible={showSettings}
        animationType="slide"
        presentationStyle="fullScreen"
      >
        <SettingsScreen onClose={() => setShowSettings(false)} />
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#1a73e8',
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  subtitle: {
    fontSize: 14,
    color: '#e3f2fd',
    marginTop: 4,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  settingsButton: {
    padding: 8,
  },
  settingsIcon: {
    fontSize: 24,
  },
  content: {
    flex: 1,
  },
  footer: {
    backgroundColor: '#333',
    paddingVertical: 12,
    alignItems: 'center',
  },
  footerText: {
    color: '#fff',
    fontSize: 12,
  },
});

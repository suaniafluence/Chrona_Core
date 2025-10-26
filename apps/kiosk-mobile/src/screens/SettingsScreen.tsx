import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Modal,
} from 'react-native';
import { KioskConfig } from '../services/api';
import ConfigQRScanner from '../components/ConfigQRScanner';

interface SettingsScreenProps {
  onClose: () => void;
}

export default function SettingsScreen({ onClose }: SettingsScreenProps) {
  const config = KioskConfig.getInstance();
  const [apiBaseUrl, setApiBaseUrl] = useState('');
  const [kioskId, setKioskId] = useState('');
  const [kioskApiKey, setKioskApiKey] = useState('');
  const [punchType, setPunchType] = useState<'clock_in' | 'clock_out'>('clock_in');
  const [showQRScanner, setShowQRScanner] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    await config.loadConfig();
    const currentConfig = config.getConfig();
    setApiBaseUrl(currentConfig.apiBaseUrl);
    setKioskId(currentConfig.kioskId.toString());
    setKioskApiKey(currentConfig.kioskApiKey);
    setPunchType(currentConfig.punchType);
  };

  const handleSave = async () => {
    try {
      // Validate inputs
      if (!apiBaseUrl) {
        Alert.alert('Erreur', 'L\'URL de l\'API est requise');
        return;
      }

      if (!kioskId || isNaN(parseInt(kioskId, 10))) {
        Alert.alert('Erreur', 'L\'ID du kiosk doit être un nombre');
        return;
      }

      // Save configuration
      await config.saveConfig({
        apiBaseUrl: apiBaseUrl.trim(),
        kioskId: parseInt(kioskId, 10),
        kioskApiKey: kioskApiKey.trim(),
        punchType,
      });

      Alert.alert('Succès', 'Configuration enregistrée', [
        { text: 'OK', onPress: onClose },
      ]);
    } catch (error) {
      console.error('Failed to save settings:', error);
      Alert.alert('Erreur', 'Impossible d\'enregistrer la configuration');
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Configuration Kiosk</Text>
        <TouchableOpacity onPress={onClose} style={styles.closeButton}>
          <Text style={styles.closeButtonText}>✕</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {/* QR Code Configuration Button */}
        <TouchableOpacity
          style={styles.qrButton}
          onPress={() => setShowQRScanner(true)}
        >
          <Text style={styles.qrButtonIcon}>📷</Text>
          <View style={styles.qrButtonContent}>
            <Text style={styles.qrButtonText}>Scanner un QR de configuration</Text>
            <Text style={styles.qrButtonSubtext}>
              Configuration automatique depuis le back-office
            </Text>
          </View>
        </TouchableOpacity>

        <View style={styles.divider}>
          <View style={styles.dividerLine} />
          <Text style={styles.dividerText}>ou configurer manuellement</Text>
          <View style={styles.dividerLine} />
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>URL de l'API Backend</Text>
          <TextInput
            style={styles.input}
            value={apiBaseUrl}
            onChangeText={setApiBaseUrl}
            placeholder="http://192.168.1.100:8000"
            placeholderTextColor="#999"
            autoCapitalize="none"
            autoCorrect={false}
          />
          <Text style={styles.helpText}>
            Format: http://[IP]:[PORT] (exemple: http://192.168.1.100:8000)
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>ID du Kiosk</Text>
          <TextInput
            style={styles.input}
            value={kioskId}
            onChangeText={setKioskId}
            placeholder="1"
            placeholderTextColor="#999"
            keyboardType="numeric"
          />
          <Text style={styles.helpText}>
            Identifiant unique du kiosk (numéro)
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>Clé API Kiosk</Text>
          <TextInput
            style={styles.input}
            value={kioskApiKey}
            onChangeText={setKioskApiKey}
            placeholder="votre-cle-api"
            placeholderTextColor="#999"
            secureTextEntry
            autoCapitalize="none"
            autoCorrect={false}
          />
          <Text style={styles.helpText}>
            Clé d'authentification pour le kiosk
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>Type de pointage</Text>
          <View style={styles.toggleContainer}>
            <TouchableOpacity
              style={[
                styles.toggleButton,
                punchType === 'clock_in' && styles.toggleButtonActive,
              ]}
              onPress={() => setPunchType('clock_in')}
            >
              <Text
                style={[
                  styles.toggleButtonText,
                  punchType === 'clock_in' && styles.toggleButtonTextActive,
                ]}
              >
                Entrée
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.toggleButton,
                punchType === 'clock_out' && styles.toggleButtonActive,
              ]}
              onPress={() => setPunchType('clock_out')}
            >
              <Text
                style={[
                  styles.toggleButtonText,
                  punchType === 'clock_out' && styles.toggleButtonTextActive,
                ]}
              >
                Sortie
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
          <Text style={styles.saveButtonText}>Enregistrer</Text>
        </TouchableOpacity>
      </ScrollView>

      {/* QR Scanner Modal */}
      <Modal
        visible={showQRScanner}
        animationType="slide"
        presentationStyle="fullScreen"
      >
        <ConfigQRScanner
          onConfigured={() => {
            setShowQRScanner(false);
            loadSettings(); // Reload settings after QR config
          }}
          onCancel={() => setShowQRScanner(false)}
        />
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 20,
    backgroundColor: '#1a73e8',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  closeButton: {
    padding: 8,
  },
  closeButtonText: {
    fontSize: 24,
    color: '#fff',
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  section: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
    color: '#333',
  },
  helpText: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  toggleContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  toggleButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
    alignItems: 'center',
    backgroundColor: '#f9f9f9',
  },
  toggleButtonActive: {
    backgroundColor: '#1a73e8',
    borderColor: '#1a73e8',
  },
  toggleButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
  },
  toggleButtonTextActive: {
    color: '#fff',
  },
  saveButton: {
    backgroundColor: '#4caf50',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 40,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  qrButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1a73e8',
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  qrButtonIcon: {
    fontSize: 32,
    marginRight: 16,
  },
  qrButtonContent: {
    flex: 1,
  },
  qrButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  qrButtonSubtext: {
    color: '#e3f2fd',
    fontSize: 13,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 24,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#ddd',
  },
  dividerText: {
    color: '#666',
    fontSize: 14,
    marginHorizontal: 12,
    fontWeight: '500',
  },
});

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  Alert,
  TouchableOpacity,
} from 'react-native';
import QRCode from 'react-native-qrcode-svg';
import { punchService } from '../services/api';

export default function QRCodeScreen({ route }: any) {
  const { deviceId } = route.params;
  const [qrToken, setQrToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [timeLeft, setTimeLeft] = useState(30);
  const [expiresAt, setExpiresAt] = useState<Date | null>(null);

  useEffect(() => {
    generateToken();
  }, []);

  useEffect(() => {
    if (!expiresAt) return;

    const interval = setInterval(() => {
      const now = new Date();
      const diff = Math.floor((expiresAt.getTime() - now.getTime()) / 1000);

      if (diff <= 0) {
        // Token expired, regenerate
        generateToken();
      } else {
        setTimeLeft(diff);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [expiresAt]);

  const generateToken = async () => {
    try {
      setIsLoading(true);
      const response = await punchService.requestQRToken(deviceId);
      setQrToken(response.qr_token);
      setExpiresAt(new Date(response.expires_at));
      setTimeLeft(response.expires_in);
    } catch (error: any) {
      console.error('Failed to generate QR token:', error);
      Alert.alert(
        'Erreur',
        error.response?.data?.detail || 'Impossible de générer le QR code'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const getTimeLeftColor = () => {
    if (timeLeft > 20) return '#4CAF50'; // Green
    if (timeLeft > 10) return '#FF9800'; // Orange
    return '#f44336'; // Red
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#667eea" />
        <Text style={styles.loadingText}>Génération du QR Code...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Présentez ce QR Code</Text>
        <Text style={styles.subtitle}>à la borne de pointage</Text>

        {qrToken && (
          <View style={styles.qrContainer}>
            <QRCode
              value={qrToken}
              size={280}
              backgroundColor="white"
              color="black"
            />
          </View>
        )}

        <View style={styles.timerContainer}>
          <Text style={styles.timerLabel}>Temps restant</Text>
          <Text style={[styles.timerValue, { color: getTimeLeftColor() }]}>
            {timeLeft}s
          </Text>
        </View>

        <View style={styles.infoBox}>
          <Text style={styles.infoText}>
            ⚠️ Ce QR Code est éphémère et expire dans {timeLeft} secondes
          </Text>
          <Text style={styles.infoText}>
            🔒 Il ne peut être utilisé qu'une seule fois
          </Text>
        </View>

        <TouchableOpacity
          style={styles.refreshButton}
          onPress={generateToken}
        >
          <Text style={styles.refreshButtonText}>🔄 Générer un nouveau code</Text>
        </TouchableOpacity>
      </View>
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
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  content: {
    flex: 1,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 32,
    textAlign: 'center',
  },
  qrContainer: {
    backgroundColor: '#fff',
    padding: 24,
    borderRadius: 16,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    marginBottom: 24,
  },
  timerContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  timerLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  timerValue: {
    fontSize: 48,
    fontWeight: 'bold',
  },
  infoBox: {
    backgroundColor: '#fff3cd',
    borderRadius: 8,
    padding: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#ffc107',
  },
  infoText: {
    fontSize: 14,
    color: '#856404',
    marginBottom: 8,
    textAlign: 'center',
  },
  refreshButton: {
    backgroundColor: '#667eea',
    borderRadius: 8,
    padding: 16,
    paddingHorizontal: 32,
  },
  refreshButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

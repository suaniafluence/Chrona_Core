import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { deviceSecurity } from '../services/deviceSecurity';

interface SecurityCheckProps {
  onComplete: (isSecure: boolean) => void;
}

/**
 * Component that performs device security checks on mount
 * Blocks app usage if critical security threats are detected
 */
export default function SecurityCheck({ onComplete }: SecurityCheckProps) {
  const [isChecking, setIsChecking] = useState(true);
  const [status, setStatus] = useState('Vérification de la sécurité de l\'appareil...');

  useEffect(() => {
    performSecurityChecks();
  }, []);

  const performSecurityChecks = async () => {
    try {
      setStatus('Vérification de l\'intégrité de l\'appareil...');

      // Check device integrity
      const integrityResult = await deviceSecurity.checkDeviceIntegrity();

      // Check security requirements
      setStatus('Vérification des exigences de sécurité...');
      const requirementsResult = await deviceSecurity.meetsSecurityRequirements();

      // Determine if device is secure enough
      const isSecure = integrityResult.isSecure && requirementsResult.meets;

      // Show warnings if any
      const allWarnings = [
        ...integrityResult.warnings,
        ...integrityResult.threats,
        ...requirementsResult.reasons,
      ];

      if (allWarnings.length > 0) {
        const warningMessage = allWarnings.join('\n• ');

        if (!isSecure) {
          // Critical threats - block app
          Alert.alert(
            'Appareil non sécurisé',
            `Votre appareil ne répond pas aux exigences de sécurité:\n\n• ${warningMessage}\n\nL'application ne peut pas être utilisée.`,
            [{ text: 'OK', onPress: () => onComplete(false) }]
          );
        } else {
          // Only warnings - allow but inform
          Alert.alert(
            'Avertissements de sécurité',
            `Quelques avertissements ont été détectés:\n\n• ${warningMessage}\n\nVous pouvez continuer mais la sécurité peut être compromise.`,
            [{ text: 'Continuer', onPress: () => onComplete(true) }]
          );
        }
      } else {
        // All clear
        onComplete(true);
      }
    } catch (error) {
      console.error('Security check failed:', error);
      Alert.alert(
        'Erreur',
        'Impossible de vérifier la sécurité de l\'appareil',
        [{ text: 'OK', onPress: () => onComplete(false) }]
      );
    } finally {
      setIsChecking(false);
    }
  };

  if (!isChecking) {
    return null;
  }

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#667eea" />
      <Text style={styles.text}>{status}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  text: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
});

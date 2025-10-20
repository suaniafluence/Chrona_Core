import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Device from 'expo-device';
import { onboardingService } from '../../services/api';

export default function CompleteOnboardingScreen({ route, navigation }: any) {
  const { sessionToken, email } = route.params;
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const generateDeviceFingerprint = async (): Promise<string> => {
    // Generate a unique device fingerprint
    // In production, use a more sophisticated method with SafetyNet/DeviceCheck
    const deviceId = await Device.getDeviceId();
    const deviceName = await Device.getDeviceName();
    const modelName = Device.modelName || 'unknown';
    const osVersion = Device.osVersion || 'unknown';

    const fingerprint = `${deviceId}-${modelName}-${osVersion}`;
    return fingerprint;
  };

  const getDeviceName = async (): Promise<string> => {
    const deviceName = await Device.getDeviceName();
    const modelName = Device.modelName;
    return deviceName || modelName || 'Mon appareil';
  };

  const performDeviceAttestation = async (): Promise<string | undefined> => {
    // Placeholder for device attestation
    // TODO: Implement SafetyNet (Android) or DeviceCheck (iOS) attestation
    try {
      if (Platform.OS === 'android') {
        // SafetyNet attestation for Android
        // const attestation = await SafetyNet.attest(...);
        // return attestation;
      } else if (Platform.OS === 'ios') {
        // DeviceCheck attestation for iOS
        // const attestation = await DeviceCheck.attest(...);
        // return attestation;
      }
      return undefined;
    } catch (error) {
      console.error('Device attestation error:', error);
      return undefined;
    }
  };

  const handleCompleteOnboarding = async () => {
    if (!password || !confirmPassword) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs');
      return;
    }

    if (password.length < 8) {
      Alert.alert('Erreur', 'Le mot de passe doit contenir au moins 8 caractères');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('Erreur', 'Les mots de passe ne correspondent pas');
      return;
    }

    setIsLoading(true);
    try {
      // Generate device fingerprint
      const deviceFingerprint = await generateDeviceFingerprint();
      const deviceName = await getDeviceName();

      // Perform device attestation
      const attestationData = await performDeviceAttestation();

      // Complete onboarding
      const response = await onboardingService.completeOnboarding({
        session_token: sessionToken,
        password,
        device_fingerprint: deviceFingerprint,
        device_name: deviceName,
        attestation_data: attestationData,
      });

      if (response.success && response.access_token) {
        // Store access token
        await AsyncStorage.setItem('@auth_token', response.access_token);

        Alert.alert(
          'Inscription réussie !',
          'Votre compte a été créé avec succès',
          [
            {
              text: 'OK',
              onPress: () => navigation.replace('Home'),
            },
          ]
        );
      } else {
        Alert.alert('Erreur', response.message || "Échec de l'inscription");
      }
    } catch (error: any) {
      console.error('Complete onboarding error:', error);
      Alert.alert(
        'Erreur',
        error.response?.data?.detail || "Échec de l'inscription"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.content}>
          <Text style={styles.title}>Finalisation</Text>
          <Text style={styles.subtitle}>Étape 3: Sécurisation</Text>

          <View style={styles.form}>
            <Text style={styles.description}>
              Créez un mot de passe sécurisé pour{'\n'}
              <Text style={styles.email}>{email}</Text>
            </Text>

            <Text style={styles.label}>Mot de passe (min. 8 caractères)</Text>
            <TextInput
              style={styles.input}
              placeholder="••••••••"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              editable={!isLoading}
            />

            <Text style={styles.label}>Confirmer le mot de passe</Text>
            <TextInput
              style={styles.input}
              placeholder="••••••••"
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              secureTextEntry
              editable={!isLoading}
            />

            <TouchableOpacity
              style={[styles.button, isLoading && styles.buttonDisabled]}
              onPress={handleCompleteOnboarding}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>Terminer l'inscription</Text>
              )}
            </TouchableOpacity>
          </View>

          <View style={styles.infoBox}>
            <Text style={styles.infoTitle}>Attestation de l'appareil</Text>
            <Text style={styles.infoText}>
              Cet appareil sera enregistré de manière sécurisée.{'\n'}
              L'attestation garantit l'intégrité de votre dispositif.
            </Text>
          </View>

          <View style={styles.securityBox}>
            <Text style={styles.securityTitle}>Recommandations :</Text>
            <Text style={styles.securityText}>
              • Utilisez au moins 12 caractères{'\n'}
              • Mélangez majuscules et minuscules{'\n'}
              • Ajoutez des chiffres et symboles{'\n'}
              • Évitez les mots du dictionnaire
            </Text>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContent: {
    flexGrow: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    minHeight: '100%',
  },
  title: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    color: '#666',
    marginBottom: 32,
  },
  form: {
    width: '100%',
    maxWidth: 400,
  },
  description: {
    fontSize: 14,
    color: '#555',
    marginBottom: 24,
    textAlign: 'center',
  },
  email: {
    fontWeight: '600',
    color: '#667eea',
  },
  label: {
    fontSize: 14,
    color: '#555',
    marginBottom: 8,
    fontWeight: '500',
  },
  input: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  button: {
    backgroundColor: '#667eea',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  infoBox: {
    marginTop: 24,
    padding: 16,
    backgroundColor: '#d1f2eb',
    borderRadius: 8,
    maxWidth: 400,
    width: '100%',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0f5132',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#555',
    lineHeight: 20,
  },
  securityBox: {
    marginTop: 16,
    padding: 16,
    backgroundColor: '#cfe2ff',
    borderRadius: 8,
    maxWidth: 400,
    width: '100%',
  },
  securityTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#084298',
    marginBottom: 8,
  },
  securityText: {
    fontSize: 13,
    color: '#555',
    lineHeight: 20,
  },
});

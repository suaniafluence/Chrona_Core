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
} from 'react-native';
import { onboardingService } from '../../services/api';

export default function HRCodeScreen({ navigation }: any) {
  const [hrCode, setHrCode] = useState('');
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    if (!hrCode || !email) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs');
      return;
    }

    setIsLoading(true);
    try {
      const response = await onboardingService.initiateOnboarding(
        hrCode.trim(),
        email.trim()
      );

      if (response.success && response.session_token) {
        Alert.alert(
          'Succès',
          'Un code OTP a été envoyé à votre adresse email',
          [
            {
              text: 'OK',
              onPress: () =>
                navigation.navigate('OTPVerification', {
                  sessionToken: response.session_token,
                  email: email.trim(),
                }),
            },
          ]
        );
      } else {
        Alert.alert('Erreur', response.message || 'Échec de la vérification');
      }
    } catch (error: any) {
      console.error('HR code validation error:', error);
      Alert.alert(
        'Erreur',
        error.response?.data?.detail || 'Code HR invalide'
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
      <View style={styles.content}>
        <Text style={styles.title}>Inscription</Text>
        <Text style={styles.subtitle}>Étape 1: Code RH</Text>

        <View style={styles.form}>
          <Text style={styles.label}>Code RH fourni par votre manager</Text>
          <TextInput
            style={styles.input}
            placeholder="Ex: EMPL-2025-A7K9X"
            value={hrCode}
            onChangeText={setHrCode}
            autoCapitalize="characters"
            editable={!isLoading}
          />

          <Text style={styles.label}>Adresse email professionnelle</Text>
          <TextInput
            style={styles.input}
            placeholder="votre.nom@entreprise.com"
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
            editable={!isLoading}
          />

          <TouchableOpacity
            style={[styles.button, isLoading && styles.buttonDisabled]}
            onPress={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Continuer</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.linkButton}
            onPress={() => navigation.navigate('Login')}
            disabled={isLoading}
          >
            <Text style={styles.linkText}>
              Vous avez déjà un compte ? Se connecter
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.infoBox}>
          <Text style={styles.infoTitle}>Niveau de sécurité B</Text>
          <Text style={styles.infoText}>
            • Vérification du code RH{'\n'}
            • Confirmation par OTP email{'\n'}
            • Attestation de l'appareil
          </Text>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
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
  linkButton: {
    marginTop: 16,
    alignItems: 'center',
  },
  linkText: {
    color: '#667eea',
    fontSize: 14,
  },
  infoBox: {
    marginTop: 32,
    padding: 16,
    backgroundColor: '#e8eaf6',
    borderRadius: 8,
    maxWidth: 400,
    width: '100%',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#3f51b5',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#555',
    lineHeight: 20,
  },
});

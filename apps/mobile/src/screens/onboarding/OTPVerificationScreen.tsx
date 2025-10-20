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

export default function OTPVerificationScreen({ route, navigation }: any) {
  const { sessionToken, email } = route.params;
  const [otpCode, setOtpCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleVerifyOTP = async () => {
    if (!otpCode || otpCode.length !== 6) {
      Alert.alert('Erreur', 'Veuillez entrer un code OTP valide (6 chiffres)');
      return;
    }

    setIsLoading(true);
    try {
      const response = await onboardingService.verifyOTP(
        sessionToken,
        otpCode.trim()
      );

      if (response.success) {
        Alert.alert('Succès', 'Code OTP vérifié', [
          {
            text: 'OK',
            onPress: () =>
              navigation.navigate('CompleteOnboarding', {
                sessionToken,
                email,
              }),
          },
        ]);
      } else {
        Alert.alert('Erreur', response.message || 'Code OTP invalide');
      }
    } catch (error: any) {
      console.error('OTP verification error:', error);
      Alert.alert(
        'Erreur',
        error.response?.data?.detail || 'Code OTP invalide'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendOTP = async () => {
    Alert.alert(
      'Renvoyer le code',
      'Souhaitez-vous renvoyer le code OTP?',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Renvoyer',
          onPress: () => {
            Alert.alert('Info', 'Fonctionnalité de renvoi à implémenter');
            // TODO: Implement resend OTP
          },
        },
      ]
    );
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.content}>
        <Text style={styles.title}>Vérification</Text>
        <Text style={styles.subtitle}>Étape 2: Code OTP</Text>

        <View style={styles.form}>
          <Text style={styles.description}>
            Un code de vérification a été envoyé à :{'\n'}
            <Text style={styles.email}>{email}</Text>
          </Text>

          <Text style={styles.label}>Code OTP (6 chiffres)</Text>
          <TextInput
            style={styles.input}
            placeholder="123456"
            value={otpCode}
            onChangeText={(text) => setOtpCode(text.replace(/[^0-9]/g, ''))}
            keyboardType="number-pad"
            maxLength={6}
            editable={!isLoading}
            autoFocus
          />

          <TouchableOpacity
            style={[styles.button, isLoading && styles.buttonDisabled]}
            onPress={handleVerifyOTP}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Vérifier</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.linkButton}
            onPress={handleResendOTP}
            disabled={isLoading}
          >
            <Text style={styles.linkText}>
              Vous n'avez pas reçu de code ? Renvoyer
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.infoBox}>
          <Text style={styles.infoTitle}>Code de vérification</Text>
          <Text style={styles.infoText}>
            Le code OTP expire après 10 minutes.{'\n'}
            Vérifiez vos spams si vous ne le trouvez pas.
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
    fontSize: 24,
    borderWidth: 1,
    borderColor: '#ddd',
    textAlign: 'center',
    letterSpacing: 8,
    fontWeight: '600',
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
    backgroundColor: '#fff3cd',
    borderRadius: 8,
    maxWidth: 400,
    width: '100%',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#856404',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#555',
    lineHeight: 20,
  },
});

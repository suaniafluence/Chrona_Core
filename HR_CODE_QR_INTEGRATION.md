# 📱 HR Code QR Integration Guide

## Overview

Integration of QR code scanning for HR code enrollment in the Chrona mobile app. This enables employees to scan a QR code (generated in the backoffice) instead of manually typing the HR code.

---

## Current Architecture

### Backend (✅ Ready)
- **HRCode API**: `/admin/hr-codes` - Create and list HR codes
- **Onboarding API**: `/onboarding/initiate` - Validates HR code and email
- **Format**: HR codes are plain text strings (e.g., `EMPL-2025-A7K9X`)

### Backoffice (✅ Complete)
- **Page**: `HRCodesPage.tsx` - Displays HR codes in a table
- **QR Generation**: `HRCodeQRDisplay.tsx` - Shows QR code modal
- **Features**:
  - Button "📱 QR" on each valid HR code
  - Modal displays QR code from HR code string
  - Download/Print functionality
  - Shows employee email and expiration

### Mobile App (⏳ To Implement)
- **Screen**: `HRCodeScreen.tsx` - Currently has manual entry only
- **Needs**: QR code scanner capability
- **Integration**: Auto-fill HR code from scanned QR

---

## Implementation Steps

### Step 1: Add QR Code Scanner Library

Add `expo-camera` and `react-native-vision-camera` to mobile dependencies:

```bash
cd apps/mobile
npx expo install expo-camera
npx expo install react-native-vision-camera react-native-worklets-core
npx expo install react-native-qrcode-scanner
```

Or use a simpler option (already compatible):
```bash
npx expo install expo-barcode-scanner
```

### Step 2: Create QR Scanner Component

Create `apps/mobile/src/components/QRCodeScanner.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Dimensions,
} from 'react-native';
import { BarCodeScanner } from 'expo-barcode-scanner';
import { Ionicons } from '@expo/vector-icons';

interface QRCodeScannerProps {
  onCodeScanned: (code: string) => void;
  onCancel: () => void;
}

export default function QRCodeScanner({
  onCodeScanned,
  onCancel,
}: QRCodeScannerProps) {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [scanned, setScanned] = useState(false);

  useEffect(() => {
    const getBarCodeScannerPermissions = async () => {
      const { status } = await BarCodeScanner.requestPermissionsAsync();
      setHasPermission(status === 'granted');
    };

    getBarCodeScannerPermissions();
  }, []);

  const handleBarCodeScanned = ({ type, data }: any) => {
    setScanned(true);

    // Validate that scanned data looks like an HR code
    // Format: EMPL-YYYY-XXXXX
    if (data.match(/^[A-Z]+-\d{4}-[A-Z0-9]{5}$/)) {
      onCodeScanned(data);
    } else {
      Alert.alert(
        'Code invalide',
        'Le code scanné ne semble pas être un code RH valide.\n\nFormat attendu: EMPL-2025-XXXXX',
        [
          {
            text: 'Réessayer',
            onPress: () => setScanned(false),
          },
        ]
      );
    }
  };

  if (hasPermission === null) {
    return (
      <View style={styles.container}>
        <Text>Permission d'accès à la caméra requise...</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.container}>
        <Text style={styles.text}>Accès à la caméra refusé</Text>
        <TouchableOpacity
          style={styles.button}
          onPress={onCancel}
        >
          <Text style={styles.buttonText}>Retour</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.scanner}>
      <BarCodeScanner
        onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
        style={StyleSheet.absoluteFillObject}
      />

      {/* Overlay */}
      <View style={styles.overlay}>
        <View style={styles.unfocused} />
        <View style={styles.focused}>
          <View style={styles.corner} />
          <View style={styles.corner} />
          <View style={styles.corner} />
          <View style={styles.corner} />
        </View>
        <View style={styles.unfocused} />
      </View>

      {/* Instructions */}
      <View style={styles.instructions}>
        <Text style={styles.instructionText}>
          📱 Pointez la caméra vers le code QR
        </Text>
      </View>

      {/* Cancel Button */}
      <TouchableOpacity
        style={styles.cancelButton}
        onPress={onCancel}
      >
        <Ionicons name="close" size={32} color="#fff" />
      </TouchableOpacity>

      {/* Rescanning */}
      {scanned && (
        <View style={styles.scanAgainContainer}>
          <TouchableOpacity
            style={styles.scanAgainButton}
            onPress={() => setScanned(false)}
          >
            <Text style={styles.scanAgainText}>Scanner à nouveau</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000',
  },
  scanner: {
    flex: 1,
    backgroundColor: '#000',
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  unfocused: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
  },
  focused: {
    width: 250,
    height: 250,
    position: 'relative',
    borderColor: '#00ff00',
  },
  corner: {
    position: 'absolute',
    width: 30,
    height: 30,
    borderColor: '#00ff00',
    borderWidth: 2,
  },
  instructions: {
    position: 'absolute',
    top: 50,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  instructionText: {
    fontSize: 16,
    color: '#fff',
    fontWeight: 'bold',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 8,
  },
  cancelButton: {
    position: 'absolute',
    bottom: 30,
    right: 20,
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(255, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scanAgainContainer: {
    position: 'absolute',
    bottom: 100,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  scanAgainButton: {
    backgroundColor: '#00ff00',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 10,
  },
  scanAgainText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#000',
  },
  text: {
    fontSize: 16,
    color: '#fff',
  },
  button: {
    marginTop: 20,
    paddingHorizontal: 30,
    paddingVertical: 12,
    backgroundColor: '#007AFF',
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
```

### Step 3: Update HRCodeScreen.tsx

Modify `apps/mobile/src/screens/onboarding/HRCodeScreen.tsx`:

```typescript
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
import QRCodeScanner from '../../components/QRCodeScanner';

export default function HRCodeScreen({ navigation }: any) {
  const [hrCode, setHrCode] = useState('');
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showScanner, setShowScanner] = useState(false);

  const handleQRCodeScanned = (scannedCode: string) => {
    // Auto-fill HR code from QR scan
    setHrCode(scannedCode);
    setShowScanner(false);
    Alert.alert(
      'Code scanné',
      `Code RH: ${scannedCode}\n\nVeuillez entrer votre email pour continuer.`
    );
  };

  const handleSubmit = async () => {
    if (!hrCode || !email) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs');
      return;
    }

    setIsLoading(true);
    try {
      const response = await onboardingService.initiateOnboarding(
        hrCode.trim().toUpperCase(),
        email.trim().toLowerCase()
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

  if (showScanner) {
    return (
      <QRCodeScanner
        onCodeScanned={handleQRCodeScanned}
        onCancel={() => setShowScanner(false)}
      />
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.content}>
        <Text style={styles.title}>Inscription</Text>
        <Text style={styles.subtitle}>Étape 1: Code RH</Text>

        <View style={styles.form}>
          {/* QR Scanner Button */}
          <TouchableOpacity
            style={styles.qrButton}
            onPress={() => setShowScanner(true)}
            disabled={isLoading}
          >
            <Text style={styles.qrButtonText}>📱 Scanner le code QR</Text>
          </TouchableOpacity>

          <Text style={styles.divider}>ou</Text>

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
    padding: 24,
    justifyContent: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 32,
  },
  form: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  qrButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 16,
  },
  qrButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  divider: {
    textAlign: 'center',
    color: '#999',
    marginVertical: 12,
    fontSize: 14,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
    marginTop: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 16,
    backgroundColor: '#fafafa',
  },
  button: {
    backgroundColor: '#34C759',
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
```

### Step 4: Request Camera Permissions

Update `apps/mobile/app.json` to include camera permissions:

```json
{
  "expo": {
    "plugins": [
      [
        "expo-camera",
        {
          "cameraPermission": "Chrona a besoin d'accès à votre caméra pour scanner le code QR d'onboarding"
        }
      ]
    ]
  }
}
```

---

## Testing Workflow

### End-to-End Test

1. **Backoffice**:
   - Navigate to "Codes RH" page
   - Click "Nouveau code RH"
   - Create: `jean.dupont@company.com`
   - Click "QR" button on the new code
   - Take screenshot or print the QR code

2. **Mobile App**:
   - Open app → Click "Nouvel employé"
   - Screen shows "Inscription - Étape 1: Code RH"
   - Click "📱 Scanner le code QR"
   - Point camera at printed/screened QR code
   - App scans and auto-fills: `EMPL-2025-XXXXX`
   - Enter email: `jean.dupont@company.com`
   - Click "Continuer"
   - Proceed to OTP verification

3. **Verification**:
   - OTP code should be sent to `jean.dupont@company.com`
   - Complete onboarding normally

---

## Code QR Format

The QR code contains **only the HR code string**:

```
EMPL-2025-A7K9X
```

**Not** a JWT or encoded payload. Just the plain text HR code.

### Validation Regex

Mobile app validates scanned codes:
```regex
^[A-Z]+-\d{4}-[A-Z0-9]{5}$
```

This ensures:
- Prefix: Uppercase letters (e.g., `EMPL`)
- Year: 4 digits
- Random part: 5 uppercase letters or digits

---

## Security Considerations

1. **QR Code Expiration**: HR code expiry is enforced at backend
2. **One-Time Use**: HR code cannot be reused after onboarding
3. **Email Validation**: Email must match the HR code's assigned email
4. **OTP Verification**: Additional security layer after HR code validation
5. **Device Attestation**: Required during onboarding completion

---

## Files Modified

### Backend (✅ No changes needed)
- Already supports HR codes in plain text format

### Backoffice (✅ Complete)
- `HRCodesPage.tsx` - Added QR generation button
- `HRCodeQRDisplay.tsx` - New component for QR display

### Mobile (⏳ To implement)
- `QRCodeScanner.tsx` - New component (barcode scanning)
- `HRCodeScreen.tsx` - Updated with QR button and scanner integration

---

## Dependencies to Add

```json
{
  "expo-barcode-scanner": "~14.1.1"
}
```

Or for more advanced use cases:
```json
{
  "expo-camera": "~15.0.8",
  "react-native-vision-camera": "^4.0.0"
}
```

---

## Troubleshooting

### QR Code Not Scanning
- Ensure good lighting
- QR code size should be at least 2x2 cm
- Camera lens should be focused at ~30cm distance

### Camera Permission Issues
- iOS: User must grant permission via system prompt
- Android: Check `app.json` plugin configuration
- Web: Camera not supported (use manual entry fallback)

### Invalid Format Error
- Ensure QR contains exactly: `EMPL-YYYY-XXXXX`
- Check that no extra characters or spaces are included

---

## Future Enhancements

1. **Biometric Auth**: Add Face ID/Touch ID before QR scan
2. **Barcode/EAN Support**: Accept other code formats
3. **Deep Linking**: Support `chrona://enrollment?code=...` URIs
4. **Offline Mode**: Cache valid codes for offline enrollment
5. **Multi-QR**: Support scanning multiple codes sequentially

---

## Support

For issues or questions, refer to:
- Backend: `backend/src/routers/onboarding.py`
- Backoffice: `apps/backoffice/src/pages/HRCodesPage.tsx`
- Mobile: `apps/mobile/src/screens/onboarding/HRCodeScreen.tsx`

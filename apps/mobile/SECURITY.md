# Mobile App Security Implementation

This document describes the security features implemented in the Chrona mobile application.

## 🔒 Security Features

### 1. Anti-Screenshot Protection

**Location**: `src/screens/QRCodeScreen.tsx`

**Implementation**:
- Uses `expo-screen-capture` to prevent screenshots and screen recordings
- Automatically enabled when QR code screen is displayed
- Automatically disabled when user leaves the screen

**Protection against**:
- Screenshots of ephemeral QR codes
- Screen recording attacks
- QR code replay from captured images

**Code**:
```typescript
import * as ScreenCapture from 'expo-screen-capture';

// Enable on mount
await ScreenCapture.preventScreenCaptureAsync();

// Disable on unmount
await ScreenCapture.allowScreenCaptureAsync();
```

---

### 2. Secure Storage (Keychain/Keystore)

**Location**: `src/services/secureStorage.ts`

**Implementation**:
- Uses `expo-secure-store` for platform-native secure storage
- iOS: Keychain Services
- Android: EncryptedSharedPreferences + Android Keystore
- Web: Falls back to AsyncStorage (browser encrypted storage)

**Stored data**:
- JWT authentication tokens
- Device ID
- User profile data

**API**:
```typescript
import { authStorage } from './services/secureStorage';

// Store token securely
await authStorage.setToken(jwtToken);

// Retrieve token
const token = await authStorage.getToken();

// Clear all auth data
await authStorage.clearAll();
```

---

### 3. Device Integrity & Root/Jailbreak Detection

**Location**: `src/services/deviceSecurity.ts`

**Implementation**:
- Uses `react-native-device-info` for device security checks
- Checks for emulator/simulator
- Verifies screen lock (PIN/biometric) is enabled
- Validates minimum OS version requirements
- Generates device fingerprints for attestation

**Security checks**:
- ✅ Emulator detection
- ✅ Screen lock verification
- ✅ OS version validation
- ✅ Device fingerprinting
- ⏳ Root/jailbreak detection (production enhancement)

**API**:
```typescript
import { deviceSecurity } from './services/deviceSecurity';

// Check device integrity
const result = await deviceSecurity.checkDeviceIntegrity();
if (!result.isSecure) {
  // Block app usage or warn user
}

// Verify security requirements
const requirements = await deviceSecurity.meetsSecurityRequirements();
if (!requirements.meets) {
  // Display reasons to user
}

// Generate device fingerprint
const fingerprint = await deviceSecurity.generateDeviceFingerprint();
```

**Component**: `src/components/SecurityCheck.tsx`
- Runs security checks on app launch
- Blocks app if critical threats detected
- Warns user about security issues

---

### 4. Biometric Authentication

**Location**: `src/services/biometricAuth.ts`

**Implementation**:
- Uses `expo-local-authentication` for biometric auth
- Supports Face ID, Touch ID, Fingerprint, Iris
- Falls back to device PIN/pattern if biometric unavailable
- Required for sensitive operations (QR generation)

**Supported methods**:
- iOS: Face ID, Touch ID
- Android: Fingerprint, Face Recognition, Iris

**API**:
```typescript
import { biometricAuth } from './services/biometricAuth';

// Check capability
const capability = await biometricAuth.checkCapability();
// Returns: { isAvailable, biometricType, isEnrolled }

// Authenticate for QR generation
const success = await biometricAuth.authenticateForQRGeneration();
if (!success) {
  // Deny QR generation
}

// Optional: authenticate on app launch
const unlocked = await biometricAuth.authenticateOnLaunch();
```

**Integration**:
- QR code generation requires biometric authentication
- Device registration can require biometric confirmation
- Optional app unlock on launch

---

## 🛡️ Security Architecture

### Defense in Depth

The mobile app implements multiple layers of security:

1. **Device Layer**: Root/jailbreak detection, OS version checks
2. **Storage Layer**: Keychain/Keystore encryption for tokens
3. **Authentication Layer**: Biometric + JWT tokens
4. **Presentation Layer**: Anti-screenshot on sensitive screens
5. **Network Layer**: JWT Bearer tokens, HTTPS enforced

### Threat Mitigation

| Threat | Mitigation |
|--------|-----------|
| QR Code Replay | Anti-screenshot + ephemeral tokens (30s) |
| Token Theft | Secure storage (Keychain/Keystore) |
| Compromised Device | Root/jailbreak detection + device attestation |
| Unauthorized Access | Biometric authentication required |
| Network Interception | HTTPS + JWT signatures (RS256) |
| Device Cloning | Device fingerprinting + attestation data |

---

## 📦 Dependencies

### Security-Related Packages

```json
{
  "expo-screen-capture": "~6.0.0",      // Anti-screenshot
  "expo-secure-store": "~14.0.0",       // Keychain/Keystore
  "expo-local-authentication": "~15.0.2", // Biometric auth
  "react-native-device-info": "^14.0.0", // Device checks
  "expo-device": "~7.0.1"                // Device info
}
```

### Installation

```bash
cd apps/mobile
npm install expo-screen-capture expo-secure-store expo-local-authentication react-native-device-info
```

---

## 🔧 Configuration

### iOS (Info.plist)

Add biometric authentication usage description:

```xml
<key>NSFaceIDUsageDescription</key>
<string>Nous utilisons Face ID pour sécuriser vos pointages</string>
```

### Android (AndroidManifest.xml)

Add biometric permission:

```xml
<uses-permission android:name="android.permission.USE_BIOMETRIC" />
<uses-permission android:name="android.permission.USE_FINGERPRINT" />
```

---

## 🚀 Production Enhancements (TODO)

### Certificate Pinning

Implement SSL certificate pinning to prevent Man-in-the-Middle attacks:

- Use `react-native-ssl-pinning` or similar
- Pin backend API certificate
- Detect and block proxy/MitM attempts

### Advanced Root Detection

Implement production-grade root/jailbreak detection:

- Android: Check for su binaries, test-keys, dangerous apps
- iOS: Check for Cydia, modified frameworks, fork protection
- Consider using commercial solutions (e.g., Arxan, GuardSquare)

### SafetyNet / DeviceCheck Integration

Add platform attestation APIs:

- **Android**: Google SafetyNet Attestation API
- **iOS**: Apple DeviceCheck API
- Send attestation tokens to backend for validation

### Tamper Detection

Detect app tampering:

- Code signature validation
- Checksum verification
- Debug mode detection
- Frida/instrumentation detection

---

## 🧪 Testing Security Features

### Manual Testing

1. **Anti-screenshot**:
   - Navigate to QR code screen
   - Try to take screenshot → should be blocked
   - Leave screen → screenshots should work again

2. **Biometric Auth**:
   - Tap "Generate QR Code"
   - Biometric prompt should appear
   - Cancel → QR not generated
   - Authenticate → QR generated

3. **Secure Storage**:
   - Login
   - Close app
   - Reopen → should still be logged in (token persisted)

4. **Device Checks**:
   - Run on emulator → warning shown
   - Run without screen lock → warning shown

### Automated Testing (TODO)

- Unit tests for security services
- Integration tests for auth flows
- E2E tests with Detox for biometric flows

---

## 📚 References

- [Expo Security Best Practices](https://docs.expo.dev/guides/security/)
- [OWASP Mobile Security](https://owasp.org/www-project-mobile-security/)
- [React Native Security](https://reactnative.dev/docs/security)
- [NIST Mobile Security Guidelines](https://csrc.nist.gov/publications/detail/sp/800-163/rev-1/final)

---

**Last Updated**: 2025-01-20
**Version**: 1.0.0
**Security Level**: Level B (HR Code + OTP + Device Attestation)

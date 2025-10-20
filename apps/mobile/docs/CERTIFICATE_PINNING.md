# Certificate Pinning Implementation Guide

Certificate pinning is a critical security measure to prevent Man-in-the-Middle (MitM) attacks by ensuring the mobile app only trusts specific SSL certificates for the backend API.

## 🎯 Why Certificate Pinning?

Without pinning, attackers can:
- Intercept HTTPS traffic using proxy tools (Charles, Burp Suite)
- Use self-signed certificates to spy on API requests
- Steal JWT tokens and sensitive data
- Replay or modify API calls

With pinning:
- App only trusts the backend's specific certificate
- MitM proxies are detected and blocked
- Network traffic remains secure even if device is compromised

---

## 🔧 Implementation Options

### Option 1: React Native SSL Pinning (Recommended)

**Package**: `react-native-ssl-pinning`

**Pros**:
- Native module for iOS and Android
- SHA-256 hash pinning
- Certificate expiration handling
- Good community support

**Cons**:
- Requires native build (not compatible with Expo Go)
- Need to update app when certificate rotates

### Option 2: Expo Custom Native Module

**Approach**: Use Expo Development Build with custom native modules

**Pros**:
- Integrates with Expo ecosystem
- Can use existing pinning libraries

**Cons**:
- Requires ejecting from managed workflow
- More complex setup

### Option 3: Backend Certificate Validation (Hybrid)

**Approach**: Backend validates client certificates (mutual TLS)

**Pros**:
- No mobile app changes needed
- Backend controls security

**Cons**:
- More complex backend setup
- Doesn't protect initial connection

---

## 📦 Installation (Option 1: react-native-ssl-pinning)

### 1. Install Package

```bash
cd apps/mobile
npm install react-native-ssl-pinning
```

### 2. Eject from Expo Managed Workflow

```bash
npx expo prebuild
```

This generates native `android/` and `ios/` folders.

### 3. Link Native Module (if needed)

```bash
npx pod-install ios  # iOS only
```

---

## 🔐 Get Certificate Fingerprint

### Method 1: OpenSSL (Recommended)

```bash
# Get SHA-256 fingerprint of production API
echo | openssl s_client -servername api.chrona.com -connect api.chrona.com:443 2>/dev/null | openssl x509 -noout -fingerprint -sha256

# Output example:
# SHA256 Fingerprint=AB:CD:EF:12:34:56:78:90:AB:CD:EF:12:34:56:78:90:AB:CD:EF:12:34:56:78:90:AB:CD:EF:12:34:56:78:90
```

### Method 2: Browser

1. Visit `https://api.chrona.com` in Chrome
2. Click padlock → Certificate → Details
3. Copy SHA-256 fingerprint

### Method 3: Python Script

```python
import ssl
import hashlib

hostname = 'api.chrona.com'
port = 443

cert = ssl.get_server_certificate((hostname, port))
der = ssl.PEM_cert_to_DER_cert(cert)
sha256_hash = hashlib.sha256(der).hexdigest()

print(f"SHA-256: {sha256_hash.upper()}")
```

---

## 💻 Code Implementation

### Create Pinning Service

**File**: `src/services/certificatePinning.ts`

```typescript
import { fetch as sslFetch } from 'react-native-ssl-pinning';

const API_URL = 'https://api.chrona.com';

// Production certificate SHA-256 fingerprint
const CERT_FINGERPRINTS = {
  production: 'ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890',
  staging: 'FEDCBA0987654321FEDCBA0987654321FEDCBA0987654321FEDCBA0987654321',
};

export const pinnedFetch = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const url = `${API_URL}${endpoint}`;

  try {
    const response = await sslFetch(url, {
      ...options,
      sslPinning: {
        certs: [
          __DEV__ ? CERT_FINGERPRINTS.staging : CERT_FINGERPRINTS.production,
        ],
      },
      timeoutInterval: 10000,
    });

    return response;
  } catch (error: any) {
    if (error.message?.includes('SSL')) {
      console.error('Certificate pinning failed - potential MitM attack!');
      throw new Error('Security validation failed');
    }
    throw error;
  }
};
```

### Update API Service

**File**: `src/services/api.ts`

```typescript
import { pinnedFetch } from './certificatePinning';

// Replace axios with pinnedFetch for production
const apiClient = {
  async get(endpoint: string, token?: string) {
    const headers: any = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = `Bearer ${token}`;

    const response = await pinnedFetch(endpoint, {
      method: 'GET',
      headers,
    });

    return response.json();
  },

  async post(endpoint: string, data: any, token?: string) {
    const headers: any = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = `Bearer ${token}`;

    const response = await pinnedFetch(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    return response.json();
  },
};
```

---

## 🔄 Certificate Rotation Strategy

### Problem
Certificates expire every 1-3 years. Apps with hard-coded pins will break.

### Solution: Multiple Pinning

Pin **both** current and backup certificates:

```typescript
const CERT_FINGERPRINTS = {
  production: [
    'ABCDEF...', // Current cert (expires 2026-01-15)
    'FEDCBA...', // Backup cert (expires 2027-01-15)
  ],
};
```

### Process
1. **90 days before expiration**: Deploy new cert on server
2. **60 days before**: Release app update with both pins
3. **30 days before**: Ensure >95% users have new app
4. **On expiration**: Switch to new cert on server
5. **After 30 days**: Release app update removing old pin

---

## 🧪 Testing Certificate Pinning

### Test 1: Normal Operation

```bash
# App should work normally
curl https://api.chrona.com/auth/me -H "Authorization: Bearer $TOKEN"
```

### Test 2: Proxy Detection

1. Configure Charles Proxy or Burp Suite
2. Install proxy certificate on device
3. Run app
4. **Expected**: App blocks requests, shows security error

### Test 3: Invalid Certificate

Change fingerprint to wrong value:

```typescript
const CERT_FINGERPRINTS = {
  production: 'WRONGFINGERPRINT123',
};
```

**Expected**: All API calls fail with SSL error

---

## 📱 Platform-Specific Configuration

### iOS (Info.plist)

Allow App Transport Security exceptions for development:

```xml
<key>NSAppTransportSecurity</key>
<dict>
  <key>NSAllowsArbitraryLoads</key>
  <false/>
  <key>NSExceptionDomains</key>
  <dict>
    <key>localhost</key>
    <dict>
      <key>NSExceptionAllowsInsecureHTTPLoads</key>
      <true/>
    </dict>
  </dict>
</dict>
```

### Android (AndroidManifest.xml)

Add network security config:

```xml
<application
  android:networkSecurityConfig="@xml/network_security_config">
```

**File**: `android/app/src/main/res/xml/network_security_config.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
  <!-- Production -->
  <domain-config cleartextTrafficPermitted="false">
    <domain includeSubdomains="true">api.chrona.com</domain>
    <pin-set expiration="2026-01-15">
      <pin digest="SHA-256">ABCDEF1234567890...</pin>
      <pin digest="SHA-256">FEDCBA0987654321...</pin>
    </pin-set>
  </domain-config>

  <!-- Development (localhost) -->
  <domain-config cleartextTrafficPermitted="true">
    <domain includeSubdomains="true">localhost</domain>
    <domain includeSubdomains="true">10.0.2.2</domain>
  </domain-config>
</network-security-config>
```

---

## ⚠️ Important Considerations

### Development vs Production

```typescript
// Toggle pinning based on environment
const USE_PINNING = !__DEV__ && process.env.NODE_ENV === 'production';

export const apiClient = USE_PINNING ? pinnedApiClient : standardApiClient;
```

### Fallback Strategy

If pinning fails repeatedly (e.g., cert rotation issue):

```typescript
let pinningFailures = 0;

async function fetchWithFallback(url: string, options: any) {
  try {
    return await pinnedFetch(url, options);
  } catch (error) {
    pinningFailures++;

    if (pinningFailures > 3) {
      // Alert user and potentially disable pinning temporarily
      Alert.alert(
        'Connection Issue',
        'Please update the app to the latest version'
      );
    }

    throw error;
  }
}
```

### Monitoring

Log pinning failures to backend for detection:

```typescript
catch (error) {
  if (error.message.includes('SSL')) {
    await logSecurityEvent({
      event_type: 'certificate_pinning_failure',
      device_id: deviceId,
      timestamp: new Date().toISOString(),
    });
  }
}
```

---

## 🔗 Resources

- [OWASP Certificate Pinning](https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning)
- [react-native-ssl-pinning](https://github.com/MaxToyberman/react-native-ssl-pinning)
- [Android Network Security Config](https://developer.android.com/training/articles/security-config)
- [iOS App Transport Security](https://developer.apple.com/documentation/bundleresources/information_property_list/nsapptransportsecurity)

---

## 📋 Implementation Checklist

- [ ] Eject from Expo managed workflow
- [ ] Install `react-native-ssl-pinning`
- [ ] Get production certificate SHA-256 fingerprint
- [ ] Implement `certificatePinning.ts` service
- [ ] Update `api.ts` to use pinned fetch
- [ ] Configure Android `network_security_config.xml`
- [ ] Configure iOS App Transport Security
- [ ] Add certificate rotation strategy (multiple pins)
- [ ] Test with Charles Proxy (should block)
- [ ] Add monitoring for pinning failures
- [ ] Document certificate expiration dates
- [ ] Set calendar reminder for cert rotation (90 days before expiry)

---

**Status**: 📝 Documentation Complete - Implementation Pending

**Note**: Certificate pinning requires native builds and cannot be tested in Expo Go. You must create a development build or production build to test pinning.

**Next Steps**:
1. Eject from Expo: `npx expo prebuild`
2. Get production certificate fingerprint
3. Implement pinning service
4. Test with proxy to verify blocking

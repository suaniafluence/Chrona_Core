# TOTP Implementation Guide

## Overview

The Chrona TOTP (Time-based One-Time Password) system provides secure two-factor authentication for employee time tracking with the following features:

### Security Compliance

**Employee Security (Mobile):**
- Secret: ≥160 bits entropy, Base32 encoding, AES-GCM encrypted storage
- TOTP: 6 digits, 30s period, SHA256 algorithm
- QR Provisioning: 300s expiry, single-use, HTTPS TLS1.2+
- Device Binding: Max 3 registered devices, SafetyNet/DeviceCheck attestation
- Recovery: 5 single-use backup codes
- Policy: Screenshot disabled, reprovisioning requires admin approval

**Kiosk Security (Establishment):**
- Backend: TLS1.3, AES-GCM secret storage (KMS/HSM), 90-day key rotation
- Scanner Auth: mTLS or JWT (ES256), rate limit 5/10min, lockout 15min, isolated VLAN
- QR Auth: JWT ES256 format [iss, uid, nonce, exp], 30s expiry, nonce blacklist
- Logging: Encrypted 90-day retention, excludes secrets/OTP
- Monitoring: Duplication detection, 3 failed attempts/10min alert threshold
- Incident: Immediate secret revocation, MFA reset required, GDPR notification

## Architecture

### Database Schema

**Tables created:**
1. `totp_secrets` - Encrypted TOTP secrets with device binding
2. `totp_recovery_codes` - Single-use recovery codes (5 per user)
3. `totp_nonce_blacklist` - Replay attack protection
4. `totp_validation_attempts` - Rate limiting and security monitoring
5. `totp_lockouts` - Account lockout after excessive failures

**Migration:** `backend/alembic/versions/0009_add_totp_tables.py`

### Backend Components

**Core Modules (`backend/src/totp/`):**
- `core.py` - TOTP generation and validation (RFC 6238)
- `encryption.py` - AES-GCM secret encryption
- `provisioning.py` - QR provisioning and activation
- `security.py` - Rate limiting, lockout, nonce blacklist
- `recovery.py` - Recovery code generation and validation

**API Endpoints (`/totp`):**
- `POST /totp/provision` - Initiate TOTP provisioning (returns QR URI)
- `POST /totp/activate` - Activate TOTP after scanning QR
- `POST /totp/validate` - Validate TOTP code (for kiosk punch)
- `POST /totp/recovery/use` - Use recovery code
- `GET /totp/recovery/status` - Get recovery codes status
- `POST /totp/recovery/regenerate` - Regenerate recovery codes

### JWT Algorithm Support

**ES256 (ECDSA P-256) - Recommended for TOTP:**
- Smaller signatures (64 bytes vs 256 bytes)
- Faster signing/verification
- Equivalent security with smaller keys (256-bit vs 2048-bit)

**RS256 (RSA 2048) - Legacy support maintained**

**Key Generation:**
```bash
# ES256 keys (recommended)
cd backend
python tools/generate_ec_keys.py

# RS256 keys (legacy)
python tools/generate_keys.py
```

**Configuration (`.env`):**
```bash
ALGORITHM=ES256  # or RS256
JWT_PRIVATE_KEY_PATH=jwt_ec_private_key.pem
JWT_PUBLIC_KEY_PATH=jwt_ec_public_key.pem

# TOTP encryption key (32 bytes base64)
TOTP_ENCRYPTION_KEY=<generate_with_base64_urandom_32>
```

## Installation & Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**New dependencies added:**
- `cryptography>=41.0.0` - AES-GCM encryption for TOTP secrets

### 2. Generate Keys

```bash
# Generate ES256 keys for JWT signing
cd backend
python tools/generate_ec_keys.py --private-key jwt_ec_private_key.pem --public-key jwt_ec_public_key.pem

# Generate TOTP encryption key
python -c "import base64, os; print(base64.b64encode(os.urandom(32)).decode())"
```

### 3. Configure Environment

Add to `backend/.env`:
```bash
ALGORITHM=ES256
JWT_PRIVATE_KEY_PATH=jwt_ec_private_key.pem
JWT_PUBLIC_KEY_PATH=jwt_ec_public_key.pem
TOTP_ENCRYPTION_KEY=<your_generated_key>
```

### 4. Apply Database Migration

```bash
cd backend
PYTHONPATH=. .venv/Scripts/alembic.exe upgrade head
```

### 5. Start Backend

```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Usage Examples

### Provision TOTP for User

```bash
# 1. Register/login user
curl -X POST http://localhost:8000/auth/token \
  -d "username=user@example.com&password=password"
# Returns: {"access_token": "...", "token_type": "bearer"}

# 2. Initiate TOTP provisioning
curl -X POST http://localhost:8000/totp/provision \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"device_id": null}'
# Returns: {
#   "totp_secret_id": 1,
#   "provisioning_uri": "otpauth://totp/Chrona:user@example.com?secret=...",
#   "expires_at": "2025-04-28T12:05:00",
#   "secret": "JBSWY3DPEHPK3PXP"
# }

# 3. User scans QR code with authenticator app (Google Authenticator, Authy, etc.)
# QR code is generated from provisioning_uri

# 4. Activate TOTP with first code
curl -X POST http://localhost:8000/totp/activate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"totp_secret_id": 1, "verification_code": "123456"}'
# Returns: {
#   "success": true,
#   "message": "TOTP activated successfully...",
#   "recovery_codes": ["ABCD-EFGH", "IJKL-MNOP", ...]
# }
```

### Validate TOTP (Kiosk Punch)

```bash
curl -X POST http://localhost:8000/totp/validate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "totp_code": "123456",
    "kiosk_id": 1,
    "nonce": "uuid-v4-nonce",
    "jwt_jti": "jwt-id"
  }'
# Returns: {
#   "success": true,
#   "message": "TOTP code validated successfully",
#   "time_offset_periods": 0
# }
```

### Use Recovery Code

```bash
curl -X POST http://localhost:8000/totp/recovery/use \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"recovery_code": "ABCD-EFGH"}'
# Returns: {
#   "success": true,
#   "message": "Recovery code used successfully"
# }
```

## Security Features

### Rate Limiting & Lockout

- **Rate Limit:** 5 attempts per 10 minutes
- **Lockout Duration:** 15 minutes
- **Alert Threshold:** 3 failed attempts in 10 minutes

### Replay Attack Protection

- **Nonce Blacklist:** Single-use nonce enforcement
- **JWT JTI Tracking:** Prevent token replay
- **Expiration:** 30-second token lifetime

### Monitoring & Alerting

All TOTP validation attempts are logged for security monitoring:
- Success/failure tracking
- IP address and user agent logging
- Duplication detection
- Rate limit violations
- Account lockouts

### Incident Response

When security incidents are detected:
1. **Immediate secret revocation** - Compromised TOTP secrets disabled
2. **MFA reset required** - User must re-provision TOTP
3. **GDPR notification** - If personal data breach detected
4. **Audit log** - Immutable security event trail

## Frontend Implementation (TODO)

### Mobile App (Expo React Native)

**Requirements:**
- expo-secure-store - Store encrypted TOTP secret
- QR code display component - Show TOTP code with 30s refresh
- expo-screen-capture - Disable screenshots (security policy)
- Device attestation - SafetyNet (Android) / DeviceCheck (iOS)

**Files to create:**
- `apps/mobile/src/screens/TOTPSetup.tsx` - TOTP provisioning UI
- `apps/mobile/src/components/TOTPDisplay.tsx` - TOTP code display
- `apps/mobile/src/services/totp.ts` - TOTP API client

### Kiosk App (Vite React)

**Requirements:**
- html5-qrcode - Scan TOTP QR codes
- TOTP validation UI - Success/failure feedback
- Rate limit handling - Display lockout messages

**Files to create:**
- `apps/kiosk/src/components/TOTPScanner.tsx` - QR scanner component
- `apps/kiosk/src/services/totp.ts` - TOTP validation API client

## Testing

### Unit Tests

```bash
cd backend
pytest tests/test_totp_core.py -v
pytest tests/test_totp_security.py -v
pytest tests/test_totp_endpoints.py -v
```

### Integration Tests

```bash
pytest tests/integration/test_totp_flow.py -v
```

## Monitoring & Maintenance

### Cleanup Tasks

**Expired nonce cleanup (run daily):**
```python
from src.totp.security import cleanup_expired_nonces
from src.db import get_session

with get_session() as db:
    deleted = cleanup_expired_nonces(db, batch_size=1000)
    print(f"Deleted {deleted} expired nonces")
```

**Key rotation (run every 90 days):**
```bash
# Generate new ES256 keys
python tools/generate_ec_keys.py --private-key jwt_ec_private_key_new.pem

# Update .env with new key paths
# Restart backend to load new keys
# Old tokens remain valid until expiration
```

### Security Monitoring

**SQL query for failed attempts:**
```sql
SELECT user_id, COUNT(*) as failed_count
FROM totp_validation_attempts
WHERE is_success = FALSE
  AND attempted_at > datetime('now', '-10 minutes')
GROUP BY user_id
HAVING failed_count >= 3;
```

**Active lockouts:**
```sql
SELECT user_id, locked_until, trigger_reason
FROM totp_lockouts
WHERE is_active = TRUE
  AND locked_until > datetime('now');
```

## Troubleshooting

### "Target database is not up to date"

```bash
cd backend
PYTHONPATH=. .venv/Scripts/alembic.exe upgrade head
```

### "JWT keys not found"

```bash
cd backend
python tools/generate_ec_keys.py
```

### "TOTP validation always fails"

Check clock synchronization:
- TOTP requires synchronized clocks (±30s tolerance)
- Verify server time: `date`
- Check authenticator app time settings

### "Account locked - Rate limit exceeded"

Wait 15 minutes or manually release lockout:
```sql
UPDATE totp_lockouts
SET is_active = FALSE, released_at = datetime('now'), released_by = 'admin'
WHERE user_id = <user_id>;
```

## References

- **RFC 6238:** TOTP: Time-Based One-Time Password Algorithm
- **RFC 4226:** HOTP: An HMAC-Based One-Time Password Algorithm
- **NIST SP 800-63B:** Digital Identity Guidelines (Authentication)

## Next Steps

1. ✅ Backend TOTP implementation (Complete)
2. ⏳ Mobile app TOTP display (In Progress)
3. ⏳ Kiosk TOTP validation UI (Pending)
4. ⏳ End-to-end testing (Pending)
5. ⏳ Security audit (Pending)
6. ⏳ Production deployment (Pending)

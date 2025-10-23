# Guide Complet: Gestion des Utilisateurs et Appareils

## Vue d'Ensemble

Chrona utilise un **système d'onboarding sécurisé en 3 étapes** pour enregistrer les nouveaux employés et leurs appareils:

```
┌─────────────────────────────────────────────────────────┐
│  Nouvel Employé                                         │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  Étape 1: Entrée Code HR (fourni par RH)              │
│  - Employé reçoit un code unique de la RH              │
│  - Saisit le code + son email                          │
│  - Crée une session d'onboarding                       │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  Étape 2: Vérification OTP                             │
│  - Code OTP envoyé par email                           │
│  - Employé vérifie le code                             │
│  - Confirme son adresse email                          │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  Étape 3: Enregistrement Appareil + Création Compte     │
│  - Device fingerprint (ID unique de l'appareil)        │
│  - Données d'attestation (SafetyNet/DeviceCheck)       │
│  - Création du compte utilisateur                      │
│  - Premier appareil lié au compte                      │
└─────────────────────────────────────────────────────────┘
```

---

## 1. Création d'Utilisateurs

### Option A: Onboarding (Recommandé pour Employés)

L'onboarding sécurisé en 3 étapes (voir ci-dessus).

**API Endpoints:**

```bash
# Étape 1: Initier l'onboarding avec code HR
POST /onboarding/initiate
{
  "hr_code": "CHRONA-2025-00001",
  "email": "jean.dupont@company.com"
}

Response:
{
  "success": true,
  "message": "Code OTP envoyé par email",
  "session_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "step": "otp_sent"
}

# Étape 2: Vérifier le code OTP
POST /onboarding/verify-otp
{
  "session_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "otp_code": "123456"
}

Response:
{
  "success": true,
  "message": "OTP vérifié",
  "session_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "step": "device_registration"
}

# Étape 3: Enregistrer l'appareil et créer le compte
POST /onboarding/complete
{
  "session_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "password": "SecurePass1234!",
  "device_name": "iPhone 13 Pro",
  "device_fingerprint": "device-uuid-12345...",
  "attestation_data": {"safetyNetToken": "..."}
}

Response:
{
  "success": true,
  "user": {
    "id": 42,
    "email": "jean.dupont@company.com",
    "role": "user"
  },
  "device": {
    "id": 15,
    "device_name": "iPhone 13 Pro",
    "registered_at": "2025-10-23T10:30:00Z",
    "is_revoked": false
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Option B: Admin Creation (Création Rapide d'Administrateurs)

Pour créer rapidement des administrateurs sans passer par l'onboarding:

```bash
# Admin création (nécessite token admin)
POST /admin/users
Authorization: Bearer <admin-token>

{
  "email": "admin@company.com",
  "password": "SecureAdminPass123!",
  "role": "admin"
}

Response:
{
  "id": 1,
  "email": "admin@company.com",
  "role": "admin"
}
```

**Ou avec le script Python:**

```bash
cd backend
python tools/create_admin_user.py \
  --email "admin@company.com" \
  --password "SecureAdminPass123!" \
  --role admin
```

---

## 2. Enregistrement des Appareils

Chaque utilisateur peut enregistrer **plusieurs appareils**.

### Enregistrement d'un Nouvel Appareil

Après l'onboarding, l'utilisateur peut ajouter d'autres appareils:

```bash
# Enregistrer un nouvel appareil
POST /devices/register
Authorization: Bearer <user-token>

{
  "device_name": "iPad Pro 12.9",
  "device_fingerprint": "device-uuid-ipad-456...",
  "attestation_data": {
    "deviceCheckToken": "...",
    "isSecureHardwareAvailable": true
  }
}

Response:
{
  "id": 16,
  "user_id": 42,
  "device_name": "iPad Pro 12.9",
  "device_fingerprint": "device-uuid-ipad-456...",
  "registered_at": "2025-10-23T14:45:00Z",
  "last_seen_at": "2025-10-23T14:45:00Z",
  "is_revoked": false
}
```

### Lister ses Appareils

```bash
# Voir tous ses appareils (actifs)
GET /devices/me
Authorization: Bearer <user-token>

Response:
[
  {
    "id": 15,
    "device_name": "iPhone 13 Pro",
    "device_fingerprint": "device-uuid-12345...",
    "registered_at": "2025-10-23T10:30:00Z",
    "last_seen_at": "2025-10-23T15:20:00Z",
    "is_revoked": false
  },
  {
    "id": 16,
    "device_name": "iPad Pro 12.9",
    "registered_at": "2025-10-23T14:45:00Z",
    "last_seen_at": "2025-10-23T14:45:00Z",
    "is_revoked": false
  }
]

# Voir aussi les appareils révoqués
GET /devices/me?include_revoked=true

Response:
[
  // ... tous les appareils actifs et révoqués
]
```

---

## 3. Révocation d'Appareils

### Révocation par l'Utilisateur (Self-Service)

L'utilisateur peut révoquer ses propres appareils:

```bash
# Révoquer un appareil personnel
POST /devices/{device_id}/revoke
Authorization: Bearer <user-token>

Response:
{
  "id": 15,
  "device_name": "iPhone 13 Pro",
  "device_fingerprint": "device-uuid-12345...",
  "registered_at": "2025-10-23T10:30:00Z",
  "last_seen_at": "2025-10-23T15:20:00Z",
  "is_revoked": true  # ← Changé à true
}
```

**Cas d'Usage:**
- Appareil perdu/volé
- Appareil défectueux
- Emploi terminé
- Changement de téléphone

### Révocation par un Administrateur (Admin Portal)

Les administrateurs peuvent révoquer n'importe quel appareil:

```bash
# Admin révoque l'appareil d'un utilisateur
POST /admin/devices/{device_id}/revoke
Authorization: Bearer <admin-token>

Response:
{
  "id": 15,
  "user_id": 42,
  "device_name": "iPhone 13 Pro",
  "is_revoked": true
}
```

**Cas d'Usage (Admin):**
- Employé licencié
- Appareil compromis (sécurité)
- Refus de conformité
- Audit de sécurité

---

## 4. Gestion Administrativa Complète

### Lister tous les Appareils (Admin)

```bash
# Voir tous les appareils (tous les utilisateurs)
GET /admin/devices
Authorization: Bearer <admin-token>

# Avec filtres
GET /admin/devices?user_id=42&is_revoked=false

Response:
[
  {
    "id": 15,
    "user_id": 42,
    "device_name": "iPhone 13 Pro",
    "device_fingerprint": "device-uuid-12345...",
    "registered_at": "2025-10-23T10:30:00Z",
    "last_seen_at": "2025-10-23T15:20:00Z",
    "is_revoked": false
  },
  // ... plus d'appareils
]
```

### Lister tous les Utilisateurs (Admin)

```bash
# Voir tous les utilisateurs
GET /admin/users
Authorization: Bearer <admin-token>

Response:
[
  {
    "id": 1,
    "email": "admin@company.com",
    "role": "admin",
    "created_at": "2025-01-15T09:00:00Z"
  },
  {
    "id": 42,
    "email": "jean.dupont@company.com",
    "role": "user",
    "created_at": "2025-10-23T10:30:00Z"
  },
  // ... plus d'utilisateurs
]
```

### Changer le Rôle d'un Utilisateur

```bash
# Promouvoir un utilisateur en administrateur
PATCH /admin/users/{user_id}/role
Authorization: Bearer <admin-token>

{
  "role": "admin"
}

Response:
{
  "id": 42,
  "email": "jean.dupont@company.com",
  "role": "admin"  # ← Changé
}
```

---

## 5. Audit et Sécurité

### Logs d'Audit Automatiques

Chaque action est enregistrée dans la table `audit_logs`:

```sql
-- Table audit_logs
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50),  -- 'device_registered', 'device_revoked', 'user_created', etc.
    user_id INTEGER,
    device_id INTEGER,
    event_data JSONB,        -- Détails de l'événement
    ip_address VARCHAR(45),  -- IP source
    user_agent TEXT,         -- Client user agent
    created_at TIMESTAMP
);

-- Exemples d'événements enregistrés:
- device_registered
- device_revoked
- user_created
- onboarding_initiated
- onboarding_completed
- password_changed
- login_failed
- login_success
```

### Consulter les Logs d'Audit

```bash
# Voir les logs d'audit (admin seulement)
GET /admin/audit-logs?event_type=device_revoked&from=2025-10-01&to=2025-10-31
Authorization: Bearer <admin-token>

Response:
[
  {
    "id": 1234,
    "event_type": "device_revoked",
    "user_id": 42,
    "device_id": 15,
    "event_data": {"device_name": "iPhone 13 Pro"},
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0 ...",
    "created_at": "2025-10-23T15:30:00Z"
  }
]
```

---

## 6. Flux Complets: Scénarios Courants

### Scénario 1: Nouvel Employé S'Inscrit

```
┌─ RH crée un code HR (ex: CHRONA-2025-00001) et le donne à l'employé

└─ Employé (sur son téléphone)
   1. Ouvre l'app Chrona
   2. Entre son code HR et email
   3. Reçoit un code OTP par email
   4. Entre le code OTP
   5. Choisit un mot de passe sécurisé
   6. L'app enregistre le fingerprint du téléphone
   7. Compte créé, ready to clock in/out!

Backend logs:
✓ onboarding_initiated
✓ otp_sent
✓ otp_verified
✓ device_registered
✓ user_created
✓ user_onboarded
```

### Scénario 2: Employé Change de Téléphone

```
┌─ Employé A: Se connecte sur ancien téléphone
   → POST /devices/{old_device_id}/revoke
   ✓ Ancien téléphone révoqué

└─ Employé B: Se connecte sur nouveau téléphone
   → POST /devices/register
   ✓ Nouveau téléphone enregistré
   ✓ Peut continuer à pointer

Backend logs:
✓ device_revoked (ancien)
✓ device_registered (nouveau)
```

### Scénario 3: Employé Licencié

```
┌─ RH ou Admin détecte que l'employé est parti

└─ Admin le révoque
   1. Ouvre le portail Back-office
   2. Cherche l'employé
   3. Clique "Révoquer tous les appareils"
   → POST /admin/devices/{device_id}/revoke
   ✓ Tous les appareils de l'employé révoqués
   ✓ Impossible de pointer

Alternative: Désactiver le compte utilisateur
   → PATCH /admin/users/{user_id}/status
   ✓ Accès complètement bloqué

Backend logs:
✓ device_revoked (tous les appareils)
✓ user_deactivated (optionnel)
```

### Scénario 4: Appareil Compromis

```
┌─ Département IT détecte une compromise
   (ex: appareil perdu, compromis de sécurité)

└─ Admin révoque immédiatement
   1. Back-office → Gestion des appareils
   2. Cherche l'appareil compromis
   3. Clique "Révoquer cet appareil"
   → POST /admin/devices/{device_id}/revoke
   ✓ Appareil immédiatement inutilisable
   ✓ Aucun QR code ne peut être généré
   ✓ Audit log pour traçabilité

Backend logs:
✓ device_revoked (compromis)
✓ security_alert (si intégration)
```

---

## 7. Sécurité et Bonnes Pratiques

### ✅ À Faire

- ✅ Vérifier les codes HR avant distribution
- ✅ Révoquer rapidement les appareils perdus/volés
- ✅ Monitorer les logs d'audit régulièrement
- ✅ Demander l'enregistrement d'un nouvel appareil pour changement
- ✅ Utiliser des mots de passe forts (12+ caractères)
- ✅ Activer l'authentification biométrique sur l'appareil
- ✅ Réviser les appareils inactifs régulièrement

### ❌ À Éviter

- ❌ Partager les codes HR par email non-chiffré
- ❌ Laisser les appareils non-révoqués après licenciement
- ❌ Ignorer les alertes de sécurité
- ❌ Autoriser les appareils non-attestés (en prod)
- ❌ Réutiliser les mêmes codes HR
- ❌ Stocker les mots de passe en clair

---

## 8. Device Fingerprinting & Attestation

### Device Fingerprint

Identifiant unique de l'appareil utilisé pour:
- Prévenir la réutilisation de tokens sur d'autres appareils
- Tracer l'origine des QR codes
- Détecter les appareils usurpés

```javascript
// Exemple: Générer un fingerprint côté mobile
import { getUniqueId } from 'react-native-device-info'

const deviceFingerprint = await getUniqueId()
// Résultat: "12345678-1234-5678-1234-567812345678"
```

### Device Attestation

Preuve que l'appareil est un vrai appareil sécurisé:

**Android (SafetyNet/Play Integrity):**
```json
{
  "attestationType": "BASIC",
  "basicIntegrity": true,
  "evaluationType": "BASIC",
  "ctsProfileMatch": true,
  "timestampMs": 1666000000000
}
```

**iOS (DeviceCheck):**
```json
{
  "isSecureHardwareAvailable": true,
  "deviceCheckToken": "..."
}
```

---

## 9. API Reference Complète

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/onboarding/initiate` | POST | ❌ | Initier onboarding |
| `/onboarding/verify-otp` | POST | ❌ | Vérifier OTP |
| `/onboarding/complete` | POST | ❌ | Compléter onboarding |
| `/devices/register` | POST | ✅ User | Enregistrer nouvel appareil |
| `/devices/me` | GET | ✅ User | Lister ses appareils |
| `/devices/{id}/revoke` | POST | ✅ User | Révoquer son appareil |
| `/admin/users` | GET | ✅ Admin | Lister tous les utilisateurs |
| `/admin/users` | POST | ✅ Admin | Créer un utilisateur |
| `/admin/users/{id}/role` | PATCH | ✅ Admin | Changer rôle utilisateur |
| `/admin/devices` | GET | ✅ Admin | Lister tous les appareils |
| `/admin/devices/{id}/revoke` | POST | ✅ Admin | Révoquer un appareil |
| `/admin/audit-logs` | GET | ✅ Admin | Voir les logs d'audit |

---

## 10. Checklist de Déploiement

- [ ] Codes HR générés et distribués aux RH
- [ ] Email SMTP configuré pour OTP
- [ ] Device attestation intégrée (SafetyNet/DeviceCheck)
- [ ] Premier admin créé
- [ ] Back-office testée (gestion utilisateurs/appareils)
- [ ] Mobile app testée (onboarding)
- [ ] Logs d'audit en place
- [ ] Politique de révocation documentée
- [ ] Formation RH complétée

---

**Version:** 1.0
**Dernière mise à jour:** 23 octobre 2025
**Auteur:** Équipe Chrona

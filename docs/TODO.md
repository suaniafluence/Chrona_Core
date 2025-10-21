# TODO - Chrona Implementation Roadmap

Ce fichier est la **source de vérité** du projet (priorités, décisions, état d'avancement). Mettez‑le à jour à chaque étape clé.

**Roadmap**: Backend (Phase 1) → Kiosk (Phase 2) → Mobile (Phase 3) → CI/CD (Phase 4) → Back-office (Phase 5)

---

## 📊 État Global

- ✅ **Fondations** : Structure monorepo, CI/CD de base, auth basique
- ✅ **Kiosk App** : Interface tablet avec mode plein écran et clé API (Phase 2 complète)
- ✅ **Back-office** : Application admin RH complète (Phase 5.1 + 5.2 frontend)
- 🚧 **En cours** : Endpoints backend admin (users, devices, kiosks, reports, audit)
- ⏳ **À venir** : Mobile app, JWT RS256, device attestation, GDPR features
- ✅ **Phase 1 (Backend)** : 100% - JWT RS256, DB schema, endpoints (devices, punch, admin), 63 tests
- ✅ **Phase 2 (Kiosk)** : 100% - React/TypeScript app, QR scanner, kiosk mode, audio feedback, connection status
- ✅ **Phase 3 (Mobile)** : 95% - React Native Expo app with full security implementation + Certificate Pinning docs
- ✅ **Phase 4 (CI/CD)** : 85% - Full security scanning + E2E tests + smoke tests
- ⏳ **Phase 5 (Back-office)** : 0% - Dashboard RH à venir

---

## Phase 1: Backend Fondations (Sprint actuel)

### 1.1 Infrastructure & Configuration

- [x] Structure monorepo avec backend, apps, docs, infra
- [x] Docker Compose pour dev local (backend + PostgreSQL)
- [x] GitHub Actions CI/CD de base (tests, lint, build)
- [x] FastAPI app avec CORS et async database
- [ ] **Redis pour cache de tokens éphémères** (nonce/jti tracking)
- [ ] **Variables d'environnement pour RS256** : `JWT_PRIVATE_KEY_PATH`, `JWT_PUBLIC_KEY_PATH`
- [ ] **Configuration pgcrypto** pour encryption at rest

### 1.2 JWT Migration HS256 → RS256

- [ ] **Générer paire de clés RS256** (private/public keys)
  - Script: `backend/tools/generate-keys.py` (génère `private.pem`, `public.pem`)
  - Stocker clés dans `.env` ou secrets manager (dev: fichiers, prod: AWS KMS/GCP Secret Manager)
- [ ] **Modifier `backend/src/config/__init__.py`**
  - Changer `ALGORITHM = "RS256"`
  - Ajouter `JWT_PRIVATE_KEY` et `JWT_PUBLIC_KEY` settings
- [ ] **Modifier `backend/src/security.py`**
  - `create_access_token()`: signer avec clé privée RS256
  - `decode_token()`: vérifier avec clé publique RS256
  - Ajouter fonction `create_ephemeral_qr_token(user_id, device_id)` pour tokens 15-30s
- [ ] **Tester migration** : tous les tests auth doivent passer avec RS256
- [ ] **Documenter clés** : ajouter instructions dans `AGENTS.md`

### 1.3 Schéma de Base de Données

- [ ] **Migration Alembic : créer tables manquantes**
  - `devices` (user_id, device_fingerprint, device_name, attestation_data, is_revoked)
  - `kiosks` (kiosk_name, location, device_fingerprint, is_active)
  - `punches` (user_id, device_id, kiosk_id, punch_type, punched_at, jwt_jti)
  - `token_tracking` (jti PK, nonce, user_id, device_id, issued_at, expires_at, consumed_at, consumed_by_kiosk_id)
  - `audit_logs` (event_type, user_id, device_id, kiosk_id, event_data JSONB, ip_address, created_at)
- [ ] **Indexation** : créer indexes sur colonnes fréquemment requêtées
  - `token_tracking.nonce`, `token_tracking.expires_at`
  - `punches.punched_at`, `punches.user_id`
  - `audit_logs.created_at`, `audit_logs.event_type`
- [ ] **Contraintes** : foreign keys, unique constraints, check constraints
- [ ] **Trigger append-only** sur `audit_logs` (empêcher UPDATE/DELETE)
- [ ] **Job de nettoyage** : cron task pour supprimer tokens expirés (token_tracking.expires_at < NOW() - interval '1 hour')

### 1.4 Modèles SQLModel

- [ ] **Créer `backend/src/models/device.py`**
  - Classe `Device(SQLModel, table=True)` avec tous les champs
- [ ] **Créer `backend/src/models/kiosk.py`**
  - Classe `Kiosk(SQLModel, table=True)`
- [ ] **Créer `backend/src/models/punch.py`**
  - Classe `Punch(SQLModel, table=True)`
  - Enum `PunchType` : clock_in, clock_out
- [ ] **Créer `backend/src/models/token_tracking.py`**
  - Classe `TokenTracking(SQLModel, table=True)`
- [ ] **Créer `backend/src/models/audit_log.py`**
  - Classe `AuditLog(SQLModel, table=True)`
- [ ] **Mettre à jour `backend/src/models/__init__.py`** avec exports

### 1.5 Schémas Pydantic

- [ ] **Créer `backend/src/schemas.py` avec schémas supplémentaires**
  - `DeviceCreate`, `DeviceRead`, `DeviceUpdate`
  - `KioskCreate`, `KioskRead`, `KioskUpdate`
  - `PunchCreate`, `PunchRead`
  - `QRTokenRequest`, `QRTokenResponse`
  - `PunchValidateRequest`, `PunchValidateResponse`
  - `AuditLogRead`

### 1.6 Endpoints Device Management

- [ ] **Créer `backend/src/routers/devices.py`**
- [ ] `POST /devices/register` : enregistrer nouveau device
  - Valider device_fingerprint unique par user
  - Stocker attestation_data (SafetyNet/DeviceCheck)
  - Créer audit log
- [ ] `GET /devices/me` : lister devices de l'utilisateur authentifié
- [ ] `POST /devices/{device_id}/revoke` : révoquer device (owner ou admin)
  - Marquer `is_revoked=True`
  - Invalider tous les tokens associés
  - Créer audit log
- [ ] **Tests** : `backend/tests/test_devices.py` (CRUD, revocation, auth)

### 1.7 Endpoints Punch (Time Tracking)

- [ ] **Créer `backend/src/routers/punch.py`**
- [ ] `POST /punch/request-token` : générer QR token éphémère
  - Vérifier user authentifié + device_id valide
  - Générer nonce random (uuid4)
  - Générer jti unique (uuid4)
  - Créer JWT RS256 avec payload: `{sub, device_id, nonce, jti, exp: 30s}`
  - Stocker dans `token_tracking` (Redis ou DB)
  - Retourner `{qr_token, expires_in}`
- [ ] `POST /punch/validate` : valider QR et enregistrer punch
  - Décoder JWT, vérifier signature RS256
  - Vérifier exp (pas expiré)
  - Vérifier nonce unique (pas dans cache/DB)
  - Vérifier jti pas déjà consommé
  - Vérifier device_id existe et non révoqué
  - Vérifier kiosk_id autorisé
  - **Atomiquement** marquer nonce/jti comme consommé
  - Créer record `punches`
  - Créer audit log
  - Retourner confirmation
- [ ] `GET /punch/history` : historique des punches de l'utilisateur
  - Filtres: from, to, limit
  - Pagination
- [ ] **Tests** : `backend/tests/test_punch.py` (request-token, validate, replay protection, expiration)

### 1.8 Endpoints Admin

- [ ] **Étendre `backend/src/routers/admin.py`**
- [ ] `GET /admin/devices` : lister tous les devices
  - Filtres: user_id, is_revoked
- [ ] `POST /admin/devices/{device_id}/revoke` : révoquer n'importe quel device
- [ ] `GET /admin/kiosks` : lister kiosks
- [ ] `POST /admin/kiosks` : enregistrer nouveau kiosk
- [ ] `PATCH /admin/kiosks/{kiosk_id}` : modifier kiosk (is_active, location)
- [ ] `GET /admin/audit-logs` : consulter logs d'audit
  - Filtres: event_type, user_id, from, to
  - Pagination
- [ ] `GET /admin/reports/attendance` : rapport de présence
  - Formats: JSON, CSV, PDF (utiliser ReportLab ou WeasyPrint)
- [ ] **Tests** : `backend/tests/test_admin_*.py` (devices, kiosks, audit, reports)

### 1.9 Service Layer & Business Logic

- [ ] **Créer `backend/src/services/token_service.py`**
  - `generate_ephemeral_token(user_id, device_id) -> str`
  - `validate_token_and_punch(qr_token, kiosk_id, punch_type) -> Punch`
- [ ] **Créer `backend/src/services/audit_service.py`**
  - `log_event(event_type, user_id, device_id, kiosk_id, event_data, request)`
- [ ] **Créer `backend/src/services/device_service.py`**
  - `register_device(user_id, device_fingerprint, device_name, attestation_data) -> Device`
  - `revoke_device(device_id, revoked_by_user_id)`

### 1.10 Tests & Couverture

- [ ] **Tests unitaires** : viser 80%+ de couverture
  - Token generation & validation
  - Nonce/JTI uniqueness
  - Device revocation
  - Punch recording
  - Audit logging
- [ ] **Tests d'intégration** : workflows complets
  - Register device → request token → validate → punch recorded
  - Replay attack prevention (réutiliser même token = erreur)
  - Expired token rejection
- [ ] **Tests de sécurité** : edge cases
  - Token forgé (mauvaise signature)
  - Device révoqué
  - Kiosk non autorisé

### 1.11 Documentation & OpenAPI

- [ ] **Enrichir docstrings** FastAPI pour OpenAPI
- [ ] **Ajouter exemples** dans schémas Pydantic
- [ ] **Tester Swagger UI** : `http://localhost:8000/docs`
- [ ] **Documenter flux complet** dans `docs/specs/punch-flow.md`

---

## Phase 2: Kiosk App (Sprint suivant)

### 2.1 Setup Kiosk Frontend

- [ ] **Initialiser app Vite/React** dans `apps/kiosk/`
  - TypeScript, ESLint, Prettier
  - Axios pour API calls
  - QR code scanner library (html5-qrcode ou jsQR)
- [ ] **Configuration** : `.env` avec `VITE_API_URL`
- [ ] **Proxy Vite** : `/api` → backend

### 2.2 Fonctionnalités Kiosk

- [ ] **UI Scanner QR** : composant avec caméra
- [ ] **Envoyer QR au backend** : `POST /punch/validate`
- [ ] **Afficher confirmation** : succès (vert) ou erreur (rouge)
- [ ] **Mode kiosk** : plein écran, pas de sortie
- [ ] **Enregistrement kiosk** : interface admin pour enregistrer kiosk_id

### 2.3 Sécurité Kiosk

- [ ] **Verrouillage tablette** : mode kiosk Android (Guided Access iOS)
- [ ] **Anti-USB** : désactiver ports USB via MDM
- [ ] **Authentification kiosk** : token API long-lived pour kiosk_id
- [ ] **Rate limiting** : limiter scans par seconde

### 2.4 Tests Kiosk

- [ ] **Tests unitaires** : composants React
- [ ] **Tests E2E** : Playwright (scanner QR, afficher résultat)

---

## Phase 3: Mobile App (2 sprints) - ✅ 95% COMPLETE

### 3.1 Setup Mobile ✅ COMPLETE

- [x] **Choisir framework** : React Native avec Expo choisi
- [x] **Initialiser projet** dans `apps/mobile/`
- [x] **Configuration** : API base URL (auto-détection dev/prod)
- [x] **Navigation** : React Navigation configurée (Stack Navigator)
- [x] **TypeScript** : Configuration avec strict mode
- [x] **Dependencies** : 946 packages installés (axios, react-native-qrcode-svg, expo-device, etc.)

### 3.2 Authentification & Enregistrement ✅ COMPLETE

- [x] **LoginScreen** : Email/password avec JWT storage sécurisé
- [x] **HomeScreen** : Device registration et navigation
- [x] **Device Fingerprint** : Génération avec expo-device (model + OS + timestamp)
- [x] **API Service** : Axios avec JWT interceptor utilisant secure storage
- [x] **Navigation guards** : Conditional rendering basé sur auth state

### 3.3 Génération QR ✅ COMPLETE

- [x] **Appel API** : `POST /punch/request-token` avec device_id
- [x] **Affichage QR** : react-native-qrcode-svg intégré (280x280)
- [x] **Expiration visuelle** : countdown timer 30s avec couleurs (vert→orange→rouge)
- [x] **Auto-régénération** : Token régénéré automatiquement à expiration
- [x] **QRCodeScreen** : UI complète avec warnings et bouton refresh manuel
- [x] **Biometric Auth** : Authentification biométrique avant génération QR

### 3.4 Historique ✅ COMPLETE

- [x] **HistoryScreen** : Liste des pointages (entrée/sortie)
- [x] **Pull-to-refresh** : Actualisation avec RefreshControl
- [x] **Formattage dates** : Format français (DD/MM/YYYY, HH:mm)
- [x] **UI cards** : Cards avec icônes (🟢 entrée, 🔴 sortie)

### 3.5 Onboarding Niveau B ✅ COMPLETE

- [x] **Écran 1** : Saisie code RH (HRCodeScreen.tsx)
- [x] **Écran 2** : OTP par email (OTPVerificationScreen.tsx)
- [x] **Écran 3** : Device attestation (CompleteOnboardingScreen.tsx)
- [x] **Navigation flow** : Intégré dans App.tsx avec stack navigator

### 3.6 Sécurité Mobile ✅ COMPLETE

- [x] **Anti-screenshot** : expo-screen-capture pour bloquer captures d'écran sur QR screen
- [x] **Root/Jailbreak detection** : react-native-device-info avec service deviceSecurity
- [x] **Stockage sécurisé** : expo-secure-store (Keychain iOS, Keystore Android)
- [x] **Device Integrity Checks** : Vérification émulateur, screen lock, OS version
- [x] **Biométrie** : expo-local-authentication pour QR generation et opérations sensibles
- [x] **Security Services** : deviceSecurity.ts, biometricAuth.ts, secureStorage.ts
- [x] **Certificate pinning documentation** : Guide complet d'implémentation (CERTIFICATE_PINNING.md)
- [ ] **Certificate pinning implémentation** : react-native-ssl-pinning (TODO - nécessite prebuild native)

### 3.7 Tests Mobile 🚧 TODO

- [ ] **Tests unitaires** : logique métier, services
- [ ] **Tests E2E** : Detox (onboarding, QR generation, punch flow)

---

## Phase 4: CI/CD Avancé (1 sprint) - ✅ 85% COMPLETE

### 4.1 Sécurité & Qualité ✅ COMPLETE

- [x] **Scan dépendances** : Safety (Python) pour backend
- [x] **NPM Audit** : Scan de vulnérabilités pour mobile, kiosk, backoffice
- [x] **SBOM** : CycloneDX pour Python (backend) et NPM (frontend apps)
- [x] **Scan images Docker** : Trivy avec upload SARIF vers GitHub Security
- [x] **SAST** : Semgrep avec règles Python, JavaScript, TypeScript, React
- [x] **Rapports CI** : Artifacts uploadés pour Safety, NPM audit, Trivy, SBOM, Semgrep
- [ ] **Signature images** : Docker Content Trust ou Cosign (TODO - production)

**Jobs CI implémentés** :
- `security-python-deps`: Safety check avec JSON report
- `security-npm-audit`: npm audit pour toutes les apps frontend
- `security-docker-scan`: Trivy scanner avec SARIF + JSON reports
- `security-sast-semgrep`: Semgrep avec upload SARIF GitHub Security
- `sbom-generation`: CycloneDX SBOM pour Python + Node.js apps
- `e2e-tests-playwright`: Tests E2E backend API + kiosk UI

### 4.2 Tests & Monitoring ✅ NEARLY COMPLETE

- [x] **Tests E2E API** : Playwright pour backend API (auth, punch flow)
- [x] **Tests E2E Kiosk UI** : Playwright pour interface kiosk (15 tests UI)
- [x] **Structure E2E** : Configuration multi-projets (API, kiosk Chrome/Firefox/tablet)
- [x] **E2E CI integration** : Job CI avec artifacts (reports, screenshots, videos)
- [x] **Smoke tests** : Scripts Bash + Python pour validation post-deploy
- [x] **Pytest configuration** : Configured to exclude interactive tools, 72 tests passing
- [ ] **Monitoring** : Prometheus + Grafana (métriques) (TODO)
- [ ] **Logs** : Loki ou ELK stack (TODO)
- [ ] **Alerting** : Sentry pour erreurs (TODO)

**E2E Tests créés** :
- `api.auth.e2e.ts`: Tests authentification complète (7 tests)
- `api.punch-flow.e2e.ts`: Test du flux complet (9 tests)
- `kiosk.ui.e2e.ts`: Tests interface kiosk (15 tests UI) ⭐
- `playwright.config.ts`: Configuration multi-projets avec CI support
- `package.json`: Scripts et dépendances Playwright

**Smoke Tests créés** :
- `tools/smoke-tests.sh`: Script Bash pour validation déploiement ⭐
- `tools/smoke_tests.py`: Script Python cross-platform ⭐
- Tests: health checks, auth flow, protected endpoints, CORS

### 4.3 Artefacts & Preuves ✅ COMPLETE

- [x] **Rapports CI** : JUnit XML, coverage XML (backend), Playwright JUnit/JSON
- [x] **Security artifacts** : Safety, NPM audit, Trivy, SBOM, Semgrep reports
- [x] **SARIF upload** : GitHub Security integration (Trivy + Semgrep)
- [x] **Playwright reports** : HTML reports, screenshots, videos on failure
- [ ] **Dashboards** : exports PDF automatiques (TODO - monitoring)
- [ ] **Logs signés** : checksums des logs CI (TODO - production)

---

## Phase 5: Back-office RH (en cours)

### 5.1 Setup Back-office ✅ TERMINÉ

- [x] **Initialiser app Vite/React** dans `apps/backoffice/`
  - React 18 + TypeScript + Tailwind CSS
  - React Router 6 pour routing
  - Axios pour API client
  - 380 packages installés
- [x] **Auth admin** : login avec JWT
  - Contexte AuthContext
  - Protection des routes (ProtectedRoute)
  - Vérification rôle admin
  - Auto-logout sur 401
- [x] **Layout** : sidebar, navigation
  - Sidebar responsive avec menu mobile
  - Navigation avec 6 pages
  - Section utilisateur avec déconnexion

### 5.2 Fonctionnalités ✅ TERMINÉ (Frontend uniquement)

- [x] **Dashboard** : statistiques temps réel
  - 4 cartes de métriques
  - Graphiques Recharts (barres + lignes)
  - Liste activités récentes
  - Auto-refresh 30s
  - Mock data (endpoint `/admin/dashboard/stats` à créer)
- [x] **Gestion employés** : CRUD users
  - Table complète
  - Création avec modal
  - Toggle rôle admin/user
  - Suppression avec confirmation
- [x] **Gestion devices** : liste, révocation
  - Table avec filtres (actifs/révoqués)
  - Révocation d'appareils
  - Indicateurs visuels de statut
- [x] **Gestion kiosks** : CRUD kiosks
  - Vue en grille (cards)
  - Création avec génération clé API
  - Toggle actif/inactif
  - Alerte sécurisée pour copie clé API
- [x] **Rapports** : génération CSV/PDF
  - Configuration période et filtres
  - Export JSON/CSV/PDF
  - Download automatique
  - Info RGPD
- [x] **Audit logs** : consultation avec filtres
  - Filtrage avancé (type, user, période)
  - Codage couleur par type
  - Détails expandables

**⚠️ Note** : Frontend 100% fonctionnel, endpoints backend à implémenter :
- `GET/POST/PATCH/DELETE /admin/users`
- `GET /admin/devices`, `POST /admin/devices/{id}/revoke`
- `GET/POST/PATCH/DELETE /admin/kiosks`
- `GET /admin/punches`
- `GET /admin/audit-logs`
- `GET /admin/reports/attendance`
- `GET /admin/dashboard/stats` (nouveau)

### 5.3 GDPR Features

- [ ] **DSR** : interface pour access, rectification, erasure
- [ ] **Export données** : JSON/CSV par employé
- [ ] **Registre RGPD** : documentation traitements
- [ ] **Politique confidentialité** : page info employés

---

## Sécurité Transverse (ongoing)

- [ ] **Rate limiting** : Slowapi ou Nginx rate limit
- [ ] **CORS** : configuration stricte par env
- [ ] **Headers sécurité** : Helmet.js ou Starlette middleware (CSP, HSTS, X-Frame-Options)
- [ ] **Validation entrées** : Pydantic strict mode
- [ ] **Secrets rotation** : procédure trimestrielle clés JWT
- [ ] **Backup/Restore** : tests mensuels
- [ ] **Incident response** : runbook documenté

---

## Conformité RGPD (ongoing)

- [ ] **Registre traitements** : `docs/rgpd/registre.md`
- [ ] **DPIA** (si nécessaire) : analyse d'impact
- [ ] **DPO** : désigner délégué protection données
- [ ] **Politique information** : consentement explicite
- [ ] **Tests DSR** : access, rectification, erasure
- [ ] **Revue annuelle** : conformité CNIL

---

## Documentation (ongoing)

- [ ] **README.md** : instructions quickstart
- [ ] **AGENTS.md** : guide dev complet (✅ fait)
- [ ] **CLAUDE.md** : référence pour Claude Code (✅ fait)
- [ ] **docs/specs/** : spécifications techniques (✅ fait)
- [ ] **docs/threat-model/** : analyse menaces (à jour)
- [ ] **docs/rgpd/** : documentation conformité
- [ ] **OpenAPI** : documentation endpoints (auto-généré)
- [ ] **Runbooks** : procédures incidents, déploiement

---

## Liens Utiles

- **Backend** : `backend/` (FastAPI, SQLModel, Alembic)
- **Apps** : `apps/mobile/`, `apps/kiosk/`, `apps/backoffice/`
- **Infra** : `docker-compose.yml`, `.github/workflows/`
- **Docs** : `docs/TODO.md` (ce fichier), `docs/specs/`, `CLAUDE.md`, `AGENTS.md`
- **Tests** : `backend/tests/`, `apps/*/tests/`

---

## Notes de Sprint

### Sprint actuel (Phase 5 - Back-office RH)
**Statut** : Phase 5.1 et 5.2 TERMINÉES ✅ (20 octobre 2025)

**Réalisations** :
- Application back-office complète (React 18 + TypeScript + Tailwind)
- 7 pages fonctionnelles : Login, Dashboard, Users, Devices, Kiosks, Reports, Audit Logs
- Authentification JWT avec protection des routes admin
- Design moderne et responsive (mobile/tablet/desktop)
- Build de production fonctionnel (662kB gzipped à 191kB)

**Bloqueurs** : Aucun (frontend complet)

**Prochaines étapes** :
1. Implémenter les endpoints backend manquants (voir Phase 5.2 note)
2. Tester l'intégration frontend-backend
3. Phase 5.3 : GDPR Features (DSR, export données, registre)

**Décisions** :
- Vite comme bundler (rapide, moderne)
- Tailwind CSS pour styling (utility-first)
- Recharts pour graphiques (léger, performant)
- Axios avec intercepteurs pour API (auto-logout 401)
- Mock data sur dashboard (en attendant endpoint stats)

**Prochaine revue** : Après implémentation endpoints backend, avant Phase 5.3

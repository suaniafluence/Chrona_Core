# 📚 Chrona - Glossaire Complet des Fichiers Markdown

**Version**: 1.0 | **Dernière mise à jour**: 27 Oct 2025

Un index de référence complet de tous les fichiers `.md` du projet Chrona avec descriptions, contenu clé et cas d'usage.

---

## 📋 Table des Matières

- [Résumé Rapide](#résumé-rapide)
- [Catégorie 1: Gestion de Projet](#catégorie-1--gestion-de-projet)
- [Catégorie 2: Démarrage & Installation](#catégorie-2--démarrage--installation)
- [Catégorie 3: Backend](#catégorie-3--backend)
- [Catégorie 4: Mobile](#catégorie-4--mobile)
- [Catégorie 5: Kiosk](#catégorie-5--kiosk)
- [Catégorie 6: Back-office](#catégorie-6--back-office)
- [Catégorie 7: Infrastructure & Déploiement](#catégorie-7--infrastructure--déploiement)
- [Catégorie 8: Sécurité & Conformité](#catégorie-8--sécurité--conformité)
- [Matrice de Références Croisées](#matrice-de-références-croisées)
- [Chemins de Lecture par Rôle](#chemins-de-lecture-par-rôle)

---

## 📊 Résumé Rapide

| Document | Type | Temps | Audience | Objectif |
|----------|------|-------|----------|----------|
| **QUICK_START.md** | Setup | 5 min | Tous | Installation en 1 commande |
| **CLAUDE.md** | Référence | 15 min | Dev | Référence technique complète |
| **AGENTS.md** | Guide | 10 min | Dev | Setup local + standards |
| **README.md** | Aperçu | 5 min | Tous | Intro + Docker |
| **docs/TODO.md** | Suivi | Continu | Tous | **SOURCE DE VÉRITÉ** du backlog |
| **docs/GUIDE_DEPLOIEMENT.md** | Guide | 30 min | DevOps/IT | Déploiement complet |
| **docs/SECURITY.md** | Référence | 5 min | Sécurité | Checklist hardening |
| **docs/RGPD.md** | Conformité | 10 min | Legal/DPO | GDPR compliance |
| **backend/README.md** | Guide | 10 min | Backend | Setup + API |
| **apps/mobile/README.md** | Aperçu | 5 min | Mobile | App overview |
| **apps/mobile/INSTALLATION.md** | Guide | 10 min | Users/IT | Installation pas à pas |
| **apps/mobile/APK_BUILD.md** | Guide | 20 min | Mobile | Build + distribution APK |
| **apps/mobile/EAS_CREDENTIALS_SETUP.md** | Guide | 10 min | DevOps | Automatisation credentials |
| **apps/mobile/SECURITY.md** | Référence | 15 min | Sécurité | Implémentation sécurité |
| **apps/kiosk/README.md** | Aperçu | 10 min | Frontend | App tablet kiosk |
| **apps/backoffice/README.md** | Aperçu | 10 min | Frontend | Portal HR admin |
| **BACKEND_ENDPOINTS_COMPLETE.md** | Référence | 15 min | API | Tous les endpoints |
| **DOCUMENTATION_INDEX.md** | Index | 5 min | Tous | Navigation master |

---

## Catégorie 1: 🗂️ Gestion de Projet

### **📍 docs/TODO.md** - **AUTHORITATIVE BACKLOG**

**Objectif**: Suivi du backlog projet et feuille de route d'implémentation avec statut par phase.

**Contenu Clé**:
- **Phase 1: Backend** (100% ✅ - JWT RS256, DB, 63 tests)
- **Phase 2: Kiosk** (100% ✅ - React/TypeScript, scanner QR)
- **Phase 3: Mobile** (95% 🟡 - React Native + sécurité)
- **Phase 4: CI/CD** (85% 🟡 - Security scanning, E2E tests)
- **Phase 5: Back-office** (Frontend 100%, API endpoints implémentés)
- Breakdown par sprint avec checkboxes
- Requirements transverses (sécurité, GDPR)
- Statut maintenance documentation

**Quand le Lire**:
- ⭐ **AVANT de commencer une nouvelle feature**
- Planification sprint
- Suivi progrès global
- **TOUJOURS mettre à jour AVANT trackers externes**

**Liens Croisés**:
- CLAUDE.md (détails architecture)
- docs/GUIDE_DEPLOIEMENT.md (procédures déploiement)
- Tous les README des composants

---

### **📍 DOCUMENTATION_INDEX.md** - Hub de Navigation Central

**Objectif**: Centre de navigation centralisant tous les docs avec chemins de lecture par rôle.

**Contenu Clé**:
- Quick start guides par rôle (Dev, DevOps, Security, DPO, Admin, User)
- Index par catégorie (mobile, backend, infrastructure, security)
- Index par topic (architecture, auth, déploiement, réseau)
- FAQ et liens troubleshooting
- Progression de lecture recommandée (1h)
- Suivi priorité mise à jour docs

**Quand le Lire**:
- 🚀 **PREMIÈRE VIS du projet**
- Impossible de trouver la bonne doc
- Comprendre structure documentation
- Reference index

**Liens Croisés**: Tous les docs du projet

---

## Catégorie 2: 🚀 Démarrage & Installation

### **📍 QUICK_START.md** - Installation Rapide (3 commandes)

**Objectif**: Faire tourner l'entier système Chrona en 3 commandes avec scripts automatisés.

**Contenu Clé**:
- Prérequis (Windows, Podman/Docker, Python, Node.js)
- `.\setup-dev.ps1` - Installation complète automatisée
- `.\start-kiosk.ps1` et `.\start-backoffice.ps1` - Lanceurs apps
- `.\setup-mobile.ps1` - Configuration mobile
- URLs résumé (Backend: 8000, Back-office: 5173, Kiosk: 5174)
- Config firewall pour mobile
- Troubleshooting issues communes

**Quand le Lire**:
- 🟢 **START HERE** - Setup première fois
- Onboarding nouveaux devs
- Reset environnement rapide

**Liens Croisés**:
- docs/GUIDE_DEPLOIEMENT.md (installation manuelle détaillée)
- CLAUDE.md (comprendre architecture)

---

### **📍 README.md** - Introduction Projet + Docker

**Objectif**: Introduction projet avec installation Docker et aperçu de tous les composants.

**Contenu Clé**:
- Aperçu système (time tracking sécurisé avec JWT RS256 QR codes)
- Quick start avec scripts setup
- Déploiement Docker Compose (backend, kiosk, PostgreSQL)
- Lancement app mobile avec Expo Go
- Info images GHCR
- Génération clés JWT
- Migrations Alembic
- Health checks services

**Quand le Lire**:
- Aperçu projet et introduction
- Installation basée Docker
- Vérifier statut CI/CD badges

**Liens Croisés**:
- QUICK_START.md (setup automatisé)
- docs/GUIDE_DEPLOIEMENT.md (déploiement production)

---

### **📍 AGENTS.md** - Setup Dev Local + Standards

**Objectif**: Procédures setup local développeurs, standards code, structure repo.

**Contenu Clé**:
- Structure projet (`apps/`, `backend/`, `docs/`, `infra/`)
- Backend quickstart (FastAPI, venv, uvicorn)
- Migrations DB (Alembic)
- Auth quickstart (register, token, me endpoints)
- Gestion rôles admin
- Password hashing (bcrypt_sha256 avec truncation 72-byte)
- Commandes Docker Compose
- Style code (Python 4-space, JS 2-space, Conventional Commits)
- Guidelines testing (~80% coverage target)

**Quand le Lire**:
- Setup environnement dev local
- Comprendre structure repo
- Suivre standards code
- Lancer tests et linting

**Liens Croisés**:
- CLAUDE.md (architecture détaillée)
- backend/README.md (spécifiques backend)
- docs/TODO.md (backlog tasks)

---

## Catégorie 3: ⚙️ Backend

### **📍 backend/README.md** - Setup Backend API

**Objectif**: Setup API FastAPI, configuration, et guide utilisation.

**Contenu Clé**:
- FastAPI avec SQLModel/SQLAlchemy (async)
- Génération clés JWT RS256 (`tools/generate_keys.py`)
- Variables environnement (DATABASE_URL, CORS, SECRET_KEY)
- Lancement Uvicorn (local avec SQLite ou Postgres)
- Setup Docker Compose recommandé
- Workflow migrations Alembic
- Commandes tests (pytest, black, isort, flake8)
- Endpoints main (health, auth, devices, kiosk, punch)
- Exemples cURL

**Quand le Lire**:
- Setup backend dev
- Comprendre architecture API
- Lancer tests et migrations
- Déployer backend

**Liens Croisés**:
- CLAUDE.md (référence complète endpoints API)
- BACKEND_ENDPOINTS_COMPLETE.md (liste endpoints complets)
- backend/tests/README.md (testing)

---

### **📍 BACKEND_ENDPOINTS_COMPLETE.md** - Référence Tous Endpoints

**Objectif**: Référence complète de tous les endpoints backend implémentés avec statut.

**Contenu Clé**:
- Tous endpoints implémentés (20 Oct 2025)
- Endpoints auth (token, register, me)
- Gestion users (CRUD, updates rôles)
- Gestion devices (list, revoke)
- Gestion kiosks (CRUD, API key generation)
- Endpoint punch history
- Endpoint audit logs
- Endpoint stats dashboard (nouveau)
- Protections sécurité (JWT, role-based access)
- Notes performance (< 100ms dashboard stats)

**Quand le Lire**:
- Intégration API
- Comprendre endpoints disponibles
- Reference dev backend
- Testing endpoints

**Liens Croisés**:
- backend/README.md (setup)
- CLAUDE.md (architecture)
- apps/backoffice/README.md (intégration frontend)

---

## Catégorie 4: 📱 Mobile

### **📍 apps/mobile/README.md** - Aperçu App Mobile

**Objectif**: Aperçu app React Native avec Expo pour time tracking employés.

**Contenu Clé**:
- Features: auth, device registration, ephemeral QR (30s), history
- Installation avec npm
- Configuration (auto-detection API URL dev/prod)
- User flow (login → device registration → QR generation → history)
- Config API base URL (`http://10.0.2.2:8000` pour Android emulator)

**Quand le Lire**:
- Aperçu app mobile
- Quick reference devs

**Liens Croisés**:
- INSTALLATION.md (setup détaillé)
- APK_BUILD.md (processus build)
- SECURITY.md (features sécurité)
- CLAUDE.md (architecture)

---

### **📍 apps/mobile/INSTALLATION.md** - Guide Installation Pour Users

**Objectif**: Guide pas-à-pas installation app mobile sur Android/iOS pour end users.

**Contenu Clé**:
- Prérequis (Android 8+/iOS 13+, app Expo Go)
- Installation 5-étapes:
  1. Install Expo Go
  2. Run `.\setup-mobile.ps1` sur PC
  3. Configure Windows firewall
  4. Start app avec `npm start`
  5. Scan QR code
- Test connectivité backend depuis phone
- Configuration manuelle (fichier `.env`)
- Troubleshooting (erreurs réseau, QR code issues)
- Usage app (onboarding, QR generation, history)

**Quand le Lire**:
- Installation app mobile première fois
- Guide setup end-user
- Troubleshooting connectivité mobile

**Liens Croisés**:
- README.md (overview)
- APK_BUILD.md (déploiement production)
- docs/GUIDE_DEPLOIEMENT.md (déploiement complet)

---

### **📍 apps/mobile/APK_BUILD.md** - Build & Distribution APK

**Objectif**: Guide complet pour build et distribution Android APK avec EAS Build.

**Contenu Clé**:
- Prérequis (compte Expo, EAS CLI)
- Configuration EAS Build (`eas.json`, `app.json`)
- Méthodes build:
  - Preview (APK pour testing interne)
  - Production (AAB pour Google Play)
  - Local build (requires Android SDK)
- Options distribution APK (download direct, QR code, hosting local, USB)
- Installation sur Android (enable sources inconnues)
- Procédure increment version
- Troubleshooting (build failures, credential errors, network issues)
- Sécurité (keystore signing, verification)

**Quand le Lire**:
- Build APK pour distribution
- Publication Google Play Store
- Distribution app interne

**Liens Croisés**:
- EAS_CREDENTIALS_SETUP.md (automatisation credentials)
- INSTALLATION.md (installation end-user)
- docs/GUIDE_DEPLOIEMENT.md (déploiement production)

---

### **📍 apps/mobile/EAS_CREDENTIALS_SETUP.md** - Automatisation Credentials EAS

**Objectif**: Quick guide pour automatiser génération Android keystore pour EAS builds en GitHub Actions.

**Contenu Clé**:
- Prérequis (Node.js, compte Expo, accès repo GitHub)
- Installation et auth EAS CLI
- Configuration credentials Android (menu interactif)
- Création keystore (alias, passwords)
- Génération EXPO_TOKEN et setup GitHub secrets
- Vérification `eas.json`
- Testing local (`eas build --local`)
- Testing workflow GitHub Actions
- Troubleshooting (mode non-interactif, authentication, credential errors)
- Checklist next steps (10 steps)

**Quand le Lire**:
- Setup EAS credentials pour CI/CD
- Automatisation APK builds en GitHub Actions
- Troubleshooting credential issues

**Liens Croisés**:
- APK_BUILD.md (builds manuels)
- .github/workflows/* (CI/CD workflows)

---

### **📍 apps/mobile/SECURITY.md** - Implémentation Sécurité Mobile

**Objectif**: Documentation complète des features sécurité implémentées et mitigation menaces.

**Contenu Clé**:
- Protection anti-screenshot (`expo-screen-capture`)
- Stockage sécurisé (Keychain iOS, Keystore Android)
- Integrity checks device (emulator detection, root/jailbreak detection)
- Biometric auth (Face ID, Touch ID, Fingerprint)
- Architecture defense-in-depth (5 couches)
- Matrice mitigation menaces (QR replay, token theft, device compromis)
- Dependencies sécurité (expo-screen-capture, expo-secure-store, expo-local-authentication, react-native-device-info)
- Enhancements production (certificate pinning, advanced root detection, SafetyNet/DeviceCheck)
- Procédures testing

**Quand le Lire**:
- Comprendre features sécurité mobile
- Audits sécurité
- Implémentation mesures sécurité supplémentaires
- Threat modeling

**Liens Croisés**:
- README.md (app overview)
- docs/SECURITY.md (stratégie sécurité globale)
- docs/CERTIFICATE_PINNING.md (sécurité HTTPS)

---

## Catégorie 5: 🖥️ Kiosk

### **📍 apps/kiosk/README.md** - App Tablet Kiosk

**Objectif**: Guide app kiosk React/TypeScript pour scanner QR codes à points d'entrée.

**Contenu Clé**:
- Features: scanner QR, kiosk mode (fullscreen), feedback audio/visuel, connection status, API key auth
- Prérequis (Node.js, backend running, kiosk registered)
- Configuration (fichier `.env`: API_URL, KIOSK_ID, PUNCH_TYPE, API_KEY)
- Génération API key (`generate_kiosk_api_key.py`)
- Modes dev et production
- Usage (normal mode → kiosk mode, exit kiosk mode)
- Hardware recommandé (Android 8+/iPadOS 14+, écran 10", caméra 720p)
- Interface (header, scan zone, result feedback)
- Sécurité (API key par kiosk, JWT RS256 tokens, mode locking)
- Troubleshooting (camera permissions, API key validation, QR recognition)
- Technologies (React 18, TypeScript 5, Vite 6, html5-qrcode, Axios)

**Quand le Lire**:
- Setup tablet kiosk
- Comprendre fonctionnalité kiosk
- Configuration hardware

**Liens Croisés**:
- CLAUDE.md (architecture)
- backend/README.md (intégration API)
- docs/GUIDE_DEPLOIEMENT.md (déploiement)

---

## Catégorie 6: 💼 Back-office

### **📍 apps/backoffice/README.md** - Portal HR Admin

**Objectif**: Documentation app React/TypeScript back-office HR avec features admin complètes.

**Contenu Clé**:
- Features:
  - Auth (JWT, role verification, persistent session)
  - Dashboard (real-time stats, graphs, auto-refresh 30s)
  - User management (CRUD, role toggle)
  - Device management (list, filter, revoke)
  - Kiosk management (CRUD, API key generation)
  - Reports (configurable, multi-format: JSON/CSV/PDF)
  - Audit logs (filtering, expandable details)
- Technologies (React 18, Vite, React Router 6, Tailwind CSS, Axios, Recharts)
- Installation et configuration
- Dev server (port 5173 avec proxy)
- Production build
- Project structure
- Backend API endpoints utilisés
- Features sécurité (JWT, role-based, auto-logout)
- Info GDPR compliance

**Quand le Lire**:
- Dev back-office
- Comprendre features admin
- Intégration API

**Liens Croisés**:
- BACKEND_ENDPOINTS_COMPLETE.md (référence API)
- backend/README.md (setup backend)
- docs/RGPD.md (conformité)

---

## Catégorie 7: 🏗️ Infrastructure & Déploiement

### **📍 docs/GUIDE_DEPLOIEMENT.md** - Guide Déploiement Complet

**Objectif**: Guide déploiement complet couvrant environnements dev, test, production avec procédures détaillées.

**Contenu Clé**:
- **Prérequis**: Requirements système (Windows/Linux), versions logiciels, architecture réseau
- **Quick Install**: Scripts automatisés (setup-dev.ps1, start-kiosk.ps1, setup-mobile.ps1)
- **Install Dev**:
  - Option 1: Docker Compose (recommandé)
  - Option 2: Manuel (Windows/Linux)
  - Génération clés JWT
  - Génération SECRET_KEY (64 chars, base64)
  - Configuration environnement
  - HTTPS local avec mkcert + Traefik
- **Install Production**:
  - Préparation serveur (Ubuntu/RHEL, Docker, Nginx, firewall)
  - Setup PostgreSQL (encryption at rest)
  - Clés JWT (RSA 4096-bit)
  - SECRET_KEY avec secrets manager
  - Config Docker Compose production
  - Reverse proxy Nginx avec SSL/TLS
  - Certificats Let's Encrypt
  - Automatisation backup (cron)
- **App Mobile**:
  - Architecture diagram
  - Setup dev (Expo Go)
  - Config API URL (WiFi IP, ngrok)
  - Production builds (EAS, local, MDM distribution)
  - Sécurité (certificate pinning, anti-screenshot)
- **Configuration Email**: Gmail, SendGrid, Office 365
- **Sécurité & Secrets**: Génération clés, stockage (dev vs prod), rotation
- **E2E Tests**: Configuration Playwright, DB initialization, API key generation
- **Vérification & Tests**: Health checks, performance tests, smoke tests
- **Troubleshooting**: Issues communes et solutions
- **CI/CD**: Génération SBOM avec CycloneDX, artifact downloads
- **Production Checklist**: 30+ items

**Quand le Lire**:
- ⭐ **ESSENTIEL pour déploiement** (dev ou production)
- Comprendre architecture infrastructure
- Configuration sécurité
- Troubleshooting issues déploiement

**Liens Croisés**:
- QUICK_START.md (setup automatisé)
- README.md (basics Docker)
- docs/SECURITY.md (mesures sécurité)
- docs/RGPD.md (conformité)

---

## Catégorie 8: 🔒 Sécurité & Conformité

### **📍 docs/SECURITY.md** - Checklist Hardening Sécurité

**Objectif**: Checklist hardening sécurité et mesures implémentées pour le backend.

**Contenu Clé**:
- **Implémenté**:
  - Security headers middleware (FastAPI)
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - Referrer-Policy: no-referrer
  - Permissions-Policy restrictions
  - Content-Security-Policy (CSP)
  - Optional HSTS (enable avec `ENABLE_HSTS=true` derrière HTTPS)
- **TODO**:
  - Rate limiting pour endpoints sensibles
  - Protection brute-force
  - Password policy & strength checks
  - Secrets scanning en CI
  - Dependency vulnerability gating
  - Audit logs alerting (SIEM)
  - CSP review pour backoffice/kiosk

**Quand le Lire**:
- Audits sécurité
- Implémentation features sécurité supplémentaires
- Hardening production
- Requirements conformité

**Liens Croisés**:
- docs/RGPD.md (conformité)
- apps/mobile/SECURITY.md (sécurité mobile)
- docs/GUIDE_DEPLOIEMENT.md (configuration sécurité)

---

### **📍 docs/RGPD.md** - Conformité GDPR/CNIL

**Objectif**: Documentation conformité GDPR/CNIL incluant rôles, catégories data, retention, procédures DSR.

**Contenu Clé**:
- **Rôles**: Controller (client), Processor (hosting team)
- **Catégories Data**:
  - Identité (email, rôle, IDs)
  - Devices (fingerprint, name, attestation)
  - Punches (date/time, type, device/kiosk links)
  - Audit (security events, IP, user-agent)
- **Legal Basis**: Contract execution, legal obligations, legitimate interest
- **Périodes Retention**:
  - Comptes users: relationship + 2 ans
  - Devices/Kiosks: 12 mois après revocation
  - Punches: 5 ans (HR reference)
  - Audit logs: 12-24 mois
- **Procédures DSR**:
  - Access/Portability (export JSON/CSV)
  - Rectification (admin interface)
  - Erasure (anonymization, exceptions légales)
  - Limitation/Opposition (account freeze, device revocation)
- **Sécurité**: Auth, audit, HTTPS, encryption at rest, access controls
- **Transparence**: Privacy notice pour employés
- **ROPA**: Template registry (docs/rgpd/registre.md)
- **DPIA**: Necessity assessment et process
- **Procédures Opérationnelles**: Access requests, erasure, revocation
- **Future Enhancements**: DSR exports dédiés, auto purge, encryption at rest

**Quand le Lire**:
- Assessment conformité GDPR
- Handling DSR requests
- Privacy impact analysis
- Legal/DPO review

**Liens Croisés**:
- docs/SECURITY.md (mesures sécurité)
- docs/GUIDE_DEPLOIEMENT.md (encryption, HTTPS)
- BACKEND_ENDPOINTS_COMPLETE.md (endpoints DSR)
- apps/backoffice/README.md (outils admin)

---

## 🔗 Matrice de Références Croisées

| Topic | Document Primaire | Documents Liés |
|-------|------------------|-----------------|
| **Aperçu Projet** | README.md | QUICK_START.md, CLAUDE.md, DOCUMENTATION_INDEX.md |
| **Architecture** | CLAUDE.md | AGENTS.md, backend/README.md, docs/TODO.md |
| **Getting Started** | QUICK_START.md | README.md, AGENTS.md, docs/GUIDE_DEPLOIEMENT.md |
| **Backend API** | backend/README.md | CLAUDE.md, BACKEND_ENDPOINTS_COMPLETE.md |
| **App Mobile** | apps/mobile/README.md | INSTALLATION.md, APK_BUILD.md, SECURITY.md |
| **Build APK** | APK_BUILD.md | EAS_CREDENTIALS_SETUP.md, INSTALLATION.md |
| **Tablet Kiosk** | apps/kiosk/README.md | CLAUDE.md, docs/GUIDE_DEPLOIEMENT.md |
| **Back-office** | apps/backoffice/README.md | BACKEND_ENDPOINTS_COMPLETE.md |
| **Déploiement** | docs/GUIDE_DEPLOIEMENT.md | QUICK_START.md, README.md, docs/SECURITY.md |
| **Sécurité** | docs/SECURITY.md | apps/mobile/SECURITY.md, docs/RGPD.md |
| **GDPR/Conformité** | docs/RGPD.md | docs/SECURITY.md, apps/backoffice/README.md |
| **Suivi Tasks** | docs/TODO.md | CLAUDE.md, AGENTS.md |
| **Toute Documentation** | DOCUMENTATION_INDEX.md | Tous les fichiers |

---

## 🧑‍💼 Chemins de Lecture par Rôle

### 🛠️ **Développeur (Nouveau au Projet)**

**Objectif**: Comprendre architecture, setup local, commencer à contribuer

1. **QUICK_START.md** (5 min) - Faire tourner l'environnement
2. **CLAUDE.md** (15 min) - Comprendre architecture
3. **AGENTS.md** (10 min) - Apprendre standards code
4. **backend/README.md** (10 min) - Spécifiques backend
5. **apps/mobile/README.md** (5 min) - Aperçu mobile
6. **docs/TODO.md** (ongoing) - Vérifier tasks

**Temps Total**: ~45 minutes ⏱️

---

### 🚀 **DevOps/IT (Déploiement)**

**Objectif**: Installer et maintenir Chrona en production/staging

1. **QUICK_START.md** (5 min) - Aperçu setup rapide
2. **docs/GUIDE_DEPLOIEMENT.md** (30 min) - Guide déploiement complet
3. **docs/SECURITY.md** (5 min) - Checklist sécurité
4. **apps/mobile/APK_BUILD.md** (20 min) - Distribution mobile
5. **apps/kiosk/README.md** (10 min) - Setup kiosk
6. **docs/RGPD.md** (10 min) - Requirements conformité

**Temps Total**: ~80 minutes ⏱️

---

### 🔒 **Sécurité/Auditeur**

**Objectif**: Audit sécurité et conformité système

1. **CLAUDE.md** (15 min) - Aperçu architecture
2. **docs/SECURITY.md** (5 min) - Mesures sécurité
3. **apps/mobile/SECURITY.md** (15 min) - Sécurité mobile
4. **docs/RGPD.md** (10 min) - Conformité
5. **docs/GUIDE_DEPLOIEMENT.md** (section sécurité) (20 min)

**Temps Total**: ~65 minutes ⏱️

---

### ⚖️ **DPO/Légal**

**Objectif**: Assurer conformité GDPR et droits DSR

1. **docs/RGPD.md** (10 min) - Aperçu GDPR
2. **apps/backoffice/README.md** (10 min) - Outils admin
3. **BACKEND_ENDPOINTS_COMPLETE.md** (15 min) - Endpoints DSR
4. **docs/GUIDE_DEPLOIEMENT.md** (section conformité)

**Temps Total**: ~35 minutes ⏱️

---

### 👤 **End User/Employé**

**Objectif**: Installer et utiliser app mobile

1. **apps/mobile/INSTALLATION.md** (10 min) - Installation app
2. **QUICK_START.md** (section mobile setup)

**Temps Total**: ~15 minutes ⏱️

---

### 📊 **Responsable Projet/Manager**

**Objectif**: Suivi progrès, planning, statut global

1. **docs/TODO.md** (15 min) - Statut complète par phase
2. **README.md** (5 min) - Aperçu système
3. **DOCUMENTATION_INDEX.md** (5 min) - Accès rapide docs

**Temps Total**: ~25 minutes ⏱️

---

## 📝 Notes Importantes

### ⭐ Source de Vérité
- **docs/TODO.md** est l'authoritative backlog
- **Toujours mettre à jour AVANT external trackers**
- Consulte avant demander status tâches

### 🔄 Cycle de Mise à Jour Docs
- Docs updated lors des commits
- Version badge dans chaque file
- Changelog dans git messages
- Links vérifiés mensuellement

### 🆘 Besoin d'Aide?

| Question | Document à Consulter |
|----------|---------------------|
| "Par où commencer?" | QUICK_START.md ou DOCUMENTATION_INDEX.md |
| "Comment déployer?" | docs/GUIDE_DEPLOIEMENT.md |
| "Quelle est la tâche suivante?" | docs/TODO.md |
| "Comment construire l'APK?" | apps/mobile/APK_BUILD.md |
| "Quels sont les endpoints API?" | BACKEND_ENDPOINTS_COMPLETE.md |
| "Comment assurer GDPR?" | docs/RGPD.md |
| "Où sont les standards code?" | AGENTS.md |

---

**Dernière mise à jour**: 27 Oct 2025 | **Statut**: ✅ Complet et à jour

# 📚 Index de la Documentation - Chrona

Bienvenue ! Ce fichier est un **guide central** pour naviguer dans toute la documentation du projet Chrona. Utilisez les liens ci-dessous pour accéder aux guides spécifiques.

---

## 🚀 Démarrage Rapide

Commencez par l'un de ces guides selon votre contexte :

| Guide | Durée | Contenu |
|-------|-------|---------|
| [**QUICK_START.md**](./QUICK_START.md) | 5 min | Démarrage rapide complet du projet (dev, kiosk, mobile) |
| [**SETUP_EAS_QUICK_START.md**](./SETUP_EAS_QUICK_START.md) | 3 min | Configuration APK Android pour GitHub Actions |
| [**CLAUDE.md**](./CLAUDE.md) | 10 min | Guide Claude Code avec architecture et commandes |

---

## 📱 Applications Mobiles

### Application Employé (Mobile)

| Document | Objectif | Public |
|----------|----------|--------|
| [**apps/mobile/README.md**](./apps/mobile/README.md) | Vue d'ensemble de l'app mobile | Tous |
| [**apps/mobile/INSTALLATION.md**](./apps/mobile/INSTALLATION.md) | Installation sur téléphones Android/iOS | Employés, IT |
| [**apps/mobile/APK_BUILD.md**](./apps/mobile/APK_BUILD.md) | Génération et distribution d'APK | Développeurs, IT |
| [**apps/mobile/EAS_CREDENTIALS_SETUP.md**](./apps/mobile/EAS_CREDENTIALS_SETUP.md) | Configuration keystore Android (EAS) | Développeurs |
| [**apps/mobile/GITHUB_RELEASES.md**](./apps/mobile/GITHUB_RELEASES.md) | Création automatique de releases GitHub | DevOps, CI/CD |
| [**apps/mobile/SECURITY.md**](./apps/mobile/SECURITY.md) | Sécurité et protections de l'app mobile | Architectes, Audits |
| [**apps/mobile/docs/CERTIFICATE_PINNING.md**](./apps/mobile/docs/CERTIFICATE_PINNING.md) | Pinning de certificats HTTPS | Sécurité |

### Kiosk Tablet (Android)

| Document | Objectif | Public |
|----------|----------|--------|
| [**apps/kiosk/README.md**](./apps/kiosk/README.md) | Vue d'ensemble du kiosk tablet | Tous |
| [**apps/kiosk/KIOSK_MODE.md**](./apps/kiosk/KIOSK_MODE.md) | Configuration du mode kiosk (verrouillage) | IT, Déploiement |
| [**apps/kiosk-mobile/README.md**](./apps/kiosk-mobile/README.md) | Application mobile kiosk (version mobile du kiosk) | Développeurs |
| [**apps/kiosk-mobile/QUICK_START.md**](./apps/kiosk-mobile/QUICK_START.md) | Démarrage rapide kiosk mobile | Développeurs |
| [**apps/kiosk-mobile/DEPLOYMENT.md**](./apps/kiosk-mobile/DEPLOYMENT.md) | Déploiement du kiosk mobile | DevOps, IT |
| [**apps/kiosk-mobile/QR_CONFIG_GUIDE.md**](./apps/kiosk-mobile/QR_CONFIG_GUIDE.md) | Configuration des QR codes | Administrateurs |
| [**apps/kiosk-mobile/HEARTBEAT_GUIDE.md**](./apps/kiosk-mobile/HEARTBEAT_GUIDE.md) | Système de heartbeat (cœur battant) | Opérations |
| [**apps/kiosk-mobile/SUMMARY.md**](./apps/kiosk-mobile/SUMMARY.md) | Résumé architecture kiosk mobile | Architectes |

### Back-office (Portail HR)

| Document | Objectif | Public |
|----------|----------|--------|
| [**apps/backoffice/README.md**](./apps/backoffice/README.md) | Vue d'ensemble back-office | Tous |
| [**apps/backoffice/SETUP_SUMMARY.md**](./apps/backoffice/SETUP_SUMMARY.md) | Résumé configuration back-office | Administrateurs |

---

## 🔧 Backend (API)

| Document | Objectif | Public |
|----------|----------|--------|
| [**backend/README.md**](./backend/README.md) | Vue d'ensemble backend FastAPI | Tous |
| [**backend/src/README.md**](./backend/src/README.md) | Structure du code source backend | Développeurs |
| [**backend/tests/README.md**](./backend/tests/README.md) | Tests et couverture de test | QA, Développeurs |
| [**backend/tests/e2e/README.md**](./backend/tests/e2e/README.md) | Tests end-to-end | QA |
| [**backend/docs/EMAIL_CONFIGURATION.md**](./backend/docs/EMAIL_CONFIGURATION.md) | Configuration emails (notifications) | Administrateurs |
| [**backend/openapi/README.md**](./backend/openapi/README.md) | Documentation API OpenAPI/Swagger | Développeurs API |
| [**BACKEND_ENDPOINTS_COMPLETE.md**](./BACKEND_ENDPOINTS_COMPLETE.md) | Référence complète des endpoints | Développeurs API |

---

## 🚢 Infrastructure & Déploiement

| Document | Objectif | Public |
|----------|----------|--------|
| [**infra/README.md**](./infra/README.md) | Vue d'ensemble infrastructure | DevOps, Architectes |
| [**infra/docker/README.md**](./infra/docker/README.md) | Configuration Docker | DevOps |
| [**infra/terraform/README.md**](./infra/terraform/README.md) | Infrastructure as Code (Terraform) | DevOps, Cloud |
| [**infra/helm/README.md**](./infra/helm/README.md) | Helm charts Kubernetes | DevOps, K8s |
| [**docs/GUIDE_DEPLOIEMENT.md**](./docs/GUIDE_DEPLOIEMENT.md) | Guide de déploiement complet | DevOps, IT |
| [**docs/HTTPS.md**](./docs/HTTPS.md) | Configuration HTTPS/SSL | Sécurité, DevOps |
| [**docs/NETWORK_ARCHITECTURE.md**](./docs/NETWORK_ARCHITECTURE.md) | Architecture réseau PME | Architectes, IT |

---

## 🔐 Sécurité & Compliance

| Document | Objectif | Public |
|----------|----------|--------|
| [**docs/SECURITY.md**](./docs/SECURITY.md) | Stratégie sécurité globale | Architectes, Audits |
| [**docs/RGPD.md**](./docs/RGPD.md) | Compliance GDPR/CNIL | Légal, DPO |
| [**docs/rgpd/README.md**](./docs/rgpd/README.md) | Index documentation RGPD | Légal |
| [**docs/rgpd/registre.md**](./docs/rgpd/registre.md) | Registre des traitements | DPO, Audit |
| [**docs/rgpd/DPIA_template.md**](./docs/rgpd/DPIA_template.md) | Modèle DPIA (analyse d'impact) | DPO |
| [**docs/threat-model/README.md**](./docs/threat-model/README.md) | Modèle de menaces | Sécurité, Architectes |
| [**docs/SECRET_KEY_GUIDE.md**](./docs/SECRET_KEY_GUIDE.md) | Gestion des clés secrètes | DevOps, Sécurité |

---

## 🌐 Networking & VPN

| Document | Objectif | Public |
|----------|----------|--------|
| [**VPN_QUICK_START.md**](./VPN_QUICK_START.md) | Configuration VPN rapide | IT, Employés |
| [**docs/VPN_SETUP.md**](./docs/VPN_SETUP.md) | Guide VPN détaillé | IT, Administrateurs |

---

## 📋 Outils & Développement

| Document | Objectif | Public |
|----------|----------|--------|
| [**AGENTS.md**](./AGENTS.md) | Setup et procédures développement local | Développeurs |
| [**tools/README.md**](./tools/README.md) | Outils disponibles et utilitaires | Développeurs |
| [**workflows/README.md**](./workflows/README.md) | Workflows GitHub Actions | DevOps, Développeurs |

---

## 📊 Documentation Technique Complète

### Spécifications & Plans

| Document | Contenu |
|----------|---------|
| [**docs/specs/chrona_plan.md**](./docs/specs/chrona_plan.md) | Plan d'implémentation détaillé |
| [**docs/TODO.md**](./docs/TODO.md) | Backlog et tâches prioritaires (source de vérité) |
| [**docs/USER_AND_DEVICE_MANAGEMENT.md**](./docs/USER_AND_DEVICE_MANAGEMENT.md) | Gestion des utilisateurs et appareils |
| [**docs/CAMERA_TROUBLESHOOTING.md**](./docs/CAMERA_TROUBLESHOOTING.md) | Dépannage caméra (QR code scanning) |

### Documentation Complète (Synthèse)

| Document | Sujet |
|----------|-------|
| [**QUICK_START.md**](./QUICK_START.md) | Démarrage global rapide |
| [**KIOSK_ANDROID.md**](./KIOSK_ANDROID.md) | Setup Android pour kiosk |
| [**KIOSK_ACCESS_CONTROL_COMPLETE.md**](./KIOSK_ACCESS_CONTROL_COMPLETE.md) | Contrôle d'accès avancé kiosk |
| [**EMPLOYEE_MOBILE_APK_COMPLETE.md**](./EMPLOYEE_MOBILE_APK_COMPLETE.md) | APK employé complet |
| [**KIOSK_MOBILE_COMPLETE.md**](./KIOSK_MOBILE_COMPLETE.md) | Kiosk mobile complet |
| [**HEARTBEAT_SYSTEM_COMPLETE.md**](./HEARTBEAT_SYSTEM_COMPLETE.md) | Système heartbeat complet |
| [**INTEGRATION_COMPLETE.md**](./INTEGRATION_COMPLETE.md) | Intégration complète système |
| [**PHASE5_COMPLETION.md**](./PHASE5_COMPLETION.md) | Achèvement Phase 5 |

---

## 🎯 Guide par Rôle

### Pour les **Développeurs**

1. [CLAUDE.md](./CLAUDE.md) - Architecture et setup
2. [AGENTS.md](./AGENTS.md) - Procédures développement
3. [backend/README.md](./backend/README.md) - Backend API
4. [apps/mobile/README.md](./apps/mobile/README.md) - App mobile
5. [backend/tests/README.md](./backend/tests/README.md) - Tests

### Pour les **DevOps / IT**

1. [QUICK_START.md](./QUICK_START.md) - Démarrage rapide
2. [docs/GUIDE_DEPLOIEMENT.md](./docs/GUIDE_DEPLOIEMENT.md) - Déploiement
3. [infra/README.md](./infra/README.md) - Infrastructure
4. [apps/kiosk/KIOSK_MODE.md](./apps/kiosk/KIOSK_MODE.md) - Setup kiosk
5. [docs/HTTPS.md](./docs/HTTPS.md) - HTTPS/SSL

### Pour les **Responsables Sécurité**

1. [docs/SECURITY.md](./docs/SECURITY.md) - Stratégie sécurité
2. [docs/threat-model/README.md](./docs/threat-model/README.md) - Menaces
3. [docs/SECRET_KEY_GUIDE.md](./docs/SECRET_KEY_GUIDE.md) - Gestion clés
4. [apps/mobile/SECURITY.md](./apps/mobile/SECURITY.md) - Sécurité mobile

### Pour les **DPO / Légal**

1. [docs/RGPD.md](./docs/RGPD.md) - Vue d'ensemble GDPR
2. [docs/rgpd/README.md](./docs/rgpd/README.md) - Index RGPD
3. [docs/rgpd/DPIA_template.md](./docs/rgpd/DPIA_template.md) - Modèle DPIA
4. [docs/rgpd/registre.md](./docs/rgpd/registre.md) - Registre

### Pour les **Administrateurs**

1. [SETUP_EAS_QUICK_START.md](./SETUP_EAS_QUICK_START.md) - Setup APK
2. [apps/kiosk/KIOSK_MODE.md](./apps/kiosk/KIOSK_MODE.md) - Kiosk
3. [VPN_QUICK_START.md](./VPN_QUICK_START.md) - VPN
4. [backend/docs/EMAIL_CONFIGURATION.md](./backend/docs/EMAIL_CONFIGURATION.md) - Emails

### Pour les **Employés / Utilisateurs Finaux**

1. [apps/mobile/INSTALLATION.md](./apps/mobile/INSTALLATION.md) - Installation app
2. [VPN_QUICK_START.md](./VPN_QUICK_START.md) - Connexion VPN

---

## 🔍 Index par Sujet

### Architecture & Conception

- [CLAUDE.md](./CLAUDE.md) - Architecture globale
- [docs/NETWORK_ARCHITECTURE.md](./docs/NETWORK_ARCHITECTURE.md) - Architecture réseau
- [docs/specs/chrona_plan.md](./docs/specs/chrona_plan.md) - Plan détaillé
- [apps/kiosk-mobile/SUMMARY.md](./apps/kiosk-mobile/SUMMARY.md) - Architecture kiosk

### Authentification & Sécurité

- [backend/src/README.md](./backend/src/README.md) - Implémentation backend
- [apps/mobile/SECURITY.md](./apps/mobile/SECURITY.md) - Sécurité mobile
- [apps/mobile/docs/CERTIFICATE_PINNING.md](./apps/mobile/docs/CERTIFICATE_PINNING.md) - Pinning certificats

### Déploiement & CI/CD

- [docs/GUIDE_DEPLOIEMENT.md](./docs/GUIDE_DEPLOIEMENT.md) - Déploiement complet
- [infra/docker/README.md](./infra/docker/README.md) - Docker
- [infra/terraform/README.md](./infra/terraform/README.md) - Terraform
- [workflows/README.md](./workflows/README.md) - GitHub Actions

### Mobile & APK

- [apps/mobile/README.md](./apps/mobile/README.md) - App mobile
- [apps/mobile/APK_BUILD.md](./apps/mobile/APK_BUILD.md) - Génération APK
- [apps/mobile/INSTALLATION.md](./apps/mobile/INSTALLATION.md) - Installation
- [apps/mobile/EAS_CREDENTIALS_SETUP.md](./apps/mobile/EAS_CREDENTIALS_SETUP.md) - EAS setup

### Kiosk & Hardware

- [apps/kiosk/README.md](./apps/kiosk/README.md) - Kiosk Web
- [apps/kiosk/KIOSK_MODE.md](./apps/kiosk/KIOSK_MODE.md) - Mode kiosk
- [KIOSK_ANDROID.md](./KIOSK_ANDROID.md) - Android kiosk
- [apps/kiosk-mobile/DEPLOYMENT.md](./apps/kiosk-mobile/DEPLOYMENT.md) - Déploiement

### Base de Données & Backend

- [backend/README.md](./backend/README.md) - Backend
- [BACKEND_ENDPOINTS_COMPLETE.md](./BACKEND_ENDPOINTS_COMPLETE.md) - Endpoints API
- [docs/USER_AND_DEVICE_MANAGEMENT.md](./docs/USER_AND_DEVICE_MANAGEMENT.md) - Gestion données

### Compliance & Légal

- [docs/RGPD.md](./docs/RGPD.md) - GDPR overview
- [docs/rgpd/registre.md](./docs/rgpd/registre.md) - Registre traitements
- [docs/rgpd/DPIA_template.md](./docs/rgpd/DPIA_template.md) - DPIA

### Networking & Connectivité

- [docs/NETWORK_ARCHITECTURE.md](./docs/NETWORK_ARCHITECTURE.md) - Réseau
- [VPN_QUICK_START.md](./VPN_QUICK_START.md) - VPN rapide
- [docs/VPN_SETUP.md](./docs/VPN_SETUP.md) - VPN détaillé
- [docs/HTTPS.md](./docs/HTTPS.md) - HTTPS/SSL

---

## 🆘 FAQ & Dépannage

### "Je ne sais pas par où commencer"
→ Allez à [QUICK_START.md](./QUICK_START.md)

### "Je dois générer une APK"
→ Allez à [SETUP_EAS_QUICK_START.md](./SETUP_EAS_QUICK_START.md)

### "Je dois déployer le système complet"
→ Allez à [docs/GUIDE_DEPLOIEMENT.md](./docs/GUIDE_DEPLOIEMENT.md)

### "J'ai des problèmes de caméra/QR code"
→ Allez à [docs/CAMERA_TROUBLESHOOTING.md](./docs/CAMERA_TROUBLESHOOTING.md)

### "Je dois vérifier la conformité GDPR"
→ Allez à [docs/RGPD.md](./docs/RGPD.md)

### "Comment configurer le VPN ?"
→ Allez à [VPN_QUICK_START.md](./VPN_QUICK_START.md)

### "Je ne comprends pas l'architecture"
→ Allez à [CLAUDE.md](./CLAUDE.md)

---

## 📈 Progression de Lecture Recommandée

Pour une compréhension complète du projet, lisez dans cet ordre :

1. **[QUICK_START.md](./QUICK_START.md)** (5 min) - Vue d'ensemble
2. **[CLAUDE.md](./CLAUDE.md)** (10 min) - Architecture
3. **[backend/README.md](./backend/README.md)** (5 min) - Backend
4. **[apps/mobile/README.md](./apps/mobile/README.md)** (5 min) - Mobile
5. **[apps/kiosk/README.md](./apps/kiosk/README.md)** (5 min) - Kiosk
6. **[docs/GUIDE_DEPLOIEMENT.md](./docs/GUIDE_DEPLOIEMENT.md)** (15 min) - Déploiement
7. **[docs/SECURITY.md](./docs/SECURITY.md)** (10 min) - Sécurité
8. **[docs/RGPD.md](./docs/RGPD.md)** (10 min) - Compliance

**Temps total : ~1 heure pour une compréhension complète**

---

## 🔄 Tenue à Jour

Certains documents sont prioritaires et doivent être tenus à jour :

- ✅ **[docs/TODO.md](./docs/TODO.md)** - Source de vérité pour le backlog
- ✅ **[CLAUDE.md](./CLAUDE.md)** - Architecture et commandes essentielles
- ✅ **[QUICK_START.md](./QUICK_START.md)** - Démarrage rapide
- ✅ **[docs/GUIDE_DEPLOIEMENT.md](./docs/GUIDE_DEPLOIEMENT.md)** - Procédures déploiement

---

## 📞 Support & Questions

Pour des questions sur :
- **Architecture** : Consultez [CLAUDE.md](./CLAUDE.md)
- **Développement** : Consultez [AGENTS.md](./AGENTS.md)
- **Déploiement** : Consultez [docs/GUIDE_DEPLOIEMENT.md](./docs/GUIDE_DEPLOIEMENT.md)
- **Sécurité** : Consultez [docs/SECURITY.md](./docs/SECURITY.md)
- **Tâches à faire** : Consultez [docs/TODO.md](./docs/TODO.md)

---

**Last Updated**: 2025-10-27
**Maintainer**: Claude Code
**Version**: 1.0

---

*Ce document est généré automatiquement et sert de référence centrale pour toute la documentation du projet Chrona.*

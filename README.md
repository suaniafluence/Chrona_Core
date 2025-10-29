# Chrona - Système de Pointage Sécurisé

[![CI](https://github.com/suaniafluence/Chrona_Core/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/suaniafluence/Chrona_Core/actions/workflows/ci.yml)
[![Docker Publish](https://github.com/suaniafluence/Chrona_Core/actions/workflows/docker-publish.yml/badge.svg?branch=main)](https://github.com/suaniafluence/Chrona_Core/actions/workflows/docker-publish.yml)

Système de pointage employés avec QR codes éphémères signés (JWT RS256), attestation d'appareil et conformité RGPD.

---

## 🚀 Démarrage Rapide (Installation en 1 Commande)

**Windows (PowerShell):**
```powershell
.\setup-dev.ps1
```

**Ce script fait tout automatiquement:**
- ✅ Génère les clés JWT RS256 et SECRET_KEY
- ✅ Configure les fichiers .env
- ✅ Démarre Backend API + PostgreSQL
- ✅ Applique les migrations
- ✅ Crée un admin (admin@example.com / Passw0rd!)
- ✅ Configure le kiosk avec sa clé API

**Durée:** ~2-3 minutes | **[Voir le guide détaillé](QUICK_START.md)**

---

## 📱 Déploiement des Applications

### Kiosk (Tablette de pointage)
```powershell
.\start-kiosk.ps1
```
Accès: http://localhost:5174

### Back-office (Administration RH)
```powershell
.\start-backoffice.ps1
```
Accès: http://localhost:5173

### Application Mobile (Employés)

**Sur PC:**
```powershell
.\setup-mobile.ps1    # Configuration auto
cd apps/mobile
npm start             # Affiche un QR code
```

**Sur téléphone:**
1. Installer [Expo Go](https://expo.dev/client)
2. Scanner le QR code avec Expo Go

**📱 [Guide d'installation mobile détaillé](apps/mobile/INSTALLATION.md)**

**[📖 Guide complet de déploiement](docs/GUIDE_DEPLOIEMENT.md)**

---

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Guide de démarrage rapide (recommandé)
- **[docs/GUIDE_DEPLOIEMENT.md](docs/GUIDE_DEPLOIEMENT.md)** - Guide complet d'installation
- **[CLAUDE.md](CLAUDE.md)** - Configuration pour développeurs Claude Code
- **[docs/TODO.md](docs/TODO.md)** - Roadmap et tâches
- **[AGENTS.md](AGENTS.md)** - Guide local détaillé
- **[docs/](docs/)** - Documentation complète (RGPD, sécurité, threat-model)

---

## 🐳 Docker & Déploiement

**Prérequis:** Docker Desktop + Python 3.11+

**Déploiement rapide:**
```bash
docker compose up -d --build
```

**Services:**
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Kiosk: `http://localhost:5174`

**Image Docker:**
```bash
docker pull ghcr.io/suaniafluence/chrona-core-backend:latest
```

Voir [docs/GUIDE_DEPLOIEMENT.md](docs/GUIDE_DEPLOIEMENT.md) pour les détails complets.

---

## 🛠️ Développement Local

### Backend (FastAPI + PostgreSQL)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### Tests & Linting

```bash
cd backend
pytest -q                    # Run tests
black --check src tests      # Check formatting
flake8 src tests            # Lint
isort --check-only backend  # Check imports
```

### Frontend Apps (Vite)

```bash
cd apps/backoffice
npm install
npm run dev  # Dev server on :5173

# ou
cd apps/kiosk
npm install
npm run dev  # Dev server on :5174
```

---

## 📋 État du Projet

- ✅ Backend API (FastAPI + PostgreSQL + Alembic)
- ✅ Kiosk tablet app (React + Vite + TypeScript)
- ✅ Back-office HR portal (React + Vite + TypeScript)
- ✅ Mobile app (Expo + React Native + TypeScript)
- ✅ TOTP 2FA authentication system
- ✅ QR code generation & JWT validation
- ✅ RGPD/CNIL compliance
- ✅ Device attestation & anti-replay protection
- ✅ CI/CD pipelines (GitHub Actions)

---

## 🔐 Sécurité

- **JWT:** RS256/ES256 signed ephemeral QR tokens
- **Passwords:** PBKDF2-HMAC-SHA256 (390k iterations)
- **Database:** PostgreSQL + encryption at rest
- **Transport:** TLS 1.2+ enforced
- **Compliance:** GDPR/RGPD compliant

---

## 🤝 Contribution

1. Create feature branch: `git checkout -b feature/description`
2. Make changes and test locally
3. Run: `pytest`, `black`, `flake8`, `isort`
4. Push and create Pull Request
5. CI/CD will validate automatically

---

## 📝 Licence

Propriétaire - Chrona Time Tracking System 2025

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/suaniafluence/Chrona_Core/issues)
- **Documentation:** See `docs/` directory
- **Developer Guide:** [CLAUDE.md](CLAUDE.md)

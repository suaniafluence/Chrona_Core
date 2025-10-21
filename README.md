# Chrona

[![CI](https://github.com/suaniafluence/Chrona_Core/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/suaniafluence/Chrona_Core/actions/workflows/ci.yml)
[![Docker Publish](https://github.com/suaniafluence/Chrona_Core/actions/workflows/docker-publish.yml/badge.svg?branch=main)](https://github.com/suaniafluence/Chrona_Core/actions/workflows/docker-publish.yml)


Voir `AGENTS.md` pour le guide local et `docs/TODO.md` pour la feuille de route.

Image GHCR
- Nom d’image: `ghcr.io/suaniafluence/chrona-core-backend`
- Pull: `docker pull ghcr.io/suaniafluence/chrona-core-backend:latest`
- Run: `docker run -p 8000:8000 ghcr.io/suaniafluence/chrona-core-backend:latest`

---
**Démarrage Avec Docker**
- Prérequis
  - Docker Desktop en état « Running »
  - Python installé pour générer les clés JWT côté hôte

- Générer les clés JWT (une fois)
  - `cd Chrona_Core/backend`
  - `python -m venv .venv`
  - `.venv\Scripts\python -m pip install -r requirements.txt`
  - `.venv\Scripts\python tools\generate_keys.py`
  - Clés générées: `backend/jwt_private_key.pem`, `backend/jwt_public_key.pem`

- Lancer la stack
  - Depuis la racine: `docker compose up -d --build`
  - Services exposés: `db` 5432, `backend` 8000, `kiosk` 5174

- Appliquer les migrations (sur l’hôte)
  - `cd Chrona_Core/backend`
  - PowerShell (session courante): `$env:DATABASE_URL="postgresql+asyncpg://chrona:chrona@localhost:5432/chrona"`
  - Facultatif: `$env:PYTHONPATH=(Get-Location).Path`
  - `.\.venv\Scripts\alembic upgrade head`

- (Optionnel) Seeder un kiosque de test (ID 1)
  - `.\.venv\Scripts\python tools\seed_kiosk.py`
  - Configurez le Kiosk avec `VITE_KIOSK_ID=1`

- Accès et vérifications
  - API santé: `http://localhost:8000/health`
  - Kiosk: `http://localhost:5174` (proxy `/api` → backend)
  - Logs backend: `docker compose logs -f backend`
  - État des services: `docker compose ps`
  - Arrêt/cleanup: `docker compose down -v`

- Script E2E (PowerShell)
  - `pwsh ./backend/tools/e2e-punch.ps1 -Email dev@example.com -Password Passw0rd! -Api http://localhost:8000 -KioskId 1 -DeviceFingerprint e2e-device-001 -PunchType clock_in`

Notes
- Le `docker-compose.yml` monte automatiquement les clés JWT dans le conteneur backend et inclut `http://localhost:5174` dans CORS.
- Un avertissement Passlib/bcrypt peut apparaître dans les logs; il n’empêche pas le fonctionnement de base.
- Le champ `version:` de Compose est obsolète et ignoré par Docker.

**Alternative Podman (facultatif)**
- Démarrer la machine: `podman machine start podman-machine-default`
- Lancer: `podman compose up -d --build`
- Les étapes de migration et de seed sont identiques (côté hôte).

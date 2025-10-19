# Chrona Backend (FastAPI)

Ce module fournit l’API Chrona (gestion des appareils, QR éphémères, pointages, audit). Il utilise FastAPI, SQLModel/SQLAlchemy (async), JWT RS256 et Alembic pour les migrations.

---
**Arborescence**
- `src/` code applicatif (routers, models, services, config)
- `alembic/` migrations DB
- `tools/` utilitaires (`generate_keys.py`, `seed_kiosk.py`)
- `requirements.txt`, `alembic.ini`, `.flake8`, `pyproject.toml`

---
**Prérequis**
- Python 3.11+
- Postgres (via Docker Compose recommandée)
- OpenSSL/cryptography (installé via `requirements.txt` pour la génération de clés)

---
**Installation locale (venv)**
- `cd Chrona_Core/backend`
- `python -m venv .venv`
- `.venv\Scripts\python -m pip install -r requirements.txt`

---
**Clés JWT (RS256)**
- Générer les clés (une seule fois):
  - `.venv\Scripts\python tools\generate_keys.py`
- Par défaut, les clés sont écrites dans `backend/jwt_private_key.pem` et `backend/jwt_public_key.pem`.
- Variables prises en charge:
  - `JWT_PRIVATE_KEY_PATH` (par défaut: `backend/jwt_private_key.pem`)
  - `JWT_PUBLIC_KEY_PATH` (par défaut: `backend/jwt_public_key.pem`)
  - `ALGORITHM` (`RS256` recommandé, `HS256` legacy)

---
**Variables d’environnement (exemples)**
- `DATABASE_URL=postgresql+asyncpg://chrona:chrona@localhost:5432/chrona`
- CORS:
  - `ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174`
  - `ALLOW_CREDENTIALS=false`
  - `ALLOWED_METHODS=*`
  - `ALLOWED_HEADERS=*`
- Sécurité:
  - `SECRET_KEY=change-me` (utile en HS256 ou pour d’autres usages)
  - `ACCESS_TOKEN_EXPIRE_MINUTES=60`
  - `EPHEMERAL_TOKEN_EXPIRE_SECONDS=30`
  - `BCRYPT_ROUNDS=12`

---
**Lancement local (Uvicorn + SQLite ou Postgres)**
- Avec SQLite (par défaut):
  - `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`
- Avec Postgres:
  - PowerShell: `$env:DATABASE_URL="postgresql+asyncpg://chrona:chrona@localhost:5432/chrona"`
  - `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`

---
**Docker Compose (recommandé)**
- Depuis la racine (`Chrona_Core/`):
  - `docker compose up -d --build`
- Le service `backend` monte automatiquement les clés JWT via `docker-compose.yml`.
- Postgres écoute sur `localhost:5432`, API sur `localhost:8000`.

---
**Migrations Alembic**
- Depuis `Chrona_Core/backend` (venv activé):
  - PowerShell (session courante): `$env:DATABASE_URL="postgresql+asyncpg://chrona:chrona@localhost:5432/chrona"`
  - Facultatif (résolution imports): `$env:PYTHONPATH=(Get-Location).Path`
  - `.venv\Scripts\alembic upgrade head`
- Générer une migration:
  - `.venv\Scripts\alembic revision -m "message" --autogenerate`

---
**Tests & Lint**
- Tests: `pytest -q`
- Lint/format (si souhaité):
  - `black src tests`
  - `isort .`
  - `flake8 src tests`

---
**Endpoints principaux**
- Santé: `GET /health`
- Racine: `GET /`
- Auth:
  - `POST /auth/register` (body JSON: `{ "email", "password" }`)
  - `POST /auth/token` (form-encoded: `username`, `password`)
  - `GET /auth/me` (header `Authorization: Bearer <token>`)
- Appareils (`Authorization: Bearer <token>`):
  - `POST /devices/register`
  - `GET /devices/me`
  - `POST /devices/{id}/revoke`
- Kiosks (admin): voir routes `admin` si activées
- Pointage (QR):
  - `POST /punch/request-token` (auth requis)
  - `POST /punch/validate` (appelé par la borne, public)

---
**Exemples cURL**
- Inscription: `curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"email":"dev@example.com","password":"Passw0rd!"}'`
- Token: `curl -X POST http://localhost:8000/auth/token -H "Content-Type: application/x-www-form-urlencoded" -d 'username=dev@example.com&password=Passw0rd!'`
- Me: `curl http://localhost:8000/auth/me -H "Authorization: Bearer <token>"`

---
**Notes**
- Les clés privées ne doivent jamais être commit (`.gitignore` ignore `jwt_private_key.pem` et `*.pem`).
- La base Postgres nécessite l’exécution des migrations avant usage.
- Les dates sont gérées en UTC (naïf) pour s’aligner avec `TIMESTAMP WITHOUT TIME ZONE`.


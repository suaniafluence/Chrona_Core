# Repository Guidelines

## Project Structure & Modules
- Répertoire principal: `Chrona_Core/` avec `apps/`, `backend/`, `docs/`, `infra/`, `tools/`, `workflows/`.
- Backend: code sous `backend/src/`, tests sous `backend/tests/` (consultez leurs README).
- Apps: `apps/backoffice/`, `apps/kiosk/`, `apps/mobile/` contiennent chacun leur README et config.
- Lisez chaque `README.md` local avant de coder ou configurer l’environnement.

## Build, Test, and Dev Commands
- Se placer dans le module visé, ex.: `cd Chrona_Core/backend` ou `cd Chrona_Core/apps/backoffice`.
- Node/TS (si présent): `npm ci`, `npm run dev`, `npm run build`, `npm test` (voir `package.json`).
- Python (si présent): créer un venv puis `pip install -r requirements.txt`; tests via `pytest -q`.
- Exemples: `cd Chrona_Core/backend && pytest -q` | `cd Chrona_Core/apps/kiosk && npm run dev`.

## Backend Quickstart (FastAPI)
- Installer dépendances (Windows):
  - `cd Chrona_Core/backend`
  - `python -m venv .venv && .venv\\Scripts\\activate`
  - `pip install -r requirements.txt` (ou, à défaut: `pip install fastapi uvicorn pytest black isort flake8`)
- Lancer l’API en local:
  - `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000` (adaptez le module si différent)
- Exécuter les tests:
  - `pytest -q` (depuis `Chrona_Core/backend`)
- Lint/format:
  - `black src tests` ; `isort .` ; `flake8 src tests`
- Variables d’environnement (exemples):
  - `DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/chrona`
  - CORS: `ALLOWED_ORIGINS=http://localhost:3000`, `ALLOW_CREDENTIALS=false`, `ALLOWED_METHODS=*`, `ALLOWED_HEADERS=*`
  - Secrets: `SECRET_KEY=change-me`

## Docker Compose
- Depuis `Chrona_Core/`:
  - `docker compose up -d --build`
  - Backend: http://localhost:8000 (FastAPI)
  - Postgres: `chrona:chrona@localhost:5432/chrona`
- Variables (overrides via `.env`): `ALLOWED_ORIGINS`, `ALLOW_CREDENTIALS`, `ALLOWED_METHODS`, `ALLOWED_HEADERS`, `DATABASE_URL`.
- Arrêt/Logs: `docker compose logs -f backend` ; `docker compose down -v`.

## Frontends CORS / API
- Backoffice/Kiosk: créer `.env` depuis `.env.example` et définir `VITE_API_URL` (ex.: `http://localhost:8000`).
- Mobile (émulateur Android): utiliser `API_BASE_URL=http://10.0.2.2:8000`.
- Pour cookies/headers sensibles: côté backend `ALLOW_CREDENTIALS=true`; côté client `credentials: 'include'`.

## Vite Dev Proxy
- Un `vite.config.ts` est fourni pour `apps/backoffice` (port 5173) et `apps/kiosk` (port 5174).
- Il redirige les appels `/api` vers `VITE_API_URL` (par défaut `http://localhost:8000`).
- Exemple d’usage côté front:
  - `fetch('/api/health')` → proxie vers `http://localhost:8000/health`.
- Lancement via Docker (si `package.json` présent): `docker compose up backoffice kiosk`.

## Source de Vérité
- Backlog et priorités: `docs/TODO.md` fait foi (tenir à jour en premier).
- Ce guide (`AGENTS.md`) sert de référence locale pour le setup et les pratiques.
- Ne créez pas d’issues externes sans répliquer les décisions dans `docs/TODO.md`.

## Coding Style & Naming Conventions
- Python: indent 4 espaces; outils suggérés `black`, `isort`, `flake8` si configurés.
- JS/TS: indent 2 espaces; `eslint` + `prettier` si présents.
- Nommage: dossiers `kebab-case`, fichiers Python `snake_case.py`, classes/composants `PascalCase`.
- Environnements: ne pas committer de secrets; fournir `.env.example` et utiliser `.env` local.

## Testing Guidelines
- Découverte: Python sous `backend/tests/test_*.py`; JS/TS sous `__tests__/` ou `*.spec|test.ts`.
- Cible: ~80% sur le code modifié; inclure cas limites, erreurs, et chemins d’échec.
- Exécuter les tests et lint localement avant toute PR.

## Commit & Pull Request Guidelines
- Commits: style Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`).
- PR: portée réduite, description claire, issues liées, captures/Logs si UX/CLI impactés.
- CI: la build, les tests et le lint doivent être verts avant merge.

## Security & Configuration Tips
- Ne jamais committer `.env*`/clés; rotation immédiate si fuite.
- Valider les entrées et journaliser les erreurs côté backend/apps.
- Documenter tout paramètre par défaut dans les README de module.

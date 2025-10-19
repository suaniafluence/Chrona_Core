# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

Chrona is a secure attendance and authentication system built with a monorepo structure. The system uses signed QR codes, device attestation, and PostgreSQL persistence for security-focused time tracking.

**Key architectural components:**
- **Backend** (`backend/`): FastAPI-based async REST API with SQLModel/SQLAlchemy ORM, JWT authentication, and role-based access control (admin/user)
- **Frontend Apps** (`apps/`):
  - `mobile/`: Employee onboarding, device attestation, and secure time tracking
  - `kiosk/`: Tablet kiosk mode for ephemeral QR code generation and display
  - `backoffice/`: HR portal for attendance management and compliance reporting
- **Database**: PostgreSQL (production) or SQLite (local dev) via async drivers (asyncpg/aiosqlite)
- **Alembic migrations**: Database schema versioning under `backend/alembic/`

**Backend structure:**
- `backend/src/main.py`: FastAPI app entry point with CORS middleware
- `backend/src/db.py`: Async engine setup with lifespan context manager; auto-creates SQLite tables on startup
- `backend/src/routers/`: API endpoints (`auth.py`, `admin.py`)
- `backend/src/models/`: SQLModel entities (e.g., `user.py`)
- `backend/src/security.py`: Password hashing, JWT token generation/validation
- `backend/src/schemas.py`: Pydantic request/response models

## Essential Commands

### Backend (FastAPI + Python)

**Setup** (from `backend/`):
```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Unix
pip install -r requirements.txt
```

**Run dev server**:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Testing**:
```bash
pytest -q                    # Run all tests
pytest -q tests/test_auth.py # Single test file
pytest -v                    # Verbose output
```

**Linting/Formatting**:
```bash
black src tests      # Format code
isort .              # Sort imports (profile: black)
flake8 src tests     # Lint (max line: 88)
```

**Database migrations** (from `backend/`):
```bash
alembic upgrade head                           # Apply migrations
alembic revision -m "description" --autogenerate # Create migration
```

### Docker Compose

**From repository root**:
```bash
docker compose up -d --build    # Start all services
docker compose logs -f backend  # Follow backend logs
docker compose down -v          # Stop and remove volumes
```

Services:
- Backend API: http://localhost:8000
- PostgreSQL: `postgres://chrona:chrona@localhost:5432/chrona`

### Frontend Apps (Vite)

**Setup** (from `apps/backoffice/` or `apps/kiosk/`):
```bash
npm ci
cp .env.example .env  # Configure VITE_API_URL
npm run dev           # Dev server (backoffice: 5173, kiosk: 5174)
npm run build         # Production build
npm test              # Run tests
```

Vite dev proxy: `/api` routes proxy to `VITE_API_URL` (default: `http://localhost:8000`)

## Authentication Flow

**Register**: `POST /auth/register` with `{ "email": "...", "password": "..." }`

**Login**: `POST /auth/token` (form-urlencoded) with `username=<email>&password=<password>` → returns JWT access token

**Authenticated requests**: Add header `Authorization: Bearer <token>`

**Quick test script**: `backend/tools/dev-auth.ps1` (PowerShell) chains register → token → me

**Admin endpoints**: Require `role=admin` in JWT. Promote user in DB or use `POST /admin/users` with `{ "email", "password", "role" }` to create admin users.

## Environment Configuration

**Backend** (`.env` in `backend/` or root):
- `DATABASE_URL`: `postgresql+asyncpg://user:pass@host:5432/dbname` (Postgres) or `sqlite+aiosqlite:///./app.db` (SQLite)
- `SECRET_KEY`: JWT signing secret (change in production!)
- `ALLOWED_ORIGINS`: Comma-separated CORS origins (e.g., `http://localhost:3000,http://localhost:5173`)
- `ALLOW_CREDENTIALS`: `true` or `false` (for cookies/auth headers)
- `ALLOWED_METHODS`: CORS methods (default: `*`)
- `ALLOWED_HEADERS`: CORS headers (default: `*`)

**Frontend** (`.env` in `apps/*/`):
- `VITE_API_URL`: Backend API base URL (e.g., `http://localhost:8000`)
- Mobile emulator: Use `http://10.0.2.2:8000` for Android emulator

## Source of Truth

`docs/TODO.md` is the authoritative backlog. Update it before external issue trackers. Consult `AGENTS.md` for detailed setup procedures.

## Code Style

- **Python**: 4-space indent, `black` formatter (line length: 88), `isort` with `profile="black"`, `flake8` linting
- **JS/TS**: 2-space indent, ESLint + Prettier (if configured)
- **Naming**:
  - Folders: `kebab-case`
  - Python files: `snake_case.py`
  - Classes/Components: `PascalCase`
- **Commits**: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`)
- **Tests**: Aim for ~80% coverage on modified code; place under `backend/tests/test_*.py` or `apps/*/__tests__/`

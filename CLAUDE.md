# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Objective & Scope

**Purpose**: Employee time tracking system using BYOD mobile devices with ephemeral signed QR codes scanned by tablet kiosks.

**Key characteristics**:
- Target: 25 employees (no LDAP directory)
- Connectivity: Online only
- Compliance: GDPR/CNIL compliant, no biometric data
- Security: Signed QR codes with RS256, device attestation, anti-replay protection

**Threat Model**: The system protects against (T1-T8):
- QR code replay attacks
- Compromised mobile devices
- Network interception (MitM)
- Unauthorized device usage
- Kiosk tampering
- Backend compromise

## Architecture Overview

Chrona is a secure attendance and authentication system built with a monorepo structure. The system uses signed QR codes, device attestation, and PostgreSQL persistence for security-focused time tracking.

**Core security features**:
- **JWT RS256 signatures**: Ephemeral QR codes with nonce, jti (single-use), and device binding
- **Device attestation**: Level B onboarding (HR code + OTP + device attestation)
- **Anti-capture**: Mobile app protections against screenshots and screen recording
- **Encrypted database**: PostgreSQL with encryption at rest
- **Immutable audit logs**: Security event tracking for compliance

**Key architectural components:**
- **Backend** (`backend/`): FastAPI Python with RS256 JWT signing, secure endpoints, device validation
- **Mobile App** (`apps/mobile/`): Native or cross-platform with:
  - QR code signing (JWT RS256 with ephemeral tokens)
  - Device attestation (secure element integration)
  - Anti-capture protections (screenshot/recording prevention)
- **Kiosk Tablet** (`apps/kiosk/`): Locked-down tablet with:
  - Kiosk mode (restricted UI, no USB access)
  - QR code scanning and validation
  - Offline resilience for temporary disconnections
- **Back-office** (`apps/backoffice/`): HR portal for attendance management, reporting, and compliance
- **Database**: PostgreSQL with encryption (production) or SQLite (local dev) via async drivers (asyncpg/aiosqlite)
- **Infrastructure**: Docker containers, CI/CD pipelines, TLS 1.2+ enforced
- **Alembic migrations**: Database schema versioning under `backend/alembic/`

**Backend structure:**
- `backend/src/main.py`: FastAPI app entry point with CORS middleware
- `backend/src/db.py`: Async engine setup with lifespan context manager; auto-creates SQLite tables on startup
- `backend/src/routers/`: API endpoints (`auth.py`, `admin.py`)
- `backend/src/models/`: SQLModel entities (e.g., `user.py`)
- `backend/src/security.py`: Password hashing (bcrypt_sha256), JWT token generation/validation
- `backend/src/core/security.py`: Alternative PBKDF2-HMAC SHA-256 password hashing (390k iterations)
- `backend/src/schemas.py`: Pydantic request/response models

**Security Implementation:**
The backend has two password hashing implementations:
- `backend/src/security.py`: Uses `passlib.hash.bcrypt_sha256` with 72-byte truncation for bcrypt compatibility
- `backend/src/core/security.py`: Uses PBKDF2-HMAC with SHA-256 (390,000 iterations) for modern security without bcrypt limitations

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
pytest                       # Run all tests (configured via pytest.ini)
pytest tests/test_auth.py    # Single test file
pytest -v                    # Verbose output
pytest -q --cov=src --cov-report=xml  # Coverage report (CI mode)
```

Pytest is configured in `pytest.ini` with `pythonpath = .` and `testpaths = tests`.

**Linting/Formatting**:
```bash
black src tests              # Format code (line length: 88)
black --check src tests      # Check formatting without changes
isort .                      # Sort imports (profile: black)
isort --profile black --check-only backend  # Check without changes
flake8 src tests             # Lint (max line: 88, configured for black)
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
docker build -t chrona-backend:ci ./backend  # Build backend image only
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

## Business Flow: Employee Time Tracking

### Onboarding (Level B Security)

Employees register their device through a secure three-step process:

1. **HR Code Entry**: Employee enters unique code provided by HR
2. **OTP Verification**: One-time password sent via SMS/email
3. **Device Attestation**: Mobile app registers device fingerprint with backend

This creates a trusted device binding that prevents unauthorized device usage.

### Time Tracking Flow

**Clock-in/Clock-out sequence**:

1. **Mobile generates ephemeral QR code**:
   - JWT signed with RS256 algorithm
   - Contains: employee ID, timestamp, nonce (anti-replay), jti (single-use token ID), device fingerprint
   - Short expiration (15-30 seconds)

2. **Employee scans QR at kiosk tablet**:
   - Kiosk validates JWT signature using backend public key
   - Backend verifies:
     - Signature validity (RS256)
     - Nonce uniqueness (prevent replay)
     - Token not already used (jti check)
     - Device is registered and not revoked
     - Kiosk is authorized
     - Timestamp within acceptable window

3. **Backend records attendance event**:
   - Stores timestamp, employee, kiosk location, device ID
   - Creates immutable audit log entry
   - Returns confirmation to both mobile and kiosk (dual-channel validation)

**Security validations**:
- Nonce prevents replay attacks
- Single-use jti prevents token reuse
- Device binding prevents unauthorized phones
- Short expiration limits attack window
- Dual-channel confirmation ensures both parties receive confirmation

## Authentication Flow

**Register**: `POST /auth/register` with `{ "email": "...", "password": "..." }`

**Login**: `POST /auth/token` (form-urlencoded) with `username=<email>&password=<password>` → returns JWT access token

**Authenticated requests**: Add header `Authorization: Bearer <token>`

**Quick test script**: `backend/tools/dev-auth.ps1` (PowerShell) chains register → token → me
```powershell
pwsh ./backend/tools/dev-auth.ps1 -Email dev@example.com -Password Passw0rd! -Api http://localhost:8000
```

**Admin endpoints**: Require `role=admin` in JWT. Promote user in DB or use `POST /admin/users` with `{ "email", "password", "role" }` to create admin users.

**Role management**: `PATCH /admin/users/{id}/role` with `{ "role": "admin" }` to promote users.

## Password Security

**Current implementation** (`backend/src/security.py`):
- Uses `passlib.hash.bcrypt_sha256` for hashing/verification
- Applies 72-byte UTF-8 truncation to handle bcrypt's inherent limit
- Truncation is consistent between hashing and verification
- Long passwords (>72 bytes) are supported safely

**Alternative implementation** (`backend/src/core/security.py`):
- PBKDF2-HMAC with SHA-256 (390,000 iterations)
- No password length limitations
- Base64-encoded salt and hash storage
- Format: `pbkdf2_sha256$<salt_b64>$<hash_b64>`

**Recommendations**:
- Use passphrases ≥ 12 characters
- Never log or echo passwords
- Both implementations use constant-time comparison for verification

## Environment Configuration

**Backend** (`.env` in `backend/` or root):
- `DATABASE_URL`: `postgresql+asyncpg://user:pass@host:5432/dbname` (Postgres) or `sqlite+aiosqlite:///./app.db` (SQLite)
- `SECRET_KEY`: JWT signing secret (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 60)
- `ALLOWED_ORIGINS`: Comma-separated CORS origins (e.g., `http://localhost:3000,http://localhost:5173`)
- `ALLOW_CREDENTIALS`: `true` or `false` (for cookies/auth headers)
- `ALLOWED_METHODS`: CORS methods (default: `*`)
- `ALLOWED_HEADERS`: CORS headers (default: `*`)

**Frontend** (`.env` in `apps/*/`):
- `VITE_API_URL`: Backend API base URL (e.g., `http://localhost:8000`)
- Mobile emulator: Use `http://10.0.2.2:8000` for Android emulator

## CI/CD Pipeline with Verifiable Artifacts

The GitHub Actions CI workflow (`.github/workflows/ci.yml`) runs on push to `main` and `ci/**` branches with comprehensive security and quality checks:

**Backend tests & lint**:
- Python 3.11 with pip cache
- Runs `pytest -q --cov=src --cov-report=xml`
- Uploads coverage to Codecov
- Checks formatting with `black --check`
- Validates import sorting with `isort --profile black --check-only`
- Lints with `flake8`

**Docker build**: Verifies backend image builds successfully with image signing

**Frontend checks**: Matrix build for `backoffice` and `kiosk` apps (if `package.json` exists)

**Security & quality gates** (planned/in-progress):
- **SAST**: Static analysis security testing
- **SBOM**: Software Bill of Materials generation
- **E2E tests**: End-to-end testing with Playwright/Cypress
- **Smoke tests**: Post-deployment validation
- **Metrics monitoring**: Performance and security metrics dashboards

**Verifiable artifacts**: Each CI/CD step generates artifacts:
- Test reports (JUnit XML, coverage)
- Linting reports
- Security scan results
- Build logs
- Docker image signatures
- Dashboard exports (PDF/JSON)
- E2E test recordings (video/screenshots)

**Badges**: CI status, Docker Publish, and Codecov coverage displayed in README.md

## GDPR Compliance & Data Protection

Chrona is designed to be GDPR/CNIL compliant from the ground up:

**Data minimization**:
- Only collect essential data: employee ID, timestamps, device fingerprint, kiosk location
- No biometric data collection
- No unnecessary personal information

**Data subject rights** (DSR):
- Right to access: Employees can request their attendance records
- Right to erasure: Data deletion upon employee departure
- Right to rectification: Correction of erroneous records
- Right to portability: Export data in machine-readable format

**Privacy by design**:
- Encryption at rest (PostgreSQL)
- Encryption in transit (TLS 1.2+)
- Access controls (role-based permissions)
- Immutable audit logs for accountability

**Documentation requirements**:
- GDPR registry maintained in `docs/rgpd/`
- Data processing records
- Privacy policy for employees
- Consent management (device registration)

**Incident response**:
- Device revocation procedures
- Key rotation mechanisms
- Backup and restore procedures
- Immutable security logs for forensics

Consult `docs/rgpd/` for detailed GDPR documentation and `docs/threat-model/` for security threat analysis.

## Reversibility & Incident Management

**Device revocation**:
- Admin can revoke compromised devices via back-office
- Revoked devices cannot generate valid QR codes
- Immediate effect (no grace period)

**Key rotation**:
- JWT signing keys can be rotated without downtime
- Old tokens remain valid until expiration
- New tokens use new keys automatically

**Backup & restore**:
- PostgreSQL daily backups
- Point-in-time recovery capability
- Encrypted backup storage
- Tested restore procedures

**Security audit logs**:
- Immutable append-only logs
- Track all authentication attempts
- Record all attendance events
- Compliance reporting capabilities

## Development Roadmap

Implementation follows this sequence:

1. **Backend** → Secure API foundation, JWT signing, database schema
2. **Kiosk** → Tablet UI for QR scanning and validation
3. **Mobile** → Employee app with QR generation and device attestation
4. **CI/CD** → Automated testing, security scanning, deployment
5. **Back-office** → HR portal for management and reporting

## Deliverables & Documentation

**Technical deliverables**:
- Versioned specifications in `docs/`
- OpenAPI/Swagger documentation (auto-generated from FastAPI)
- E2E test scripts under `tests/e2e/`
- Security dashboards and metrics
- GDPR registry and compliance documents

**References**:
- `docs/TODO.md`: Authoritative backlog and task tracking
- `docs/specs/chrona_plan.md`: Detailed implementation plan
- `docs/threat-model/`: Security threat analysis
- `docs/rgpd/`: GDPR compliance documentation
- `AGENTS.md`: Local development setup and procedures

## Source of Truth

`docs/TODO.md` is the authoritative backlog. Update it before external issue trackers. Consult `AGENTS.md` for detailed setup procedures and local development guidelines.

## Code Style

- **Python**: 4-space indent, `black` formatter (line length: 88), `isort` with `profile="black"`, `flake8` linting
- **JS/TS**: 2-space indent, ESLint + Prettier (if configured)
- **Naming**:
  - Folders: `kebab-case`
  - Python files: `snake_case.py`
  - Classes/Components: `PascalCase`
- **Commits**: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `ci:`)
- **Tests**: Aim for ~80% coverage on modified code; place under `backend/tests/test_*.py` or `apps/*/__tests__/`
- **Security**: Never commit secrets, API keys, or credentials; use `.env` files (gitignored)

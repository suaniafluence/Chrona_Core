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

1. **Mobile requests ephemeral QR token**:
   - Mobile app calls `POST /punch/request-token` with authenticated user + device_id
   - Backend generates JWT signed with RS256 (private key stored securely)
   - JWT payload contains: `employee_id`, `device_id`, `nonce` (random), `jti` (unique ID), `iat`, `exp` (15-30s), `kiosk_scope`
   - Backend stores nonce and jti in tracking table/cache (Redis) with TTL
   - Backend returns JWT token to mobile

2. **Mobile displays QR code**:
   - Mobile receives JWT string from backend
   - Mobile generates QR code from JWT string (visual representation only)
   - QR code displayed on screen for employee to scan at kiosk
   - Short expiration (15-30 seconds) limits attack window

3. **Kiosk scans and validates QR code**:
   - Kiosk scans QR code, extracts JWT string
   - Kiosk sends JWT to backend via `POST /punch/validate` with `kiosk_id`
   - Backend verifies:
     - JWT signature validity (RS256 with public key)
     - Token not expired (`exp` claim)
     - Nonce uniqueness (check against tracking table, mark as used)
     - JTI not already used (single-use enforcement)
     - Device is registered and not revoked
     - Kiosk is authorized (kiosk_id in whitelist)
   - Backend atomically marks nonce/jti as used to prevent race conditions

4. **Backend records attendance event**:
   - Creates record in `punches` table: timestamp, employee_id, device_id, kiosk_id, punch_type (in/out)
   - Creates immutable audit log entry in `audit_logs` table
   - Returns success confirmation to kiosk
   - Optionally notifies mobile via push notification (dual-channel confirmation)

**Security validations**:
- RS256 signature: Private key never leaves backend, public key can be distributed to kiosks
- Nonce prevents replay attacks (each token has unique random value)
- Single-use jti prevents token reuse (marked as consumed after first validation)
- Device binding prevents unauthorized phones (device_id checked against registered devices)
- Short expiration (15-30s) limits attack window
- Kiosk whitelist prevents rogue scanning devices
- Atomic nonce/jti marking prevents race conditions

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

## Database Schema

The PostgreSQL database uses the following key tables:

### Core Tables

**`users`** - Employee accounts
- `id`: Primary key (integer)
- `email`: Unique email address (indexed)
- `hashed_password`: bcrypt_sha256 hash
- `role`: User role (user/admin, indexed)
- `created_at`: Account creation timestamp

**`devices`** - Registered employee devices
- `id`: Primary key (integer)
- `user_id`: Foreign key to users
- `device_fingerprint`: Unique device identifier (hashed)
- `device_name`: Human-readable name (e.g., "iPhone 13")
- `attestation_data`: JSON blob with SafetyNet/DeviceCheck data
- `registered_at`: Device registration timestamp
- `last_seen_at`: Last activity timestamp
- `is_revoked`: Boolean flag for revoked devices

**`kiosks`** - Authorized kiosk tablets
- `id`: Primary key (integer)
- `kiosk_name`: Unique identifier (e.g., "Entrance-Floor1")
- `location`: Physical location description
- `device_fingerprint`: Kiosk hardware identifier
- `public_key`: Optional RS256 public key for validation
- `is_active`: Boolean flag
- `created_at`: Registration timestamp

**`punches`** - Attendance events (clock-in/out)
- `id`: Primary key (integer)
- `user_id`: Foreign key to users
- `device_id`: Foreign key to devices
- `kiosk_id`: Foreign key to kiosks
- `punch_type`: Enum ('clock_in', 'clock_out')
- `punched_at`: Timestamp of the punch (indexed)
- `jwt_jti`: JTI from validated JWT (for traceability)
- `created_at`: Record creation timestamp

**`token_tracking`** - Nonce and JTI single-use enforcement
- `jti`: Unique token ID (primary key, string)
- `nonce`: Random nonce value (indexed)
- `user_id`: Foreign key to users
- `device_id`: Foreign key to devices
- `issued_at`: Token issue timestamp
- `expires_at`: Token expiration (indexed for cleanup)
- `consumed_at`: Timestamp when token was used (null if unused)
- `consumed_by_kiosk_id`: Foreign key to kiosks (null if unused)

**`audit_logs`** - Immutable security audit trail
- `id`: Primary key (integer, append-only)
- `event_type`: Type of event (e.g., 'punch_validated', 'device_revoked', 'login_failed')
- `user_id`: Foreign key to users (nullable)
- `device_id`: Foreign key to devices (nullable)
- `kiosk_id`: Foreign key to kiosks (nullable)
- `event_data`: JSON blob with event details
- `ip_address`: Source IP address
- `user_agent`: Client user agent
- `created_at`: Event timestamp (indexed)

### Security Notes
- Use PostgreSQL `pgcrypto` extension for column-level encryption of sensitive fields
- Implement row-level security (RLS) policies for multi-tenant isolation
- Token tracking table should have automatic cleanup job (delete expired entries after grace period)
- Audit logs should be write-once (no updates/deletes) with database triggers

## API Endpoints

### Authentication Endpoints (`/auth`)

**`POST /auth/register`** - Register new user account
- Body: `{ "email": "user@example.com", "password": "..." }`
- Returns: `UserRead` with user details
- Status: 201 Created

**`POST /auth/token`** - Login and obtain JWT access token
- Body: Form-urlencoded `username=<email>&password=<password>`
- Returns: `{ "access_token": "...", "token_type": "bearer" }`
- Status: 200 OK

**`GET /auth/me`** - Get current authenticated user
- Headers: `Authorization: Bearer <token>`
- Returns: `UserRead` with user details
- Status: 200 OK

### Device Management Endpoints (`/devices`)

**`POST /devices/register`** - Register new device for authenticated user
- Headers: `Authorization: Bearer <token>`
- Body: `{ "device_fingerprint": "...", "device_name": "...", "attestation_data": {...} }`
- Returns: Device registration confirmation
- Status: 201 Created

**`GET /devices/me`** - List authenticated user's registered devices
- Headers: `Authorization: Bearer <token>`
- Returns: List of devices
- Status: 200 OK

**`POST /devices/{device_id}/revoke`** - Revoke a device (admin or owner)
- Headers: `Authorization: Bearer <token>`
- Returns: Confirmation
- Status: 200 OK

### Punch (Time Tracking) Endpoints (`/punch`)

**`POST /punch/request-token`** - Request ephemeral QR token
- Headers: `Authorization: Bearer <token>`
- Body: `{ "device_id": 123 }`
- Returns: `{ "qr_token": "<JWT-string>", "expires_in": 30 }`
- Status: 200 OK
- Token payload: `{ "sub": user_id, "device_id": ..., "nonce": "...", "jti": "...", "exp": ..., "iat": ... }`

**`POST /punch/validate`** - Validate QR token and record punch
- Body: `{ "qr_token": "<JWT-string>", "kiosk_id": 5, "punch_type": "clock_in" }`
- Returns: `{ "success": true, "punch_id": 123, "punched_at": "..." }`
- Status: 200 OK
- Validates signature, nonce, jti, device, kiosk authorization
- Creates punch record and audit log

**`GET /punch/history`** - Get punch history for authenticated user
- Headers: `Authorization: Bearer <token>`
- Query params: `?from=<date>&to=<date>&limit=50`
- Returns: List of punch records
- Status: 200 OK

### Admin Endpoints (`/admin`)

**`POST /admin/users`** - Create user with specific role (admin only)
- Headers: `Authorization: Bearer <token>` (admin role required)
- Body: `{ "email": "...", "password": "...", "role": "admin" }`
- Returns: `UserRead`
- Status: 201 Created

**`PATCH /admin/users/{user_id}/role`** - Change user role (admin only)
- Headers: `Authorization: Bearer <token>` (admin role required)
- Body: `{ "role": "admin" }`
- Returns: Updated `UserRead`
- Status: 200 OK

**`GET /admin/devices`** - List all devices (admin only)
- Headers: `Authorization: Bearer <token>` (admin role required)
- Query params: `?user_id=<id>&is_revoked=<bool>`
- Returns: List of all devices
- Status: 200 OK

**`POST /admin/devices/{device_id}/revoke`** - Revoke any device (admin only)
- Headers: `Authorization: Bearer <token>` (admin role required)
- Returns: Confirmation
- Status: 200 OK

**`GET /admin/kiosks`** - List all kiosks (admin only)
- Headers: `Authorization: Bearer <token>` (admin role required)
- Returns: List of kiosks
- Status: 200 OK

**`POST /admin/kiosks`** - Register new kiosk (admin only)
- Headers: `Authorization: Bearer <token>` (admin role required)
- Body: `{ "kiosk_name": "...", "location": "...", "device_fingerprint": "..." }`
- Returns: Kiosk details
- Status: 201 Created

**`GET /admin/audit-logs`** - Query audit logs (admin only)
- Headers: `Authorization: Bearer <token>` (admin role required)
- Query params: `?event_type=<type>&user_id=<id>&from=<date>&to=<date>`
- Returns: List of audit log entries
- Status: 200 OK

**`GET /admin/reports/attendance`** - Generate attendance report (admin only)
- Headers: `Authorization: Bearer <token>` (admin role required)
- Query params: `?from=<date>&to=<date>&user_id=<id>&format=json|csv|pdf`
- Returns: Attendance report
- Status: 200 OK

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

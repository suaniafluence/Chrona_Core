import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import db_health, lifespan
from .routers.admin import router as admin_router
from .routers.auth import router as auth_router
from .routers.devices import router as devices_router
from .routers.onboarding import router as onboarding_router
from .routers.punch import router as punch_router

load_dotenv()


def _csv_list(value: str, default: List[str]) -> List[str]:
    if not value:
        return default
    items = [v.strip() for v in value.split(",") if v.strip()]
    return items or default


def _get_allowed_origins() -> List[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
    items = _csv_list(raw, ["http://localhost:3000"])
    # Support wildcard via "*"
    if any(o == "*" for o in items):
        return ["*"]
    return items


def _get_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


app = FastAPI(
    title="Chrona - Time Tracking API",
    description="""
## Chrona Time Tracking System

Secure time tracking system with QR code-based punch validation.

### Features

* **Device Management**: Register and manage employee devices
* **QR Token Generation**: Generate ephemeral JWT tokens (30s expiration)
* **Punch Validation**: Validate QR codes with replay attack protection
* **Admin Dashboard**: Manage devices, kiosks, and audit logs
* **Security**: RS256 JWT, nonce/jti tracking, device attestation

### Authentication

Use `/auth/token` to obtain a JWT bearer token, then include it in requests:

```
Authorization: Bearer <your_token>
```

### Security Features

- **RS256 JWT**: Asymmetric encryption for tokens
- **Replay Protection**: Single-use tokens with nonce/jti tracking
- **Device Revocation**: Instantly revoke compromised devices
- **Audit Logging**: Comprehensive security event trail
- **GDPR Compliant**: Data minimization and subject rights support
    """,
    version="1.0.0",
    contact={
        "name": "Chrona Support",
        "email": "support@chrona.example.com",
    },
    license_info={
        "name": "Proprietary",
    },
    lifespan=lifespan,
)

allowed_origins = _get_allowed_origins()
allow_credentials = _get_bool("ALLOW_CREDENTIALS", False)
allowed_methods = _csv_list(os.getenv("ALLOWED_METHODS", "*"), ["*"])
allowed_headers = _csv_list(os.getenv("ALLOWED_HEADERS", "*"), ["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers,
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(devices_router)
app.include_router(onboarding_router)
app.include_router(punch_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "db": "ok" if await db_health() else "down"}


@app.get("/")
def root() -> dict:
    return {"service": "chrona-backend"}

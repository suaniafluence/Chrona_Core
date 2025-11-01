import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .db import db_health, lifespan
from .routers.admin import router as admin_router
from .routers.auth import router as auth_router
from .routers.devices import router as devices_router
from .routers.kiosk_access_admin import router as kiosk_access_admin_router
from .routers.kiosk_heartbeat import router as kiosk_heartbeat_router
from .routers.onboarding import router as onboarding_router
from .routers.punch import router as punch_router
from .routers.totp import router as totp_router

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

# --- Security Headers Middleware ---
_ENABLE_HSTS = _get_bool("ENABLE_HSTS", False)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Basic hardening headers
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault(
        "Permissions-Policy",
        "geolocation=(), microphone=(), camera=(), payment=()",
    )
    # A permissive CSP to avoid breaking Swagger UI
    # Allow CDN resources for FastAPI's default /docs endpoint
    csp_value = (
        "default-src 'self'; "
        "img-src 'self' data: https://cdn.jsdelivr.net "
        "https://fastapi.tiangolo.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net "
        "https://unpkg.com; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
        "https://cdn.jsdelivr.net https://unpkg.com; "
        "font-src 'self' data: https://cdn.jsdelivr.net https://unpkg.com"
    )
    response.headers.setdefault("Content-Security-Policy", csp_value)
    # Only set HSTS when explicitly enabled (should be served over HTTPS)
    if _ENABLE_HSTS:
        hsts_value = "max-age=31536000; includeSubDomains; preload"
        response.headers.setdefault("Strict-Transport-Security", hsts_value)
    return response


app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(devices_router)
app.include_router(kiosk_access_admin_router)
app.include_router(kiosk_heartbeat_router)
app.include_router(onboarding_router)
app.include_router(punch_router)
app.include_router(totp_router)

# Mount static files for Swagger UI (downloaded in Dockerfile)
static_path = Path("/app/static/swagger-ui")
if static_path.exists():
    app.mount(
        "/static/swagger-ui",
        StaticFiles(directory=str(static_path)),
        name="swagger_ui_static",
    )


@app.get("/docs-offline", response_class=HTMLResponse)
async def swagger_ui_offline() -> str:
    """Swagger UI with locally served files (fully offline)."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chrona API Documentation</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/static/swagger-ui/swagger-ui.css">
        <style>
            html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }  # noqa: E501
            *, *:before, *:after { box-sizing: inherit; }
            body { margin:0; background: #fafafa; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="/static/swagger-ui/swagger-ui-bundle.js" charset="UTF-8"></script>  # noqa: E501
        <script src="/static/swagger-ui/swagger-ui-standalone-preset.js" charset="UTF-8"></script>  # noqa: E501
        <script>
            const ui = SwaggerUIBundle({
                url: "/openapi.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "BaseLayout"
            })
        </script>
    </body>
    </html>
    """


@app.get("/redoc-offline", response_class=HTMLResponse)
async def redoc_offline() -> str:
    """ReDoc with CDN (alternative documentation view)."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chrona API - ReDoc</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">  # noqa: E501
        <style>
            body {
                margin: 0;
                padding: 0;
            }
        </style>
    </head>
    <body>
        <redoc spec-url='/openapi.json'></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"> </script>  # noqa: E501
    </body>
    </html>
    """


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "db": "ok" if await db_health() else "down"}


@app.get("/docs-custom", response_class=HTMLResponse)
async def custom_swagger_ui() -> str:
    """Swagger UI with alternative CDN for offline environments."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chrona API Documentation</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@3/swagger-ui.css">  # noqa: E501
        <style>
            html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }  # noqa: E501
            *, *:before, *:after { box-sizing: inherit; }
            body { margin:0; background: #fafafa; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js" charset="UTF-8"></script>  # noqa: E501
        <script src="https://unpkg.com/swagger-ui-dist@3/swagger-ui-standalone-preset.js" charset="UTF-8"></script>  # noqa: E501
        <script>
            const ui = SwaggerUIBundle({
                url: "/openapi.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "BaseLayout"
            })
        </script>
    </body>
    </html>
    """


@app.get("/")
def root() -> dict:
    return {"service": "chrona-backend"}

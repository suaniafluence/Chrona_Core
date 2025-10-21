HTTPS for Dev/Test and Production

Overview
- Uses Traefik as reverse proxy and TLS terminator.
- Dev/Test: local certificates via mkcert; subdomains on .localhost.
- Prod: automatic Let's Encrypt certificates.

Prerequisites
- Docker + Docker Compose v2
- Domains (production): api.<domain>, backoffice.<domain>, kiosk.<domain> pointing to your server
- Email for ACME (Let's Encrypt)

Dev/Test (mkcert + localhost)
1) Install mkcert and its local CA:
   - macOS: `brew install mkcert nss`
   - Windows: `choco install mkcert`
   - Linux: see https://github.com/FiloSottile/mkcert
   - Then: `mkcert -install`

2) Generate a cert for localhost and subdomains:
   - From repo root:
     `mkcert -cert-file infra/traefik/certs/dev-localhost.pem -key-file infra/traefik/certs/dev-localhost-key.pem localhost 127.0.0.1 ::1 api.localhost backoffice.localhost kiosk.localhost`

3) Start stack with HTTPS reverse proxy:
   - `DOMAIN=localhost docker compose -f docker-compose.yml -f docker-compose.https.dev.yml up -d`

4) Access services over HTTPS:
   - Backend (FastAPI): https://api.localhost
   - Backoffice (Vite dev): https://backoffice.localhost
   - Kiosk (Vite dev): https://kiosk.localhost

Notes
- Vite dev servers are already configured with `host: true`; Traefik routes to their internal ports.
- If you rotate certificates, restart Traefik container.

Production (Let's Encrypt)
1) DNS: create A/AAAA records to your server IP(s):
   - api.<domain>, backoffice.<domain>, kiosk.<domain>

2) Prepare ACME storage (first run will create it):
   - Ensure `infra/traefik/acme/` exists; the file `acme.json` will be created by Traefik.
   - Recommended permissions on host: `chmod 600 infra/traefik/acme` (or on `acme.json` after first run).

3) Start stack with HTTPS reverse proxy (replace your domain/email):
   - `DOMAIN=example.com TRAEFIK_ACME_EMAIL=admin@example.com docker compose -f docker-compose.yml -f docker-compose.https.prod.yml up -d`

4) Access services over HTTPS:
   - https://api.example.com
   - https://backoffice.example.com
   - https://kiosk.example.com

Security Tips
- Consider enabling HSTS in backend via `ENABLE_HSTS=true` when traffic is strictly HTTPS.
- Keep Traefik updated. Review CSP and headers for backend and frontends.
- Restrict Traefik dashboard to internal networks only (disabled by default in prod config).


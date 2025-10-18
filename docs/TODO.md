# TODOs / Next Steps

- [ ] AuthN/AuthZ: OAuth2 (JWT), rôles (admin, employé), rotation `SECRET_KEY`.
- [ ] DB & Migrations: SQLAlchemy/SQLModel + Alembic; scripts `alembic upgrade head`.
- [ ] API Schemas: Pydantic models (QR signé, attestation appareil), validation stricte.
- [ ] Observability: logs structurés (JSON), health détaillé, métriques Prometheus.
- [ ] CI: lint (`black`, `isort`, `flake8`), tests (`pytest -q`), build Docker; GitHub Actions.
- [ ] Fronts: bootstrap Vite (backoffice/kiosk), appel `/api/health`, config env.
- [ ] Security: CORS par env, rate limit, headers de sécurité (Starlette middleware), audit deps.
- [ ] Docs: OpenAPI enrichi, guides d’installation, scénario e2e.

Liens utiles
- Backend: `Chrona_Core/backend/`
- Compose: `Chrona_Core/docker-compose.yml`
- Guide: `Chrona_Core/AGENTS.md`

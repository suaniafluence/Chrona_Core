from fastapi.testclient import TestClient

from src.main import app


def test_cors_allows_default_origin_on_get() -> None:
    origin = "http://localhost:3000"
    with TestClient(app) as client:
        r = client.get("/health", headers={"Origin": origin})
        assert r.status_code == 200
        # If origin is allowed, response should echo allowed origin header
        assert r.headers.get("access-control-allow-origin") in (origin, "*")


def test_cors_preflight_options() -> None:
    origin = "http://localhost:3000"
    with TestClient(app) as client:
        r = client.options(
            "/",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )
        assert r.status_code in (200, 204)
        assert r.headers.get("access-control-allow-origin") in (origin, "*")

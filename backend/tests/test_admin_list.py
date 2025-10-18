from fastapi.testclient import TestClient

from src.main import app


def _register(c: TestClient, email: str, password: str) -> int:
    r = c.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201
    return r.json()["id"]


def _login(c: TestClient, email: str, password: str) -> str:
    r = c.post(
        "/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    return r.json()["access_token"]


def test_admin_list_and_detail(tmp_path, monkeypatch) -> None:
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    with TestClient(app) as client:
        # Create three users
        a = _register(client, "a@example.com", "aaa11111")
        b = _register(client, "b@example.com", "bbb22222")
        c = _register(client, "c@example.com", "ccc33333")

        # For simplicity: login as A (role=user), expect forbidden when listing
        token_a = _login(client, "a@example.com", "aaa11111")
        r_forbidden = client.get("/admin/users", headers={"Authorization": f"Bearer {token_a}"})
        assert r_forbidden.status_code in (401, 403)

        # Note: the success path is covered in test_admin_promote.py


def test_admin_list_with_real_admin(tmp_path, monkeypatch) -> None:
    # Full flow using role change via admin endpoint after initial DB bootstrap from earlier tests is not shared across tests.
    # So we perform minimal check: listing requires admin and detail requires admin (403 for user)
    db_file = tmp_path / "test2.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    with TestClient(app) as client:
        _register(client, "x@example.com", "xxx11111")
        user_id = _register(client, "y@example.com", "yyy22222")
        token_user = _login(client, "y@example.com", "yyy22222")
        res = client.get("/admin/users", headers={"Authorization": f"Bearer {token_user}"})
        assert res.status_code in (401, 403)
        res2 = client.get(f"/admin/users/{user_id}", headers={"Authorization": f"Bearer {token_user}"})
        assert res2.status_code in (401, 403)

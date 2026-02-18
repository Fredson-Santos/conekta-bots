"""Testes de integração para endpoints de autenticação."""


class TestAuthEndpoints:
    def test_register(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "email": "new@test.com",
            "password": "senha1234",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@test.com"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate(self, client):
        payload = {"email": "dup@test.com", "password": "senha1234"}
        client.post("/api/v1/auth/register", json=payload)
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 409
        assert resp.json()["error_code"] == "CONFLICT"

    def test_register_invalid_email(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "email": "invalid-email",
            "password": "senha1234",
        })
        assert resp.status_code == 400
        assert resp.json()["error_code"] == "VALIDATION_ERROR"

    def test_register_short_password(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "email": "short@test.com",
            "password": "123",
        })
        assert resp.status_code == 400

    def test_login_success(self, client):
        client.post("/api/v1/auth/register", json={
            "email": "login@test.com",
            "password": "senha1234",
        })
        resp = client.post("/api/v1/auth/login", json={
            "email": "login@test.com",
            "password": "senha1234",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client):
        client.post("/api/v1/auth/register", json={
            "email": "wrong@test.com",
            "password": "senha1234",
        })
        resp = client.post("/api/v1/auth/login", json={
            "email": "wrong@test.com",
            "password": "errada123",
        })
        assert resp.status_code == 401
        assert resp.json()["error_code"] == "UNAUTHORIZED"

    def test_refresh_token(self, client):
        client.post("/api/v1/auth/register", json={
            "email": "refresh@test.com",
            "password": "senha1234",
        })
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "refresh@test.com",
            "password": "senha1234",
        })
        refresh_token = login_resp.json()["refresh_token"]
        resp = client.post(f"/api/v1/auth/refresh?refresh_token={refresh_token}")
        assert resp.status_code == 200
        assert "access_token" in resp.json()

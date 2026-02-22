"""Testes de integração para endpoints de bots."""


class TestBotEndpoints:
    def test_list_bots_empty(self, client, auth_headers):
        resp = client.get("/api/v1/bots/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_bot(self, client, auth_headers):
        resp = client.post("/api/v1/bots/", headers=auth_headers, json={
            "nome": "Meu Bot",
            "api_id": "12345",
            "api_hash": "abc123",
            "tipo": "user",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["nome"] == "Meu Bot"
        assert data["ativo"] is True

    def test_create_bot_without_auth(self, client):
        resp = client.post("/api/v1/bots/", json={
            "nome": "Bot Sem Auth",
            "api_id": "12345",
            "api_hash": "abc123",
            "tipo": "user",
        })
        assert resp.status_code == 401

    def test_get_bot(self, client, auth_headers):
        create_resp = client.post("/api/v1/bots/", headers=auth_headers, json={
            "nome": "Get Bot",
            "api_id": "12345",
            "api_hash": "abc123",
            "tipo": "user",
        })
        bot_id = create_resp.json()["id"]
        resp = client.get(f"/api/v1/bots/{bot_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["nome"] == "Get Bot"

    def test_get_bot_not_found(self, client, auth_headers):
        resp = client.get("/api/v1/bots/999", headers=auth_headers)
        assert resp.status_code == 404
        assert resp.json()["error_code"] == "NOT_FOUND"

    def test_update_bot(self, client, auth_headers):
        create_resp = client.post("/api/v1/bots/", headers=auth_headers, json={
            "nome": "Original",
            "api_id": "12345",
            "api_hash": "abc123",
            "tipo": "user",
        })
        bot_id = create_resp.json()["id"]
        resp = client.patch(f"/api/v1/bots/{bot_id}", headers=auth_headers, json={
            "nome": "Atualizado",
        })
        assert resp.status_code == 200
        assert resp.json()["nome"] == "Atualizado"

    def test_toggle_bot(self, client, auth_headers):
        create_resp = client.post("/api/v1/bots/", headers=auth_headers, json={
            "nome": "Toggle Bot",
            "api_id": "12345",
            "api_hash": "abc123",
            "tipo": "user",
        })
        bot_id = create_resp.json()["id"]
        resp = client.patch(f"/api/v1/bots/{bot_id}/toggle", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["ativo"] is False

    def test_delete_bot(self, client, auth_headers):
        create_resp = client.post("/api/v1/bots/", headers=auth_headers, json={
            "nome": "Delete Bot",
            "api_id": "12345",
            "api_hash": "abc123",
            "tipo": "user",
        })
        bot_id = create_resp.json()["id"]
        resp = client.delete(f"/api/v1/bots/{bot_id}", headers=auth_headers)
        assert resp.status_code == 204

        # Verifica que foi removido
        get_resp = client.get(f"/api/v1/bots/{bot_id}", headers=auth_headers)
        assert get_resp.status_code == 404


class TestHealthEndpoint:
    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["app"] == "ConektaBots"

"""Testes unitários para AuthService."""

from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


class TestAuthService:
    def test_register_success(self, db):
        data = UserCreate(email="novo@test.com", password="senha1234")
        user = AuthService.register(db, data)
        assert user.id is not None
        assert user.email == "novo@test.com"
        assert user.is_active is True

    def test_register_duplicate_email(self, db):
        data = UserCreate(email="dup@test.com", password="senha1234")
        AuthService.register(db, data)
        try:
            AuthService.register(db, data)
            assert False, "Deveria ter lançado ValueError"
        except ValueError as e:
            assert "já cadastrado" in str(e)

    def test_authenticate_success(self, db):
        data = UserCreate(email="auth@test.com", password="senha1234")
        AuthService.register(db, data)
        user = AuthService.authenticate(db, "auth@test.com", "senha1234")
        assert user is not None
        assert user.email == "auth@test.com"

    def test_authenticate_wrong_password(self, db):
        data = UserCreate(email="auth2@test.com", password="senha1234")
        AuthService.register(db, data)
        user = AuthService.authenticate(db, "auth2@test.com", "senhaerrada")
        assert user is None

    def test_authenticate_nonexistent_email(self, db):
        user = AuthService.authenticate(db, "nao-existe@test.com", "senha1234")
        assert user is None

    def test_create_tokens(self, db):
        data = UserCreate(email="token@test.com", password="senha1234")
        user = AuthService.register(db, data)
        tokens = AuthService.create_tokens(user.id)
        assert tokens.access_token is not None
        assert tokens.refresh_token is not None

    def test_refresh_access_token(self, db):
        data = UserCreate(email="refresh@test.com", password="senha1234")
        user = AuthService.register(db, data)
        tokens = AuthService.create_tokens(user.id)
        new_tokens = AuthService.refresh_access_token(tokens.refresh_token)
        assert new_tokens.access_token is not None
        assert new_tokens.refresh_token is not None

    def test_refresh_with_access_token_fails(self, db):
        data = UserCreate(email="bad-refresh@test.com", password="senha1234")
        user = AuthService.register(db, data)
        tokens = AuthService.create_tokens(user.id)
        try:
            AuthService.refresh_access_token(tokens.access_token)
            assert False, "Deveria ter lançado ValueError"
        except ValueError as e:
            assert "refresh" in str(e).lower()

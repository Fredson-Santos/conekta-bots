"""Service de autenticação: registro, login, refresh de tokens."""

import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import Token, UserCreate


class AuthService:
    """Gerencia registro, login e refresh de usuários."""

    @staticmethod
    def register(db: Session, data: UserCreate) -> User:
        """Registra um novo usuário.

        Raises:
            ValueError: se o email já estiver cadastrado.
        """
        existing = db.execute(
            select(User).where(User.email == data.email)
        ).scalar_one_or_none()

        if existing:
            raise ValueError("Email já cadastrado")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> User | None:
        """Valida credenciais e retorna o User ou None."""
        user = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    @staticmethod
    def create_tokens(user_id: int) -> Token:
        """Gera par access + refresh tokens."""
        return Token(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Token:
        """Gera novo par de tokens a partir de um refresh token válido.

        Raises:
            ValueError: se o token for inválido ou expirado.
        """
        try:
            payload = decode_token(refresh_token)
        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token expirado")
        except jwt.InvalidTokenError:
            raise ValueError("Refresh token inválido")

        if payload.get("type") != "refresh":
            raise ValueError("Token não é um refresh token")

        user_id = int(payload["sub"])
        return Token(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )

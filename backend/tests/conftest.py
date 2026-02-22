"""Fixtures compartilhadas para os testes."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User


# ── Database de teste (SQLite in-memory) ─────────────────

engine_test = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine_test, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def db():
    """Cria tabelas antes de cada teste e dropa depois."""
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def client(db):
    """TestClient com override de get_db para usar DB em memória."""

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user(db) -> User:
    """Cria um usuário de teste no DB."""
    user = User(
        email="test@example.com",
        hashed_password=hash_password("senha1234"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def auth_headers(test_user) -> dict:
    """Retorna headers com Bearer token válido."""
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}

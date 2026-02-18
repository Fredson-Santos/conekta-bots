"""Endpoints de autenticação: registro, login, refresh."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.core.exceptions import ConflictException, UnauthorizedException
from app.db.session import get_db
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: Session = Depends(get_db)):
    """Registra um novo usuário."""
    try:
        user = AuthService.register(db, data)
    except ValueError as e:
        raise ConflictException(detail=str(e))
    return user


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """Autentica e retorna tokens JWT."""
    user = AuthService.authenticate(db, data.email, data.password)
    if not user:
        raise UnauthorizedException(detail="Email ou senha incorretos")
    return AuthService.create_tokens(user.id)


@router.post("/refresh", response_model=Token)
async def refresh(refresh_token: str):
    """Gera novo par de tokens a partir de um refresh token."""
    try:
        return AuthService.refresh_access_token(refresh_token)
    except ValueError as e:
        raise UnauthorizedException(detail=str(e))

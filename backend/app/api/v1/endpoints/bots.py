"""Endpoints de CRUD de Bots + autenticação Telegram."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.api.deps import get_current_user
from app.core.exceptions import BadRequestException, NotFoundException, PlanLimitException
from app.db.session import get_db
from app.models.user import User
from app.schemas.bot import (
    BotAuthResponse,
    BotAuthStart,
    BotAuthVerify,
    BotCreate,
    BotResponse,
    BotToggleResponse,
    BotUpdate,
)
from app.services import telegram_service
from app.services.bot_service import BotService

router = APIRouter(prefix="/bots", tags=["Bots"])


def _get_bot_or_404(db, bot_id: int, owner_id: int):
    bot = BotService.get_by_id(db, bot_id, owner_id)
    if not bot:
        raise NotFoundException("Bot")
    return bot


# ── CRUD ─────────────────────────────────────────────────


@router.get("/", response_model=list[BotResponse])
async def list_bots(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todos os bots do usuário."""
    return BotService.get_all(db, current_user.id)


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna um bot pelo ID."""
    return _get_bot_or_404(db, bot_id, current_user.id)


@router.post("/", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
async def create_bot(
    data: BotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria um novo bot (verifica limite do plano)."""
    count = BotService.count_by_owner(db, current_user.id)
    if count >= current_user.max_bots:
        raise PlanLimitException(
            resource="bots", limit=current_user.max_bots, plan=current_user.plan
        )
    return BotService.create(db, data, current_user.id)


@router.patch("/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: int,
    data: BotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualiza campos de um bot (partial update)."""
    bot = _get_bot_or_404(db, bot_id, current_user.id)
    return BotService.update(db, bot, data)


@router.patch("/{bot_id}/toggle", response_model=BotToggleResponse)
async def toggle_bot(
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ativa/desativa um bot."""
    bot = _get_bot_or_404(db, bot_id, current_user.id)
    return BotService.toggle_active(db, bot)


@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot(
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove um bot e todos seus dados (regras, agendamentos)."""
    bot = _get_bot_or_404(db, bot_id, current_user.id)
    BotService.delete(db, bot)


# ── Autenticação Telegram ────────────────────────────────


@router.post("/auth/start", response_model=BotAuthResponse)
async def start_telegram_auth(
    data: BotAuthStart,
    _current_user: User = Depends(get_current_user),
):
    """Inicia autenticação Telegram — envia código SMS."""
    try:
        auth_id = await telegram_service.start_auth(
            data.api_id, data.api_hash, data.phone
        )
    except Exception as e:
        raise BadRequestException(detail=f"Erro ao iniciar auth: {e}")
    return BotAuthResponse(auth_id=auth_id, message="Código enviado via SMS")


@router.post("/auth/verify", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
async def verify_telegram_code(
    data: BotAuthVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verifica código SMS e cria o bot autenticado."""
    try:
        session_string, phone = await telegram_service.verify_code(data.auth_id, data.code)
    except ValueError as e:
        raise BadRequestException(detail=str(e))

    bot_data = BotCreate(
        nome=data.nome,
        api_id=data.api_id,
        api_hash=data.api_hash,
        tipo="user",
        phone=phone,
    )
    bot = BotService.create(db, bot_data, current_user.id)
    bot.session_string = session_string
    db.commit()
    db.refresh(bot)
    return bot

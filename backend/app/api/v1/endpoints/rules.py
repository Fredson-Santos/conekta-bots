"""Endpoints de CRUD de Regras."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.db.session import get_db
from app.models.user import User
from app.schemas.rule import RuleCreate, RuleResponse, RuleUpdate
from app.services.bot_service import BotService
from app.services.rule_service import RuleService

router = APIRouter(prefix="/rules", tags=["Regras"])


def _verify_bot_ownership(db: Session, bot_id: int, user: User):
    bot = BotService.get_by_id(db, bot_id, user.id)
    if not bot:
        raise NotFoundException("Bot")
    return bot


def _get_rule_or_404(db: Session, rule_id: int, bot_id: int):
    regra = RuleService.get_by_id(db, rule_id, bot_id)
    if not regra:
        raise NotFoundException("Regra")
    return regra


@router.get("/", response_model=list[RuleResponse])
async def list_all_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todas as regras de todos os bots do usuário."""
    return RuleService.get_all_by_owner(db, current_user.id)


@router.get("/bot/{bot_id}", response_model=list[RuleResponse])
async def list_rules(
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todas as regras de um bot."""
    _verify_bot_ownership(db, bot_id, current_user)
    return RuleService.get_all_by_bot(db, bot_id)


@router.get("/{rule_id}/bot/{bot_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: int,
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna uma regra pelo ID."""
    _verify_bot_ownership(db, bot_id, current_user)
    return _get_rule_or_404(db, rule_id, bot_id)


@router.post("/", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    data: RuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria uma nova regra para um bot."""
    _verify_bot_ownership(db, data.bot_id, current_user)
    return RuleService.create(db, data)


@router.patch("/{rule_id}/bot/{bot_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: int,
    bot_id: int,
    data: RuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualiza campos de uma regra (partial update)."""
    _verify_bot_ownership(db, bot_id, current_user)
    regra = _get_rule_or_404(db, rule_id, bot_id)
    return RuleService.update(db, regra, data)


@router.patch("/{rule_id}/bot/{bot_id}/toggle", response_model=RuleResponse)
async def toggle_rule(
    rule_id: int,
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ativa/desativa uma regra."""
    _verify_bot_ownership(db, bot_id, current_user)
    regra = _get_rule_or_404(db, rule_id, bot_id)
    return RuleService.toggle_active(db, regra)


@router.delete("/{rule_id}/bot/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: int,
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove uma regra."""
    _verify_bot_ownership(db, bot_id, current_user)
    regra = _get_rule_or_404(db, rule_id, bot_id)
    RuleService.delete(db, regra)

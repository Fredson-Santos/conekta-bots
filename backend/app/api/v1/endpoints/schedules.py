"""Endpoints de CRUD de Agendamentos."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.db.session import get_db
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.services.bot_service import BotService
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/schedules", tags=["Agendamentos"])


def _verify_bot_ownership(db: Session, bot_id: int, user: User):
    bot = BotService.get_by_id(db, bot_id, user.id)
    if not bot:
        raise NotFoundException("Bot")
    return bot


def _get_schedule_or_404(db: Session, schedule_id: int, bot_id: int):
    agendamento = ScheduleService.get_by_id(db, schedule_id, bot_id)
    if not agendamento:
        raise NotFoundException("Agendamento")
    return agendamento


@router.get("/", response_model=list[ScheduleResponse])
async def list_all_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todos os agendamentos de todos os bots do usuário."""
    return ScheduleService.get_all_by_owner(db, current_user.id)


@router.get("/bot/{bot_id}", response_model=list[ScheduleResponse])
async def list_schedules(
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todos os agendamentos de um bot."""
    _verify_bot_ownership(db, bot_id, current_user)
    return ScheduleService.get_all_by_bot(db, bot_id)


@router.post("/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    data: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria um novo agendamento."""
    _verify_bot_ownership(db, data.bot_id, current_user)
    return ScheduleService.create(db, data)


@router.patch("/{schedule_id}/bot/{bot_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    bot_id: int,
    data: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualiza campos de um agendamento (partial update)."""
    _verify_bot_ownership(db, bot_id, current_user)
    agendamento = _get_schedule_or_404(db, schedule_id, bot_id)
    return ScheduleService.update(db, agendamento, data)


@router.patch("/{schedule_id}/bot/{bot_id}/toggle", response_model=ScheduleResponse)
async def toggle_schedule(
    schedule_id: int,
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ativa/desativa um agendamento."""
    _verify_bot_ownership(db, bot_id, current_user)
    agendamento = _get_schedule_or_404(db, schedule_id, bot_id)
    return ScheduleService.toggle_active(db, agendamento)


@router.delete("/{schedule_id}/bot/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove um agendamento."""
    _verify_bot_ownership(db, bot_id, current_user)
    agendamento = _get_schedule_or_404(db, schedule_id, bot_id)
    ScheduleService.delete(db, agendamento)

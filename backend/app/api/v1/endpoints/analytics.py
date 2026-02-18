"""Endpoints de logs e analytics."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.log import LogResponse
from app.services.bot_service import BotService
from app.services.log_service import LogService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/logs/{bot_id}", response_model=list[LogResponse])
async def get_logs_by_bot(
    bot_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna logs de execução de um bot (paginado)."""
    bot = BotService.get_by_id(db, bot_id, current_user.id)
    if not bot:
        return []
    return LogService.get_by_bot(db, bot_id, limit=limit, offset=offset)


@router.get("/logs/recent", response_model=list[LogResponse])
async def get_recent_logs(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Retorna os logs mais recentes (todos os bots)."""
    return LogService.get_recent(db, limit=limit)


@router.get("/dashboard")
async def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna estatísticas resumidas para o dashboard."""
    bots = BotService.get_all(db, current_user.id)
    total_bots = len(bots)
    active_bots = sum(1 for b in bots if b.ativo)
    recent_logs = LogService.get_recent(db, limit=10)

    return {
        "total_bots": total_bots,
        "active_bots": active_bots,
        "inactive_bots": total_bots - active_bots,
        "max_bots": current_user.max_bots,
        "plan": current_user.plan,
        "recent_logs": [LogResponse.model_validate(log) for log in recent_logs],
    }

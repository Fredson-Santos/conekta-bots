"""Endpoints de Configurações do usuário (ex: credenciais Shopee)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.configuracao import ConfiguracaoResponse, ConfiguracaoUpdate
from app.services.configuracao_service import ConfiguracaoService

router = APIRouter(prefix="/settings", tags=["Configurações"])


@router.get("/", response_model=ConfiguracaoResponse | None)
async def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna a configuração do usuário autenticado."""
    return ConfiguracaoService.get_by_owner(db, current_user.id)


@router.put("/", response_model=ConfiguracaoResponse)
async def update_settings(
    data: ConfiguracaoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria ou atualiza a configuração do usuário (Shopee, etc.)."""
    return ConfiguracaoService.create_or_update(db, current_user.id, data)

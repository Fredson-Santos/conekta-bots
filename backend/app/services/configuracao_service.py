from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.configuracao import Configuracao
from app.schemas.configuracao import ConfiguracaoCreate, ConfiguracaoUpdate


class ConfiguracaoService:
    """Service para operações de Configuração do usuário."""

    @staticmethod
    def get_by_owner(db: Session, owner_id: int) -> Configuracao | None:
        stmt = select(Configuracao).where(Configuracao.owner_id == owner_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create_or_update(
        db: Session, owner_id: int, data: ConfiguracaoCreate | ConfiguracaoUpdate
    ) -> Configuracao:
        config = ConfiguracaoService.get_by_owner(db, owner_id)
        if config is None:
            config = Configuracao(owner_id=owner_id, **data.model_dump(exclude_unset=True))
            db.add(config)
        else:
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(config, field, value)
        db.commit()
        db.refresh(config)
        return config

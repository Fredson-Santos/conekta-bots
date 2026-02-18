from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rule import Regra
from app.schemas.rule import RuleCreate, RuleUpdate


class RuleService:
    """Service para operações de CRUD de Regras."""

    @staticmethod
    def get_by_id(db: Session, rule_id: int, bot_id: int) -> Regra | None:
        stmt = select(Regra).where(Regra.id == rule_id, Regra.bot_id == bot_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_all_by_bot(db: Session, bot_id: int) -> list[Regra]:
        stmt = select(Regra).where(Regra.bot_id == bot_id).order_by(Regra.id)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def create(db: Session, data: RuleCreate) -> Regra:
        regra = Regra(**data.model_dump())
        db.add(regra)
        db.commit()
        db.refresh(regra)
        return regra

    @staticmethod
    def update(db: Session, regra: Regra, data: RuleUpdate) -> Regra:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(regra, field, value)
        db.commit()
        db.refresh(regra)
        return regra

    @staticmethod
    def toggle_active(db: Session, regra: Regra) -> Regra:
        regra.ativo = not regra.ativo
        db.commit()
        db.refresh(regra)
        return regra

    @staticmethod
    def delete(db: Session, regra: Regra) -> None:
        db.delete(regra)
        db.commit()

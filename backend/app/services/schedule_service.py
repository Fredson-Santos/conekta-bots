from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.schedule import Agendamento
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate


class ScheduleService:
    """Service para operações de CRUD de Agendamentos."""

    @staticmethod
    def get_by_id(db: Session, schedule_id: int, bot_id: int) -> Agendamento | None:
        stmt = select(Agendamento).where(
            Agendamento.id == schedule_id, Agendamento.bot_id == bot_id
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_all_by_bot(db: Session, bot_id: int) -> list[Agendamento]:
        stmt = (
            select(Agendamento).where(Agendamento.bot_id == bot_id).order_by(Agendamento.id)
        )
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def create(db: Session, data: ScheduleCreate) -> Agendamento:
        agendamento = Agendamento(**data.model_dump())
        db.add(agendamento)
        db.commit()
        db.refresh(agendamento)
        return agendamento

    @staticmethod
    def update(db: Session, agendamento: Agendamento, data: ScheduleUpdate) -> Agendamento:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agendamento, field, value)
        db.commit()
        db.refresh(agendamento)
        return agendamento

    @staticmethod
    def toggle_active(db: Session, agendamento: Agendamento) -> Agendamento:
        agendamento.ativo = not agendamento.ativo
        db.commit()
        db.refresh(agendamento)
        return agendamento

    @staticmethod
    def delete(db: Session, agendamento: Agendamento) -> None:
        db.delete(agendamento)
        db.commit()

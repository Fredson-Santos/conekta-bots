from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Agendamento(Base):
    __tablename__ = "agendamento"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100))
    origem: Mapped[str] = mapped_column(String(255))
    destino: Mapped[str] = mapped_column(String(255))
    msg_id_atual: Mapped[int] = mapped_column(Integer)
    tipo_envio: Mapped[str] = mapped_column(String(20))
    horario: Mapped[str] = mapped_column(String(255))  # "HH:MM" ou múltiplos "HH:MM,HH:MM"
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Foreign key
    bot_id: Mapped[int] = mapped_column(ForeignKey("bot.id"))

    # Relationships
    bot: Mapped["Bot"] = relationship(back_populates="agendamentos")

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Bot(Base):
    __tablename__ = "bot"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100))
    api_id: Mapped[str] = mapped_column(String(50))
    api_hash: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    bot_token: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tipo: Mapped[str] = mapped_column(String(10), default="user")
    session_string: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Foreign key para User (multi-tenancy)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="bots")
    regras: Mapped[list["Regra"]] = relationship(
        back_populates="bot", cascade="all, delete-orphan"
    )
    agendamentos: Mapped[list["Agendamento"]] = relationship(
        back_populates="bot", cascade="all, delete-orphan"
    )

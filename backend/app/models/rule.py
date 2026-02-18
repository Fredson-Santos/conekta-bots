from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Regra(Base):
    __tablename__ = "regra"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100))
    origem: Mapped[str] = mapped_column(String(255))
    destino: Mapped[str] = mapped_column(String(255))

    # Filtros e edições
    filtro: Mapped[str | None] = mapped_column(Text, nullable=True)
    substituto: Mapped[str | None] = mapped_column(Text, nullable=True)
    bloqueios: Mapped[str | None] = mapped_column(Text, nullable=True)
    somente_se_tiver: Mapped[str | None] = mapped_column(Text, nullable=True)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Foreign key
    bot_id: Mapped[int] = mapped_column(ForeignKey("bot.id"))

    # Relationships
    bot: Mapped["Bot"] = relationship(back_populates="regras")

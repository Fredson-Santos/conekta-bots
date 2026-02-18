"""Modelo Configuracao — configurações globais do usuário (ex: Shopee API)."""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Configuracao(Base):
    __tablename__ = "configuracao"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Shopee Afiliados
    shopee_app_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shopee_app_secret: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Dono
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True)
    owner: Mapped["User"] = relationship(back_populates="configuracao")

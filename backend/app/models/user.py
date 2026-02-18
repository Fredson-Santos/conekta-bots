from datetime import datetime

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    plan: Mapped[str] = mapped_column(String(20), default="free")
    max_bots: Mapped[int] = mapped_column(default=2)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    # Relationships
    bots: Mapped[list["Bot"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    configuracao: Mapped["Configuracao | None"] = relationship(
        back_populates="owner", cascade="all, delete-orphan", uselist=False
    )

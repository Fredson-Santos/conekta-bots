from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LogExecucao(Base):
    __tablename__ = "logexecucao"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bot_id: Mapped[int] = mapped_column(Integer, ForeignKey("bot.id"))
    bot_nome: Mapped[str] = mapped_column(String(100))
    origem: Mapped[str] = mapped_column(String(255))
    destino: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20))
    mensagem: Mapped[str] = mapped_column(Text)
    data_hora: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.log import LogExecucao


class LogService:
    """Service para consulta de logs de execução."""

    @staticmethod
    def get_by_bot(
        db: Session, bot_id: int, limit: int = 50, offset: int = 0
    ) -> list[LogExecucao]:
        stmt = (
            select(LogExecucao)
            .where(LogExecucao.bot_id == bot_id)
            .order_by(LogExecucao.data_hora.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get_recent(db: Session, limit: int = 20) -> list[LogExecucao]:
        stmt = (
            select(LogExecucao)
            .order_by(LogExecucao.data_hora.desc())
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def create(
        db: Session,
        bot_id: int,
        bot_nome: str,
        origem: str,
        destino: str,
        status: str,
        mensagem: str,
    ) -> LogExecucao:
        log = LogExecucao(
            bot_id=bot_id,
            bot_nome=bot_nome,
            origem=origem,
            destino=destino,
            status=status,
            mensagem=mensagem,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

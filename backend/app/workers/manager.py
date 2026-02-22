"""Manager: inicializa e executa todos os workers de bots ativos."""

import asyncio
import logging

from sqlalchemy import select

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.bot import Bot
from app.workers.bot_worker import BotWorker
from app.workers.scheduler_worker import SchedulerWorker

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)-5s | %(message)s",
    datefmt="%H:%M:%S",
)

# Nossos loggers: INFO para ver envio de mensagens e eventos importantes
for _name in ("conekta-bots.manager", "conekta-bots.worker", "conekta-bots.scheduler", "conekta-bots.shopee"):
    logging.getLogger(_name).setLevel(logging.INFO)

# Silencia libs externas (SQLAlchemy, Telethon)
for _name in ("sqlalchemy", "sqlalchemy.engine", "sqlalchemy.engine.Engine",
              "sqlalchemy.pool", "sqlalchemy.dialects", "sqlalchemy.orm",
              "telethon", "telethon.network"):
    _lg = logging.getLogger(_name)
    _lg.setLevel(logging.WARNING)
    _lg.handlers.clear()  # Remove handlers criados pelo echo do SQLAlchemy
    _lg.propagate = False

logger = logging.getLogger("conekta-bots.manager")


async def main() -> None:
    """Ponto de entrada do manager — busca bots ativos e inicia workers."""
    # Garante que as tabelas existem
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        bots_ativos = list(
            db.execute(select(Bot).where(Bot.ativo == True)).scalars().all()  # noqa: E712
        )
    finally:
        db.close()

    if not bots_ativos:
        logger.warning("Nenhum bot ativo encontrado. Manager aguardando...")
        # Fica rodando para não encerrar o container
        while True:
            await asyncio.sleep(60)
        return

    logger.info("Iniciando %d bot(s) ativo(s)", len(bots_ativos))

    tarefas = []
    for bot_data in bots_ativos:
        # Worker de regras (encaminhamento)
        worker = BotWorker(bot_data)
        tarefas.append(worker.start())

        # Worker de agendamentos
        scheduler = SchedulerWorker(bot_data)
        tarefas.append(scheduler.start())

        logger.info("  → %s (id=%d)", bot_data.nome, bot_data.id)

    await asyncio.gather(*tarefas)


if __name__ == "__main__":
    asyncio.run(main())

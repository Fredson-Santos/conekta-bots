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
    level=logging.INFO,
    format="%(asctime)s | %(name)-25s | %(levelname)-5s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
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

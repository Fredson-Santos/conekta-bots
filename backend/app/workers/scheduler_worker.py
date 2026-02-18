"""Scheduler Worker — verifica agendamentos e envia mensagens programadas."""

import asyncio
import logging
from datetime import datetime

from telethon import TelegramClient
from telethon.sessions import StringSession

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.bot import Bot
from app.services.log_service import LogService
from app.services.schedule_service import ScheduleService

logger = logging.getLogger("conekta-bots.scheduler")


class SchedulerWorker:
    """Worker que verifica e executa agendamentos de envio de mensagens."""

    def __init__(self, bot_data: Bot):
        self.bot_id = bot_data.id
        self.bot_nome = bot_data.nome
        self.api_id = int(bot_data.api_id)
        self.api_hash = bot_data.api_hash
        self.session_string = bot_data.session_string
        self.client = TelegramClient(
            StringSession(self.session_string), self.api_id, self.api_hash
        )
        self._running = False

    @staticmethod
    def _processar_chat_id(chat_id: str):
        """Converte ID numérico para int; mantém string caso contrário ('me', '@canal')."""
        try:
            return int(chat_id)
        except (ValueError, TypeError):
            return chat_id

    async def start(self) -> None:
        """Conecta o client e inicia o loop de verificação."""
        logger.debug("Scheduler iniciado: %s (id=%d)", self.bot_nome, self.bot_id)
        await self.client.connect()

        if not await self.client.is_user_authorized():
            logger.error("Bot %s não autorizado — session expirada?", self.bot_nome)
            return

        self._running = True
        await self._loop_verificacao()

    async def stop(self) -> None:
        """Para o scheduler e desconecta."""
        self._running = False
        await self.client.disconnect()
        logger.info("Scheduler parado: %s", self.bot_nome)

    async def _loop_verificacao(self) -> None:
        """Loop principal: verifica agendamentos a cada 30 segundos."""
        while self._running:
            await self._verificar_agendamentos()
            await asyncio.sleep(30)

    async def _verificar_agendamentos(self) -> None:
        """Carrega agendamentos ativos e executa os que batem com o horário atual."""
        agora = datetime.now().strftime("%H:%M")

        db = SessionLocal()
        try:
            agendamentos = ScheduleService.get_all_by_bot(db, self.bot_id)
            ativos = [a for a in agendamentos if a.ativo]

            for agendamento in ativos:
                horarios = [h.strip() for h in agendamento.horario.split(",")]
                if agora in horarios:
                    await self._executar_agendamento(db, agendamento)
        finally:
            db.close()

    async def _executar_agendamento(self, db, agendamento) -> None:
        """Executa um agendamento: busca mensagem na origem e envia ao destino."""
        try:
            origem = self._processar_chat_id(agendamento.origem)
            destino = self._processar_chat_id(agendamento.destino)

            # Busca mensagem pelo ID na origem
            mensagem = await self.client.get_messages(
                origem, ids=agendamento.msg_id_atual
            )

            if not mensagem:
                logger.warning(
                    "[%s] Msg %d não encontrada em %s",
                    self.bot_nome, agendamento.msg_id_atual, agendamento.origem,
                )
                return

            texto = mensagem.text or ""
            # Envia o objeto Message completo (preserva mídia/formatação)
            await self.client.send_message(destino, mensagem)

            LogService.create(
                db,
                bot_id=self.bot_id,
                bot_nome=self.bot_nome,
                origem=agendamento.origem,
                destino=agendamento.destino,
                status="sucesso",
                mensagem=f"[Agendamento: {agendamento.nome}] {texto[:150]}",
            )

            # Se envio sequencial, avança para próxima mensagem
            if agendamento.tipo_envio == "sequencial":
                agendamento.msg_id_atual += 1
                db.commit()

            logger.info(
                "⏰ [%s] Agendamento '%s': %s → %s",
                self.bot_nome, agendamento.nome,
                agendamento.origem, agendamento.destino,
            )

        except Exception as e:
            LogService.create(
                db,
                bot_id=self.bot_id,
                bot_nome=self.bot_nome,
                origem=agendamento.origem,
                destino=agendamento.destino,
                status="erro",
                mensagem=f"[Agendamento: {agendamento.nome}] {str(e)[:150]}",
            )
            logger.error(
                "[%s] Erro no agendamento '%s': %s",
                self.bot_nome, agendamento.nome, e,
            )

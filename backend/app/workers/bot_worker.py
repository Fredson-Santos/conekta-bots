"""BotWorker refatorado — usa services layer para DB e logging."""

import asyncio
import logging

from telethon import TelegramClient, events
from telethon.sessions import StringSession

from app.db.session import SessionLocal
from app.models.bot import Bot
from app.services.log_service import LogService
from app.services.rule_service import RuleService

logger = logging.getLogger("conekta-bots.worker")


class BotWorker:
    """Worker que gerencia um bot Telegram: regras de encaminhamento + fila de envio."""

    def __init__(self, bot_data: Bot):
        self.bot_id = bot_data.id
        self.bot_nome = bot_data.nome
        self.api_id = int(bot_data.api_id)
        self.api_hash = bot_data.api_hash
        self.session_string = bot_data.session_string
        self.client = TelegramClient(
            StringSession(self.session_string), self.api_id, self.api_hash
        )
        self.fila_envio: asyncio.Queue = asyncio.Queue()
        self._running = False

    async def start(self) -> None:
        """Conecta o client, carrega regras e inicia loops."""
        logger.info("Iniciando worker: %s (id=%d)", self.bot_nome, self.bot_id)
        await self.client.connect()

        if not await self.client.is_user_authorized():
            logger.error("Bot %s não autorizado — session expirada?", self.bot_nome)
            return

        self._running = True
        await self._carregar_regras()

        await asyncio.gather(
            self._loop_fila(),
            self.client.run_until_disconnected(),
        )

    async def stop(self) -> None:
        """Para o worker e desconecta o client."""
        self._running = False
        await self.client.disconnect()
        logger.info("Worker parado: %s", self.bot_nome)

    async def _carregar_regras(self) -> None:
        """Carrega regras do DB e registra event handlers no Telethon."""
        db = SessionLocal()
        try:
            regras = RuleService.get_all_by_bot(db, self.bot_id)
            regras_ativas = [r for r in regras if r.ativo]
            logger.info(
                "Bot %s: %d regras ativas carregadas", self.bot_nome, len(regras_ativas)
            )

            for regra in regras_ativas:
                self._registrar_handler(regra)
        finally:
            db.close()

    def _registrar_handler(self, regra) -> None:
        """Registra um event handler para uma regra específica."""
        origem = regra.origem
        regra_id = regra.id
        regra_nome = regra.nome
        destino = regra.destino
        filtro = regra.filtro
        substituto = regra.substituto
        bloqueios = regra.bloqueios
        somente_se_tiver = regra.somente_se_tiver

        async def handler(event):
            texto = event.message.text or ""

            # Filtro: bloqueia se contiver palavras bloqueadas
            if bloqueios:
                palavras_bloqueadas = [p.strip() for p in bloqueios.split(",")]
                if any(p in texto for p in palavras_bloqueadas if p):
                    return

            # Filtro: só encaminha se contiver palavras obrigatórias
            if somente_se_tiver:
                palavras_obrigatorias = [p.strip() for p in somente_se_tiver.split(",")]
                if not any(p in texto for p in palavras_obrigatorias if p):
                    return

            # Filtro: regex ou substring
            if filtro and filtro not in texto:
                return

            # Substituição
            mensagem_final = texto
            if substituto:
                pares = substituto.split("|")
                for par in pares:
                    partes = par.split("->")
                    if len(partes) == 2:
                        mensagem_final = mensagem_final.replace(
                            partes[0].strip(), partes[1].strip()
                        )

            await self.fila_envio.put((destino, mensagem_final, regra_nome, origem))

        self.client.add_event_handler(
            handler, events.NewMessage(chats=origem)
        )
        logger.debug("Handler registrado: regra '%s' (id=%d)", regra_nome, regra_id)

    async def _loop_fila(self) -> None:
        """Processa fila de envio de mensagens."""
        while self._running:
            try:
                destino, mensagem, regra_nome, origem = await asyncio.wait_for(
                    self.fila_envio.get(), timeout=1.0
                )
            except asyncio.TimeoutError:
                continue

            db = SessionLocal()
            try:
                await self.client.send_message(destino, mensagem)
                LogService.create(
                    db,
                    bot_id=self.bot_id,
                    bot_nome=self.bot_nome,
                    origem=origem,
                    destino=destino,
                    status="sucesso",
                    mensagem=mensagem[:200],
                )
                logger.info(
                    "[%s] %s → %s (regra: %s)",
                    self.bot_nome, origem, destino, regra_nome,
                )
            except Exception as e:
                LogService.create(
                    db,
                    bot_id=self.bot_id,
                    bot_nome=self.bot_nome,
                    origem=origem,
                    destino=destino,
                    status="erro",
                    mensagem=str(e)[:200],
                )
                logger.error(
                    "[%s] Erro ao enviar %s → %s: %s",
                    self.bot_nome, origem, destino, e,
                )
            finally:
                db.close()

    async def recarregar_regras(self) -> None:
        """Remove handlers antigos e recarrega do DB (hot-reload)."""
        self.client.list_event_handlers().clear()
        await self._carregar_regras()
        logger.info("Regras recarregadas para bot %s", self.bot_nome)

"""BotWorker refatorado — usa services layer para DB e logging.

Portado do MVP com melhorias:
- Hot-reload de regras e credenciais Shopee (poll a cada 3s)
- Conversão de chat IDs numéricos para int
- Suporte para origens/destinos múltiplos (separados por vírgula)
- Anti-flood (delay aleatório + FloodWaitError handling)
- Logs diagnósticos detalhados para Shopee
"""

import asyncio
import logging
import random
import re

from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from telethon.sessions import StringSession

from app.db.session import SessionLocal
from app.models.bot import Bot
from app.models.configuracao import Configuracao
from app.services.configuracao_service import ConfiguracaoService
from app.services.log_service import LogService
from app.services.rule_service import RuleService
from app.services.shopee_service import ShopeeAPI, converter_links_shopee

logger = logging.getLogger("conekta-bots.worker")


class BotWorker:
    """Worker que gerencia um bot Telegram: regras de encaminhamento + fila de envio."""

    def __init__(self, bot_data: Bot):
        self.bot_id = bot_data.id
        self.bot_nome = bot_data.nome
        self.owner_id = bot_data.owner_id
        self.api_id = int(bot_data.api_id)
        self.api_hash = bot_data.api_hash
        self.session_string = bot_data.session_string
        self.client = TelegramClient(
            StringSession(self.session_string), self.api_id, self.api_hash
        )
        self.fila_envio: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._shopee_api: ShopeeAPI | None = None
        self._handlers_ativos: list = []
        self._hash_regras: str = ""

    # ------------------------------------------------------------------
    # Helpers para converter chat IDs (igual ao MVP)
    # ------------------------------------------------------------------

    @staticmethod
    def _processar_chat_id(chat_id: str):
        """Converte ID numérico para int; mantém string caso contrário ('me', '@canal')."""
        try:
            return int(chat_id)
        except (ValueError, TypeError):
            return chat_id

    @staticmethod
    def _processar_lista_chats(chat_id_str: str | None) -> list:
        """Aceita IDs separados por vírgula e converte cada um."""
        if not chat_id_str:
            return []
        items = [i.strip() for i in chat_id_str.split(",")]
        return [BotWorker._processar_chat_id(i) for i in items if i]

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Conecta o client, carrega regras e inicia loops."""
        logger.info("🤖 Worker iniciado: %s (id=%d)", self.bot_nome, self.bot_id)
        await self.client.connect()

        if not await self.client.is_user_authorized():
            logger.error("Bot %s não autorizado — session expirada?", self.bot_nome)
            return

        self._running = True

        # Carrega Shopee API logo no início (com log)
        self._carregar_shopee_api()

        await asyncio.gather(
            self._monitorar_regras_loop(),
            self._loop_fila(),
            self.client.run_until_disconnected(),
        )

    async def stop(self) -> None:
        """Para o worker e desconecta o client."""
        self._running = False
        await self.client.disconnect()
        logger.info("Worker parado: %s", self.bot_nome)

    # ------------------------------------------------------------------
    # Shopee API — com fallback e logs diagnósticos
    # ------------------------------------------------------------------

    def _carregar_shopee_api(self) -> ShopeeAPI | None:
        """Carrega ShopeeAPI a partir do BD. Tenta owner_id primeiro, fallback global."""
        db = SessionLocal()
        try:
            # 1) Busca por owner_id (multi-tenancy)
            config = ConfiguracaoService.get_by_owner(db, self.owner_id)

            # 2) Fallback: pega qualquer configuracao existente (compat MVP)
            if config is None:
                from sqlalchemy import select
                config = db.execute(select(Configuracao).limit(1)).scalar_one_or_none()
                if config:
                    logger.warning(
                        "[%s] Configuracao owner_id=%s não encontrada. "
                        "Usando config global (id=%d).",
                        self.bot_nome, self.owner_id, config.id,
                    )

            if config and config.shopee_app_id and config.shopee_app_secret:
                self._shopee_api = ShopeeAPI(
                    config.shopee_app_id, config.shopee_app_secret
                )
                logger.debug(
                    "[%s] ShopeeAPI carregada (app_id=%s)",
                    self.bot_nome, config.shopee_app_id,
                )
                return self._shopee_api

            # Nenhuma config encontrada — só loga uma vez
            logger.debug(
                "[%s] Nenhuma configuracao Shopee encontrada (owner_id=%s)",
                self.bot_nome, self.owner_id,
            )
        except Exception as e:
            logger.error("[%s] Erro ao carregar ShopeeAPI: %s", self.bot_nome, e)
        finally:
            db.close()

        self._shopee_api = None
        return None

    def _get_shopee_api(self) -> ShopeeAPI | None:
        """Retorna a instância ShopeeAPI (lazy-load com cache)."""
        if self._shopee_api is not None:
            return self._shopee_api
        return self._carregar_shopee_api()

    # ------------------------------------------------------------------
    # Hot-reload de regras e credenciais (como no MVP)
    # ------------------------------------------------------------------

    async def _monitorar_regras_loop(self) -> None:
        """Re-carrega regras e credenciais Shopee a cada 3 segundos."""
        while self._running:
            try:
                await self._aplicar_regras()
                self._carregar_shopee_api()  # Atualiza credenciais se mudaram
            except Exception as e:
                logger.error("[%s] Erro no monitor de regras: %s", self.bot_nome, e)
            await asyncio.sleep(3)

    async def _aplicar_regras(self) -> None:
        """Compara hash das regras e re-registra handlers se mudaram."""
        db = SessionLocal()
        try:
            regras = RuleService.get_all_by_bot(db, self.bot_id)
            regras_ativas = [r for r in regras if r.ativo]

            # Snapshot para detectar mudanças
            snapshot = str([
                (r.id, r.nome, r.origem, r.destino, r.filtro, r.substituto,
                 r.bloqueios, r.somente_se_tiver, r.converter_shopee)
                for r in regras_ativas
            ])
            if snapshot == self._hash_regras:
                return  # Sem mudanças

            logger.info("🔄 [%s] Regras atualizadas (%d ativas)", self.bot_nome, len(regras_ativas))

            # Remove handlers antigos
            for h in self._handlers_ativos:
                self.client.remove_event_handler(h)
            self._handlers_ativos.clear()

            # Registra novos
            for regra in regras_ativas:
                self._registrar_handler(regra)

            self._hash_regras = snapshot
        finally:
            db.close()

    # ------------------------------------------------------------------
    # Handler de regra
    # ------------------------------------------------------------------

    def _registrar_handler(self, regra) -> None:
        """Registra um event handler para uma regra específica."""
        origens = self._processar_lista_chats(regra.origem)
        regra_id = regra.id
        regra_nome = regra.nome
        destino = self._processar_chat_id(regra.destino)
        filtro = regra.filtro
        substituto = regra.substituto
        bloqueios = regra.bloqueios
        somente_se_tiver = regra.somente_se_tiver
        regra_converter_shopee = regra.converter_shopee

        async def handler(event):
            texto = event.message.text or ""
            texto_lower = texto.lower()

            # Filtro: bloqueia se contiver palavras bloqueadas (case-insensitive)
            if bloqueios:
                palavras_bloqueadas = [p.strip() for p in bloqueios.split(",")]
                if any(p.strip().lower() in texto_lower for p in palavras_bloqueadas if p.strip()):
                    return

            # Filtro: só encaminha se contiver palavras obrigatórias (case-insensitive)
            if somente_se_tiver:
                palavras_obrigatorias = [p.strip() for p in somente_se_tiver.split(",") if p.strip()]
                achou = False
                for p in palavras_obrigatorias:
                    if re.search(p, texto, re.IGNORECASE) or p.lower() in texto_lower:
                        achou = True
                        break
                if not achou:
                    return

            # Filtro: regex ou substring
            if filtro and filtro not in texto:
                return

            # Substituição (suporta regex como no MVP)
            mensagem_final = texto
            if filtro and substituto:
                mensagem_final = re.sub(filtro, substituto, mensagem_final, flags=re.IGNORECASE)
            elif substituto:
                pares = substituto.split("|")
                for par in pares:
                    partes = par.split("->")
                    if len(partes) == 2:
                        mensagem_final = mensagem_final.replace(
                            partes[0].strip(), partes[1].strip()
                        )

            # Conversão de links Shopee
            if regra_converter_shopee:
                try:
                    shopee_api = self._get_shopee_api()
                    if shopee_api:
                        logger.debug(
                            "[%s] Convertendo links Shopee (regra: %s)",
                            self.bot_nome, regra_nome,
                        )
                        mensagem_final = await converter_links_shopee(
                            mensagem_final, shopee_api
                        )
                    else:
                        logger.warning(
                            "[%s] Shopee habilitada na regra '%s' mas API não configurada!",
                            self.bot_nome, regra_nome,
                        )
                except Exception as e:
                    logger.error(
                        "[%s] Erro na conversão Shopee (regra %s): %s",
                        self.bot_nome, regra_nome, e,
                    )

            # Coloca na fila: texto + mídia separados
            media = event.message.media
            await self.fila_envio.put((destino, mensagem_final, media, regra_nome, event.chat_id))

        self.client.add_event_handler(
            handler, events.NewMessage(chats=origens)
        )
        self._handlers_ativos.append(handler)
        logger.debug(
            "[%s] Handler registrado: regra '%s' (id=%d) origens=%s destino=%s shopee=%s",
            self.bot_nome, regra_nome, regra_id, origens, destino, regra_converter_shopee,
        )

    # ------------------------------------------------------------------
    # Fila de envio
    # ------------------------------------------------------------------

    async def _loop_fila(self) -> None:
        """Processa fila de envio de mensagens."""
        while self._running:
            try:
                destino, texto, media, regra_nome, origem = await asyncio.wait_for(
                    self.fila_envio.get(), timeout=1.0
                )
            except asyncio.TimeoutError:
                continue

            db = SessionLocal()
            try:
                # Envia com mídia (foto/vídeo/doc) ou só texto
                if media:
                    await self.client.send_file(
                        destino, media, caption=texto or None
                    )
                else:
                    await self.client.send_message(destino, texto)

                LogService.create(
                    db,
                    bot_id=self.bot_id,
                    bot_nome=self.bot_nome,
                    origem=str(origem),
                    destino=str(destino),
                    status="sucesso",
                    mensagem=(texto or "")[:200],
                )
                logger.info(
                    "🚀 [%s] %s → %s (regra: %s)",
                    self.bot_nome, origem, destino, regra_nome,
                )
                # Anti-flood: delay aleatório entre envios
                await asyncio.sleep(random.uniform(2, 5))
            except FloodWaitError as e:
                logger.warning(
                    "[%s] FloodWait do Telegram: aguardando %ds",
                    self.bot_nome, e.seconds,
                )
                await asyncio.sleep(e.seconds)
                # Recoloca na fila para tentar novamente
                await self.fila_envio.put((destino, texto, media, regra_nome, origem))
            except Exception as e:
                LogService.create(
                    db,
                    bot_id=self.bot_id,
                    bot_nome=self.bot_nome,
                    origem=str(origem),
                    destino=str(destino),
                    status="erro",
                    mensagem=str(e)[:200],
                )
                logger.error(
                    "[%s] Erro ao enviar %s → %s: %s",
                    self.bot_nome, origem, destino, e,
                )
            finally:
                db.close()

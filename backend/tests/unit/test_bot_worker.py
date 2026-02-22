"""Testes unitários para BotWorker (helpers e lógica de envio)."""

import asyncio

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.bot import Bot
from app.workers.bot_worker import BotWorker


class TestBotWorkerHelpers:
    """Testes para helpers estáticos."""

    def test_processar_chat_id_numero(self):
        """Converte string numérica para int."""
        assert BotWorker._processar_chat_id("123456") == 123456
        assert BotWorker._processar_chat_id("-1001234567890") == -1001234567890

    def test_processar_chat_id_string_mantem(self):
        """Mantém strings como 'me' ou '@canal'."""
        assert BotWorker._processar_chat_id("me") == "me"
        assert BotWorker._processar_chat_id("@meucanal") == "@meucanal"

    def test_processar_chat_id_invalido(self):
        """Valores inválidos mantêm como string ou TypeError."""
        # "abc" não converte para int, retorna "abc"
        assert BotWorker._processar_chat_id("abc") == "abc"

    def test_processar_lista_chats_vazia(self):
        """Lista vazia ou None retorna []."""
        assert BotWorker._processar_lista_chats(None) == []
        assert BotWorker._processar_lista_chats("") == []

    def test_processar_lista_chats_multiplos(self):
        """Aceita IDs separados por vírgula."""
        result = BotWorker._processar_lista_chats("123, 456, @canal")
        assert result == [123, 456, "@canal"]

    def test_processar_lista_chats_espacos(self):
        """Remove espaços ao redor dos itens."""
        result = BotWorker._processar_lista_chats("  100  ,  200  ")
        assert result == [100, 200]


class TestBotWorkerSendMessage:
    """Testes para envio de mensagem (com mock do client)."""

    @pytest.fixture
    def mock_bot(self):
        """Bot mock para testes."""
        bot = MagicMock(spec=Bot)
        bot.id = 1
        bot.nome = "TestBot"
        bot.owner_id = 1
        bot.api_id = "12345"
        bot.api_hash = "abc123"
        bot.session_string = "any"
        return bot

    def test_send_message_via_client_mock(self, mock_bot):
        """Verifica que send_message é chamado com destino e texto corretos."""
        mock_client = MagicMock()
        mock_client.send_message = AsyncMock()
        mock_session = MagicMock()
        with patch(
            "app.workers.bot_worker.StringSession", return_value=mock_session
        ), patch(
            "app.workers.bot_worker.TelegramClient", return_value=mock_client
        ):
            worker = BotWorker(mock_bot)

            async def _send():
                await worker.client.send_message("me", "Mensagem de teste")

            asyncio.run(_send())
            mock_client.send_message.assert_awaited_once_with(
                "me", "Mensagem de teste"
            )

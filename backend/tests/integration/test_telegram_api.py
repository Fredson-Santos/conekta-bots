"""
Testes de integração que usam a API real do Telegram para enviar mensagens.

Configure no .env:
  TELEGRAM_TEST_API_ID=12345
  TELEGRAM_TEST_API_HASH=abcdef123456...
  TELEGRAM_TEST_SESSION_STRING=1BVtsOH0Bu...

Obtenha em my.telegram.org (API ID/Hash) e faça login via app para obter session.
Se não configurado, os testes são ignorados (skip).
"""

import asyncio
import os

import pytest
from telethon import TelegramClient
from telethon.sessions import StringSession

# Credenciais para testes (opcional)
TELEGRAM_API_ID = os.getenv("TELEGRAM_TEST_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_TEST_API_HASH")
TELEGRAM_SESSION = os.getenv("TELEGRAM_TEST_SESSION_STRING")

pytestmark = pytest.mark.skipif(
    not all([TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION]),
    reason="Configure TELEGRAM_TEST_API_ID, TELEGRAM_TEST_API_HASH e TELEGRAM_TEST_SESSION_STRING no .env",
)


@pytest.fixture
def telegram_client():
    """Cliente Telethon conectado para testes."""
    client = TelegramClient(
        StringSession(TELEGRAM_SESSION),
        int(TELEGRAM_API_ID),
        TELEGRAM_API_HASH,
    )
    return client


def test_send_message_to_me(telegram_client):
    """Envia mensagem de teste para Saved Messages ('me') e verifica recebimento."""

    async def _run():
        await telegram_client.connect()

        if not await telegram_client.is_user_authorized():
            pytest.skip("Session não autorizada — faça login para obter session_string")

        try:
            # Envia mensagem de teste
            msg_text = "[ConektaBots Test] Mensagem de teste unitário"
            sent = await telegram_client.send_message("me", msg_text)

            assert sent.id is not None
            assert sent.text == msg_text

            # Busca a mensagem enviada para confirmar
            messages = await telegram_client.get_messages("me", limit=1)
            assert len(messages) >= 1
            assert messages[0].text == msg_text

            # Remove a mensagem de teste (opcional, limpa o chat)
            await sent.delete()
        finally:
            await telegram_client.disconnect()

    asyncio.run(_run())


def test_check_connection_service(telegram_client):
    """Testa telegram_service.check_connection com credenciais reais."""
    from app.services import telegram_service

    async def _run():
        return await telegram_service.check_connection(
            session_string=TELEGRAM_SESSION,
            api_id=TELEGRAM_API_ID,
            api_hash=TELEGRAM_API_HASH,
        )

    result = asyncio.run(_run())
    assert result is True


def test_send_and_receive_roundtrip(telegram_client):
    """Envia mensagem e confirma roundtrip via get_messages."""

    async def _run():
        await telegram_client.connect()

        if not await telegram_client.is_user_authorized():
            pytest.skip("Session não autorizada")

        try:
            texto = "[Test Roundtrip] " + str(__import__("time").time())
            sent = await telegram_client.send_message("me", texto)

            # Pega mensagem pelo ID
            fetched = await telegram_client.get_messages("me", ids=sent.id)
            assert fetched is not None
            assert fetched.text == texto

            await sent.delete()
        finally:
            await telegram_client.disconnect()

    asyncio.run(_run())

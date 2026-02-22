"""Testes unitários para telegram_service com mocks."""

import asyncio

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services import telegram_service


def _run(coro):
    """Executa coroutine em evento síncrono."""
    return asyncio.run(coro)


class TestTelegramServiceStartAuth:
    """Testes para start_auth."""

    def test_start_auth_retorna_auth_id(self):
        """start_auth retorna um auth_id válido."""
        with patch.object(
            telegram_service, "TelegramClient", autospec=True
        ) as mock_client_class:
            mock_client = AsyncMock()
            mock_client.connect = AsyncMock()
            mock_client.send_code_request = AsyncMock()
            mock_client_class.return_value = mock_client

            auth_id = _run(
                telegram_service.start_auth(
                    api_id="12345", api_hash="abc123", phone="+5511999999999"
                )
            )

            assert auth_id is not None
            assert len(auth_id) == 32  # uuid4.hex
            mock_client.connect.assert_awaited_once()
            mock_client.send_code_request.assert_awaited_once_with("+5511999999999")

    def test_start_auth_armazena_pending_auth(self):
        """start_auth armazena dados em _pending_auths."""
        with patch.object(
            telegram_service, "TelegramClient", autospec=True
        ) as mock_client_class:
            mock_client = AsyncMock()
            mock_client.connect = AsyncMock()
            mock_client.send_code_request = AsyncMock()
            mock_client_class.return_value = mock_client

            auth_id = _run(
                telegram_service.start_auth(
                    api_id="999", api_hash="hash", phone="+5511111111111"
                )
            )

            assert auth_id in telegram_service._pending_auths
            pending = telegram_service._pending_auths[auth_id]
            assert pending["phone"] == "+5511111111111"
            assert pending["api_id"] == "999"
            assert pending["api_hash"] == "hash"
            assert pending["client"] is mock_client

            # Limpa para não afetar outros testes
            telegram_service._pending_auths.pop(auth_id, None)


class TestTelegramServiceVerifyCode:
    """Testes para verify_code."""

    def test_verify_code_auth_id_invalido(self):
        """verify_code levanta ValueError para auth_id inexistente."""
        with pytest.raises(ValueError, match="auth_id inválido ou expirado"):
            _run(telegram_service.verify_code("auth_inexistente", "12345"))

    def test_verify_code_sucesso_retorna_session_e_phone(self):
        """verify_code retorna (session_string, phone) em caso de sucesso."""
        mock_client = MagicMock()
        mock_client.sign_in = AsyncMock()
        mock_client.session = MagicMock()
        mock_client.session.save.return_value = "session_string_abc123"
        mock_client.disconnect = AsyncMock()

        auth_id = "test_auth_123"
        telegram_service._pending_auths[auth_id] = {
            "client": mock_client,
            "phone": "+5511999999999",
            "api_id": "12345",
            "api_hash": "abc",
        }

        try:
            session_string, phone = _run(
                telegram_service.verify_code(auth_id, "12345")
            )

            assert session_string == "session_string_abc123"
            assert phone == "+5511999999999"
            mock_client.sign_in.assert_awaited_once_with("+5511999999999", "12345")
            mock_client.disconnect.assert_awaited_once()
            assert auth_id not in telegram_service._pending_auths
        finally:
            telegram_service._pending_auths.pop(auth_id, None)

    def test_verify_code_falha_sign_in_levanta_value_error(self):
        """verify_code propaga erro do sign_in como ValueError."""
        mock_client = AsyncMock()
        mock_client.sign_in = AsyncMock(side_effect=Exception("Código inválido"))
        mock_client.disconnect = AsyncMock()

        auth_id = "test_auth_fail"
        telegram_service._pending_auths[auth_id] = {
            "client": mock_client,
            "phone": "+5511999999999",
            "api_id": "12345",
            "api_hash": "abc",
        }

        try:
            with pytest.raises(ValueError, match="Falha na verificação"):
                _run(telegram_service.verify_code(auth_id, "00000"))
        finally:
            telegram_service._pending_auths.pop(auth_id, None)


class TestTelegramServiceCheckConnection:
    """Testes para check_connection."""

    def test_check_connection_true(self):
        """check_connection retorna True quando autorizado."""
        with patch.object(
            telegram_service, "StringSession", return_value=MagicMock()
        ), patch.object(
            telegram_service, "TelegramClient", autospec=True
        ) as mock_client_class:
            mock_client = AsyncMock()
            mock_client.connect = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)
            mock_client.disconnect = AsyncMock()
            mock_client_class.return_value = mock_client

            result = _run(
                telegram_service.check_connection(
                    session_string="valid_session",
                    api_id="12345",
                    api_hash="abc123",
                )
            )

            assert result is True

    def test_check_connection_false(self):
        """check_connection retorna False quando não autorizado."""
        with patch.object(
            telegram_service, "StringSession", return_value=MagicMock()
        ), patch.object(
            telegram_service, "TelegramClient", autospec=True
        ) as mock_client_class:
            mock_client = AsyncMock()
            mock_client.connect = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=False)
            mock_client.disconnect = AsyncMock()
            mock_client_class.return_value = mock_client

            result = _run(
                telegram_service.check_connection(
                    session_string="invalid_session",
                    api_id="12345",
                    api_hash="abc123",
                )
            )

            assert result is False

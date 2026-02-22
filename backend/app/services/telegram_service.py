"""Abstração do Telethon para autenticação de userbots via telefone."""

import uuid

from telethon import TelegramClient
from telethon.sessions import StringSession


# Cache in-memory para sessões de autenticação pendentes
_pending_auths: dict[str, dict] = {}


async def start_auth(api_id: str, api_hash: str, phone: str) -> str:
    """Inicia fluxo de autenticação — envia código SMS.

    Returns:
        auth_id: identificador único para completar a verificação.
    """
    auth_id = uuid.uuid4().hex
    client = TelegramClient(StringSession(), int(api_id), api_hash)
    await client.connect()
    await client.send_code_request(phone)

    _pending_auths[auth_id] = {
        "client": client,
        "phone": phone,
        "api_id": api_id,
        "api_hash": api_hash,
    }
    return auth_id


async def verify_code(auth_id: str, code: str) -> tuple[str, str]:
    """Verifica código SMS e retorna (session_string, phone).

    Raises:
        ValueError: se auth_id não existir ou código inválido.
    """
    auth = _pending_auths.pop(auth_id, None)
    if not auth:
        raise ValueError("auth_id inválido ou expirado")

    client: TelegramClient = auth["client"]
    phone = auth["phone"]
    try:
        await client.sign_in(phone, code)
        session_string = client.session.save()
        return session_string, phone
    except Exception as e:
        raise ValueError(f"Falha na verificação: {e}") from e
    finally:
        await client.disconnect()


async def check_connection(session_string: str, api_id: str, api_hash: str) -> bool:
    """Verifica se uma session_string ainda é válida."""
    client = TelegramClient(StringSession(session_string), int(api_id), api_hash)
    try:
        await client.connect()
        return await client.is_user_authorized()
    finally:
        await client.disconnect()

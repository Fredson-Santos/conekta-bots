"""Integração com a API de Afiliados da Shopee.

Portada do ConektaBots-mvp1.0/worker.py — lógica idêntica:
- ShopeeAPI: autenticação HMAC-SHA256 + GraphQL generateShortLink
- converter_links_shopee: regex para encontrar URLs Shopee e converter
"""

import asyncio
import hashlib
import json
import logging
import re
import time

import requests

logger = logging.getLogger("conekta-bots.shopee")

# Regex para capturar links Shopee (shopee.com.br e s.shopee.com.br)
SHOPEE_URL_REGEX = re.compile(
    r'https?://(?:s\.)?shopee\.com(?:\.br)?/[^\s\)\]\\"]+', re.IGNORECASE
)


class ShopeeAPI:
    """Client para a API de Afiliados da Shopee (GraphQL)."""

    def __init__(self, app_id: str, secret: str):
        self.app_id = app_id
        self.secret = secret
        self.base_url = "https://open-api.affiliate.shopee.com.br"
        self.endpoint = "/graphql"

    def _gen_sig(self, payload: str) -> tuple[str, str]:
        ts = str(int(time.time()))
        msg = f"{self.app_id}{ts}{payload}{self.secret}"
        sig = hashlib.sha256(msg.encode("utf-8")).hexdigest()
        return sig, ts

    def _auth_header(self, payload: str) -> dict[str, str]:
        sig, ts = self._gen_sig(payload)
        auth_h = f"SHA256 Credential={self.app_id}, Timestamp={ts}, Signature={sig}"
        return {"Authorization": auth_h, "Content-Type": "application/json"}

    def gen_link(self, url: str) -> str | None:
        """Gera um link afiliado curto para uma URL Shopee."""
        sub_ids = ["conekta"]
        gq = {
            "query": f'mutation {{ generateShortLink(input: {{ originUrl: "{url}", subIds: {json.dumps(sub_ids)} }}) {{ shortLink }} }}'
        }
        payload = json.dumps(gq)
        headers = self._auth_header(payload)
        try:
            logger.debug("Shopee API request: url=%s app_id=%s", url, self.app_id)
            resp = requests.post(
                f"{self.base_url}{self.endpoint}",
                headers=headers,
                json=gq,
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                link = (
                    data.get("data", {})
                    .get("generateShortLink", {})
                    .get("shortLink")
                )
                if link:
                    logger.info("🔗 Shopee: %s → %s", url, link)
                    return link
                logger.warning("⚠️ Shopee API 200 sem link: %s", data)
            else:
                logger.warning("Shopee API erro %d: %s", resp.status_code, resp.text)
        except Exception as e:
            logger.error("Shopee exceção: %s", e)
        return None


async def converter_links_shopee(texto: str, shopee_api: ShopeeAPI) -> str:
    """Encontra todos os links Shopee no texto e converte para links afiliados."""
    if not texto:
        return texto

    links = SHOPEE_URL_REGEX.findall(texto)
    if not links:
        return texto

    novo_texto = texto
    for link in links:
        novo_link = await asyncio.to_thread(shopee_api.gen_link, link)
        if novo_link:
            novo_texto = novo_texto.replace(link, novo_link)

    return novo_texto

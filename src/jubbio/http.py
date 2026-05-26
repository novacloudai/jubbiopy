from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

import aiohttp

from .exceptions import HTTPError, VoiceError


@dataclass(frozen=True, slots=True)
class VoiceJoinInfo:
    """
    Minimal shape expected from the REST endpoint that returns voice server info.

    The actual Jubbio API payload can evolve; keep this dataclass narrow and extend
    it as you discover real fields.
    """

    endpoint: str
    token: str
    session_id: str


class HTTPClient:
    """
    REST/HTTP client for the Jubbio platform.

    This class is intentionally small and async-only (aiohttp).
    """

    def __init__(
        self,
        *,
        base_url: str = "https://api.jubbio.com",
        session: Optional[aiohttp.ClientSession] = None,
        auth_token: Optional[str] = None,
        auth_header: str = "Authorization",
        auth_prefix: str = "",
        timeout_s: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = session
        self._auth_token = auth_token
        self._auth_header = auth_header
        self._auth_prefix = auth_prefix
        self._timeout = aiohttp.ClientTimeout(total=timeout_s)

    async def __aenter__(self) -> "HTTPClient":
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise RuntimeError("HTTPClient session not initialized. Use it as an async context manager.")
        return self._session

    def set_auth_token(self, token: str) -> None:
        self._auth_token = token

    def _make_headers(self) -> dict[str, str]:
        if not self._auth_token:
            return {}
        if self._auth_prefix:
            return {self._auth_header: f"{self._auth_prefix}{self._auth_token}"}
        return {self._auth_header: self._auth_token}

    async def _request(self, method: str, path: str, *, json_body: Any | None = None) -> Any:
        url = f"{self._base_url}{path}"
        headers = self._make_headers()

        async with self.session.request(
            method,
            url,
            headers=headers,
            json=json_body,
        ) as resp:
            # Fail fast with useful error payload.
            text = await resp.text()
            if resp.status >= 400:
                raise HTTPError(resp.status, method, path, text)

            if not text:
                return None

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text

    async def send_message(self, channel_id: str, content: str) -> Any:
        """
        Sends a message to the given channel.

        NOTE: Endpoint path is a placeholder and should be aligned with real @jubbio/core REST routes.
        """

        payload = {"channel_id": channel_id, "content": content}
        return await self._request("POST", "/v1/messages", json_body=payload)

    async def join_voice_channel(self, guild_id: str, channel_id: str) -> VoiceJoinInfo:
        """
        Returns voice server info required to start a voice session.

        NOTE: Endpoint path + payload shape are placeholders until the real API contract is known.
        """

        payload = {"guild_id": guild_id, "channel_id": channel_id}
        data = await self._request("POST", "/v1/voice/join", json_body=payload)
        if not isinstance(data, dict):
            raise VoiceError(f"Unexpected voice join response: {data!r}")

        # Keep mapping explicit to surface missing keys early.
        endpoint = data["endpoint"]
        token = data["token"]
        session_id = data["session_id"]
        return VoiceJoinInfo(endpoint=endpoint, token=token, session_id=session_id)


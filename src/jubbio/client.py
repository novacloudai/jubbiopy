from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, Optional, TypeVar

import aiohttp

from .gateway import GatewayConfig, JubboWebSocket
from .http import HTTPClient
from .models import Message
from .voice import VoiceClient

T = TypeVar("T")


class Client:
    """
    Unified Jubbio client (core + voice) with a discord.py-like event API.
    """

    def __init__(
        self,
        *,
        base_http_url: str = "https://api.jubbio.com",
        gateway_url: str = "ws://api.jubbio.com/gateway",
    ) -> None:
        self._events: dict[str, Callable[..., Awaitable[Any]]] = {}
        self._http: Optional[HTTPClient] = None
        self._voice: Optional[VoiceClient] = None
        self._gateway: Optional[JubboWebSocket] = None
        self._session: Optional[aiohttp.ClientSession] = None

        # If/when gateway exposes the bot user id, store it here.
        self.user_id: str = ""

        self._base_http_url = base_http_url
        self._gateway_url = gateway_url

    # ----------------------------
    # Event API (@client.event)
    # ----------------------------
    def event(self, coro: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        """
        Register an async callback as an event handler.

        Example:

            client = Client()

            @client.event
            async def on_message(message: Message):
                ...
        """

        name = getattr(coro, "__name__", None) or ""
        if not name:
            raise ValueError("Event handler must be a function with a __name__.")
        self._events[name] = coro
        return coro

    async def _dispatch(self, event_name: str, *args: Any) -> None:
        handler = self._events.get(event_name)
        if handler is None:
            return
        await handler(*args)

    async def dispatch(self, event: str, *args: Any) -> None:
        """
        Dispatch by gateway event name.

        If you call `dispatch("message", ...)` it will look for `on_message`.
        """

        await self._dispatch(f"on_{event}", *args)

    # ----------------------------
    # Gateway -> Client handlers
    # ----------------------------
    async def _on_gateway_message_create(self, data: dict[str, Any]) -> None:
        if self._http is None:
            return
        msg = Message.from_payload(data, http=self._http)

        # User-facing event.
        await self._dispatch("on_message", msg)

    async def _on_gateway_voice_state_update(self, data: dict[str, Any]) -> None:
        if self._voice is not None:
            await self._voice.on_voice_state_update(data)
        await self._dispatch("on_voice_state_update", data)

    async def _on_gateway_ready(self, data: dict[str, Any]) -> None:
        """
        Best-effort bot identity extraction.

        The gateway contract is unknown here; extend parsing as you learn real payload fields.
        """

        user = data.get("user") or {}
        user_id = (
            data.get("user_id")
            or data.get("bot_id")
            or user.get("id")
            or user.get("user_id")
            or ""
        )
        self.user_id = str(user_id)

    # ----------------------------
    # Run/login
    # ----------------------------
    async def _run(self, token: str) -> None:
        async with aiohttp.ClientSession() as session:
            self._session = session

            self._http = HTTPClient(
                base_url=self._base_http_url,
                session=session,
                auth_token=token,
                auth_header="Authorization",
                auth_prefix="",
            )

            self._voice = VoiceClient(self, http=self._http)
            self._gateway = JubboWebSocket(
                self,
                config=GatewayConfig(url=self._gateway_url),
            )

            await self._gateway.start(token)

    def run(self, token: str) -> None:
        """
        Start the gateway loop and login with the given token.

        Note: This is a blocking call (asyncio.run).
        """

        asyncio.run(self._run(token))


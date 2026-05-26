from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Optional

import websockets
from websockets.legacy.client import WebSocketClientProtocol


@dataclass(frozen=True, slots=True)
class GatewayConfig:
    url: str = "ws://api.jubbio.com/gateway"
    ping_interval_s: float = 20.0
    identify_timeout_s: float = 10.0


class JubboWebSocket:
    """
    Jubbio gateway websocket listener.

    It receives gateway events and forwards them to `Client.dispatch(...)`.

    The payload contract for event names + payload shapes may differ from real life;
    this class is written to be easily adjusted without touching the rest of the client.
    """

    def __init__(self, client: Any, *, config: GatewayConfig | None = None) -> None:
        self._client = client
        self._config = config or GatewayConfig()
        self._ws: Optional[WebSocketClientProtocol] = None
        self._closing = asyncio.Event()

    @property
    def ws(self) -> WebSocketClientProtocol:
        if self._ws is None:
            raise RuntimeError("WebSocket not connected yet.")
        return self._ws

    async def start(self, token: str) -> None:
        async with websockets.connect(
            self._config.url,
            ping_interval=self._config.ping_interval_s,
            max_queue=32,
        ) as ws:
            self._ws = ws

            # Identification format is intentionally a placeholder.
            await ws.send(json.dumps({"type": "IDENTIFY", "token": token}))

            # Main receive loop.
            try:
                async for raw in ws:
                    if raw is None:
                        continue
                    await self._handle_raw(raw)
            finally:
                self._closing.set()
                self._ws = None

    async def close(self) -> None:
        self._closing.set()
        if self._ws is not None:
            await self._ws.close()

    async def _handle_raw(self, raw: Any) -> None:
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8", errors="replace")
        if not isinstance(raw, str):
            return

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            # Ignore non-JSON frames.
            return

        # Common shape for event-driven gateways is either:
        #   {"type": "MESSAGE_CREATE", "data": {...}}
        # or:
        #   {"event": "MESSAGE_CREATE", "payload": {...}}
        event_type = payload.get("type") or payload.get("event")
        data = payload.get("data") or payload.get("payload") or payload

        if not isinstance(event_type, str):
            return

        event_type = event_type.upper()

        if event_type == "MESSAGE_CREATE":
            await self._client._on_gateway_message_create(data)
        elif event_type == "VOICE_STATE_UPDATE":
            await self._client._on_gateway_voice_state_update(data)
        elif event_type == "READY":
            await self._client._on_gateway_ready(data)
        else:
            await self._client.dispatch(event_type.lower(), data)


from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Optional

from .http import HTTPClient, VoiceJoinInfo


@dataclass(frozen=True, slots=True)
class VoiceState:
    guild_id: str
    channel_id: str
    user_id: str


class VoiceClient:
    """
    Voice subsystem skeleton.

    This is designed to be extended later with:
    - RTP/UDP transport
    - codec (Opus) integration
    - WebRTC simulation if required by the Jubbio voice contract
    """

    def __init__(self, client: Any, *, http: HTTPClient) -> None:
        self._client = client
        self._http = http
        self._join_task: Optional[asyncio.Task[None]] = None
        self._state: Optional[VoiceState] = None
        self._running = asyncio.Event()
        self._join_lock = asyncio.Lock()
        self._join_info: Optional[VoiceJoinInfo] = None

    @property
    def state(self) -> Optional[VoiceState]:
        return self._state

    async def join_voice_channel(self, *, guild_id: str, channel_id: str) -> None:
        """
        Join a voice channel.

        This calls the REST endpoint to obtain voice server connection details.
        UDP/WebRTC streaming management is left as a safe async skeleton.
        """

        info = await self._http.join_voice_channel(guild_id, channel_id)
        await self._start_voice_session(info=info, guild_id=guild_id, channel_id=channel_id)

    async def start_voice_session_from_gateway(
        self, *, info: VoiceJoinInfo, guild_id: str, channel_id: str
    ) -> None:
        """
        Gateway payload zaten voice server bilgilerini taşıyorsa (endpoint/token/session_id),
        burada REST join çağrısı yapmadan oturumu başlat.
        """

        await self._start_voice_session(info=info, guild_id=guild_id, channel_id=channel_id)

    async def leave(self) -> None:
        self._running.clear()
        self._state = None
        self._join_info = None
        if self._join_task is not None and not self._join_task.done():
            self._join_task.cancel()
        self._join_task = None

    async def _start_voice_session(self, *, info: VoiceJoinInfo, guild_id: str, channel_id: str) -> None:
        # If already running, stop previous attempt.
        if self._join_task is not None and not self._join_task.done():
            self._join_task.cancel()

        self._join_info = info
        self._state = VoiceState(
            guild_id=guild_id,
            channel_id=channel_id,
            user_id=getattr(self._client, "user_id", ""),
        )
        self._running.set()

        # Placeholder streaming loop; replace with real transport/codec.
        async def streaming_loop() -> None:
            while self._running.is_set():
                # TODO: Implement UDP/WebRTC/RTP streaming here.
                await asyncio.sleep(0.5)

        self._join_task = asyncio.create_task(streaming_loop(), name="jubbio-voice-stream")
        # Prevent immediate cancellation by returning after starting loop.
        await asyncio.sleep(0)

    async def on_voice_state_update(self, data: dict[str, Any]) -> None:
        """
        Called by the main client when gateway emits VOICE_STATE_UPDATE.

        Default behavior:
        - If the payload indicates the bot moved/joined, keep internal state aligned.
        - If a leave is detected, stop voice session.
        """

        # Payload contract is unknown; parse conservatively.
        user_id = str(data.get("user_id") or data.get("userId") or "")
        guild_id = str(data.get("guild_id") or data.get("guildId") or "")
        channel_id = str(data.get("channel_id") or data.get("channelId") or "")

        bot_user_id = str(getattr(self._client, "user_id", ""))

        # If gateway includes the affected user id, only react when it's the bot itself.
        if bot_user_id and user_id and user_id != bot_user_id:
            return

        # Leave conditions: missing/zero channel id.
        if not channel_id or channel_id in {"0", "null", "None"}:
            if self._state is not None:
                await self.leave()
            return

        # Ensure we have a meaningful current state before comparing.
        current_channel_id = self._state.channel_id if self._state is not None else ""

        # Avoid redundant joins.
        if current_channel_id == channel_id and self._running.is_set():
            return

        async with self._join_lock:
            # State may have changed while awaiting the lock.
            current_channel_id = self._state.channel_id if self._state is not None else ""
            if current_channel_id == channel_id and self._running.is_set():
                return

            if not guild_id:
                # Can't join without guild context; keep internal state best-effort.
                self._state = VoiceState(guild_id=guild_id, channel_id=channel_id, user_id=user_id or bot_user_id)
                return
            # Some gateway contracts may include voice server details directly.
            endpoint = data.get("endpoint")
            token = data.get("token")
            session_id = data.get("session_id") or data.get("sessionId")
            if isinstance(endpoint, str) and isinstance(token, str) and isinstance(session_id, str):
                info = VoiceJoinInfo(endpoint=endpoint, token=token, session_id=session_id)
                await self.start_voice_session_from_gateway(
                    info=info, guild_id=guild_id, channel_id=channel_id
                )
            else:
                await self.join_voice_channel(guild_id=guild_id, channel_id=channel_id)


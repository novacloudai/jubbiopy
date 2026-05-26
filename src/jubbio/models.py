from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .http import HTTPClient


@dataclass(frozen=True, slots=True)
class User:
    id: str
    username: str
    is_bot: bool = False


@dataclass(slots=True)
class Message:
    id: str
    content: str
    channel_id: str
    author: User

    # Not part of Jubbio payload; injected by Client so reply can call HTTP.
    _http: Optional[HTTPClient] = None

    @classmethod
    def from_payload(cls, payload: dict[str, Any], *, http: Optional[HTTPClient] = None) -> "Message":
        """
        Parse a Jubbio MESSAGE_CREATE payload into a typed Message.

        Keep parsing conservative; if your payload differs, extend this mapping.
        """

        author_payload = payload.get("author") or {}
        author = User(
            id=str(author_payload.get("id") or payload.get("author_id") or ""),
            username=str(author_payload.get("username") or author_payload.get("name") or "unknown"),
            is_bot=bool(author_payload.get("is_bot", False)),
        )

        return cls(
            id=str(payload.get("id") or payload.get("message_id") or ""),
            content=str(payload.get("content") or payload.get("text") or ""),
            channel_id=str(payload.get("channel_id") or payload.get("channelId") or ""),
            author=author,
            _http=http,
        )

    async def reply(self, content: str) -> Any:
        if self._http is None:
            raise RuntimeError("Message.reply() requires an HTTPClient instance.")
        return await self._http.send_message(self.channel_id, content)


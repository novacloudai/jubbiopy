from __future__ import annotations


class JubbioError(Exception):
    """Base exception for all Jubbio errors."""


class HTTPError(JubbioError):
    """Raised when the Jubbio REST API returns an error response."""

    def __init__(self, status: int, method: str, path: str, body: str) -> None:
        self.status = status
        self.method = method
        self.path = path
        self.body = body
        super().__init__(f"HTTP {status} on {method} {path}: {body}")


class GatewayError(JubbioError):
    """Raised on unexpected gateway / websocket failures."""


class VoiceError(JubbioError):
    """Raised when a voice session cannot be established or encounters a fatal error."""


class AuthenticationError(JubbioError):
    """Raised when the bot token is rejected by the gateway or REST API."""

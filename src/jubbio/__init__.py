from .client import Client
from .exceptions import (
    AuthenticationError,
    GatewayError,
    HTTPError,
    JubbioError,
    VoiceError,
)
from .gateway import GatewayConfig, JubboWebSocket
from .http import HTTPClient, VoiceJoinInfo
from .models import Message, User
from .voice import VoiceClient, VoiceState

__version__ = "0.1.0"

__all__ = [
    # Core
    "Client",
    # HTTP
    "HTTPClient",
    "VoiceJoinInfo",
    # Gateway
    "JubboWebSocket",
    "GatewayConfig",
    # Voice
    "VoiceClient",
    "VoiceState",
    # Models
    "User",
    "Message",
    # Exceptions
    "JubbioError",
    "HTTPError",
    "GatewayError",
    "VoiceError",
    "AuthenticationError",
    # Version
    "__version__",
]

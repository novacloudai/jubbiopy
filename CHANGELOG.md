# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-26

### Added

- Initial PyPI release of the unified `jubbio` Python client.
- Async REST client (`HTTPClient`) with `send_message` and `join_voice_channel`.
- Gateway websocket listener (`JubboWebSocket`) with event dispatch.
- Voice subsystem skeleton (`VoiceClient`) with join/leave and streaming placeholder.
- Typed models: `User`, `Message` (with `reply()`), `VoiceState`, `VoiceJoinInfo`.
- discord.py-style `@client.event` API on `Client`.
- Exception hierarchy: `JubbioError`, `HTTPError`, `GatewayError`, `VoiceError`, `AuthenticationError`.
- PEP 561 `py.typed` marker for static type checkers.

[0.1.0]: https://github.com/jubbio/jubbiopy/releases/tag/v0.1.0

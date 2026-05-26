# jubbio

[![PyPI version](https://img.shields.io/pypi/v/jubbio.svg)](https://pypi.org/project/jubbio/)
[![Python versions](https://img.shields.io/pypi/pyversions/jubbio.svg)](https://pypi.org/project/jubbio/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Pure-async Python client for the [Jubbio](https://jubbio.com) platform.

`@jubbio/core` and `@jubbio/voice` are combined into a single package: REST messaging, gateway events, and voice session management — no JavaScript runtime required.

Built with **asyncio**, **aiohttp**, and **websockets**.

## Requirements

- Python 3.10+
- `aiohttp >= 3.9`
- `websockets >= 12`

## Installation

```bash
pip install jubbio
```

From source (development):

```bash
git clone https://github.com/jubbio/jubbiopy.git
cd jubbiopy
pip install -e ".[dev]"
```

## Quick start

```python
from jubbio import Client, Message

client = Client()

@client.event
async def on_message(message: Message):
    if message.author.is_bot:
        return
    if message.content == "!ping":
        await message.reply("Pong!")

@client.event
async def on_voice_state_update(data: dict):
    print("voice state:", data)

client.run("YOUR_BOT_TOKEN")
```

See [`examples/bot.py`](examples/bot.py) for a fuller example with environment variables.

## Features

| Module | Description |
|---|---|
| `Client` | Main entry point with `@client.event` decorator and `run(token)` |
| `HTTPClient` | Async REST calls: `send_message`, `join_voice_channel` |
| `JubboWebSocket` | Gateway listener for `MESSAGE_CREATE`, `VOICE_STATE_UPDATE`, etc. |
| `VoiceClient` | Voice join/leave with async streaming skeleton (UDP/WebRTC ready) |
| `Message.reply()` | Reply to a message directly from the model object |

## Environment variables (examples)

| Variable | Default | Description |
|---|---|---|
| `JUBBIO_TOKEN` | — | Bot authentication token |
| `JUBBIO_BASE_URL` | `https://api.jubbio.com` | REST API base URL |
| `JUBBIO_GATEWAY_URL` | `ws://api.jubbio.com/gateway` | Gateway websocket URL |

## Development

```bash
pip install -e ".[dev]"

# Lint
ruff check src tests

# Type check
mypy src/jubbio

# Tests
pytest
```

## Publishing to PyPI

```bash
pip install -e ".[publish]"

# Clean previous builds
python -m build --clean

# Validate artifacts before upload
twine check dist/*

# Upload to TestPyPI first (recommended)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

You need a [PyPI account](https://pypi.org/account/register/) and an API token.
Use `TWINE_USERNAME=__token__` and `TWINE_PASSWORD=pypi-...` (never commit tokens).

## Notes

- REST endpoint paths (`/v1/messages`, `/v1/voice/join`) are placeholders; align them with the real Jubbio API contract as it stabilizes.
- `VoiceClient` streaming loop is a skeleton — RTP/UDP/WebRTC transport can be plugged in later.

## License

MIT — see [LICENSE](LICENSE).

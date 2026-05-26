"""
Minimal Jubbio bot örneği.

Çalıştırmak için:
    pip install -e ..          (proje kökünde)
    python bot.py
"""

from __future__ import annotations

import os

from jubbio import Client, Message

client = Client(
    base_http_url=os.getenv("JUBBIO_BASE_URL", "https://api.jubbio.com"),
    gateway_url=os.getenv("JUBBIO_GATEWAY_URL", "ws://api.jubbio.com/gateway"),
)


@client.event
async def on_message(message: Message) -> None:
    """Her yeni mesajda tetiklenir."""

    # Bot'un kendi mesajlarını yoksay.
    if message.author.is_bot:
        return

    if message.content.lower() == "!ping":
        await message.reply("Pong! 🏓")
        return

    if message.content.lower().startswith("!echo "):
        text = message.content[6:]
        await message.reply(text)


@client.event
async def on_voice_state_update(data: dict) -> None:
    """Bir kullanıcı ses kanalına girip/çıktığında tetiklenir."""

    user_id = data.get("user_id") or data.get("userId") or "(bilinmiyor)"
    channel_id = data.get("channel_id") or data.get("channelId")

    if channel_id:
        print(f"[Voice] {user_id} → kanal {channel_id}")
    else:
        print(f"[Voice] {user_id} kanaldan ayrıldı")


if __name__ == "__main__":
    token = os.environ.get("JUBBIO_TOKEN")
    if not token:
        raise SystemExit("JUBBIO_TOKEN ortam değişkeni tanımlı değil.")

    client.run(token)

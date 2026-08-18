import os
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("WEBAPP_URL", "https://example.com/miniapp")

from telegram_bot.bot import start


@pytest.mark.asyncio
async def test_start_sends_webapp_button():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()

    await start(update, context)

    update.message.reply_text.assert_called_once()
    _, kwargs = update.message.reply_text.call_args
    markup = kwargs["reply_markup"]
    button = markup.inline_keyboard[0][0]
    assert button.web_app.url == "https://example.com/miniapp"
    assert "capturas" in button.text.lower()

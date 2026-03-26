import pytest

from src.bot import main as bot_main


@pytest.mark.asyncio
async def test_bot_main_wires_dispatcher(monkeypatch):
    class FakeBot:
        def __init__(self, _token):
            self.token = _token
            self.session = self

        async def close(self):
            return None

    class FakeDispatcher:
        def include_router(self, _router):
            return None

        async def start_polling(self, _bot):
            return None

    monkeypatch.setattr(bot_main, "Bot", FakeBot)
    monkeypatch.setattr(bot_main, "Dispatcher", FakeDispatcher)
    await bot_main.main()

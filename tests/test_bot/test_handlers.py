import pytest

from src.bot.handlers import admin, callbacks, commands
from src.bot.keyboards.inline import order_actions_keyboard


class DummyMessage:
    def __init__(self):
        self.answers = []
        self.chat = type("Chat", (), {"id": 101})()
        self.from_user = type("User", (), {"id": 123456789})()
        self.text = ""

    async def answer(self, text: str, **kwargs):
        self.answers.append((text, kwargs))


class DummyCallback:
    def __init__(self):
        self.called = False
        self.data = "cancel:order-1"
        self.message = type("Msg", (), {"chat": type("Chat", (), {"id": 101})()})()
        self.from_user = type("User", (), {"id": 123456789})()

    async def answer(self, _text: str = "", **kwargs):
        self.called = True


@pytest.mark.asyncio
async def test_command_handlers(monkeypatch):
    class FakeApi:
        async def list_orders(self, limit=5):
            return [{"id": "order-1", "status": "pending", "amount": 10.0}]

        async def get_order_status(self, order_id: str):
            return "processing"

    class FakePublisher:
        async def publish_telegram_notification(self, payload):
            return True

    monkeypatch.setattr(commands, "api_client", FakeApi())
    monkeypatch.setattr(commands, "publisher", FakePublisher())

    msg = DummyMessage()
    msg.text = "/status order-1"
    await commands.start_command(msg)
    await commands.orders_command(msg)
    await commands.subscribe_command(msg)
    await commands.status_command(msg)
    await commands.help_command(msg)
    assert len(msg.answers) == 5


@pytest.mark.asyncio
async def test_admin_handler(monkeypatch):
    monkeypatch.setattr(admin.settings, "telegram_admin_ids", "123456789")
    msg = DummyMessage()
    await admin.admin_panel(msg)
    assert msg.answers
    forbidden = DummyMessage()
    forbidden.from_user = type("User", (), {"id": 999})()
    await admin.admin_panel(forbidden)
    assert "Доступ запрещен." in forbidden.answers[0][0]


@pytest.mark.asyncio
async def test_callback_handler(monkeypatch):
    class FakePublisher:
        async def publish_telegram_notification(self, payload):
            return True

    monkeypatch.setattr(callbacks, "publisher", FakePublisher())
    query = DummyCallback()
    await callbacks.callback_handler(query)
    assert query.called


def test_inline_keyboard_builder():
    kb = order_actions_keyboard("123")
    assert kb.inline_keyboard

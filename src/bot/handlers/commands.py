from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from structlog import get_logger

from src.bot.keyboards.inline import order_actions_keyboard
from src.bot.services import BotApiClient, BotNotificationPublisher

router = Router()
logger = get_logger(__name__)
api_client = BotApiClient()
publisher = BotNotificationPublisher()


@router.message(Command("start"))
async def start_command(message: Message) -> None:
    await message.answer("Добро пожаловать в OrderBot. Используйте /help для списка команд.")


@router.message(Command("orders"))
async def orders_command(message: Message) -> None:
    orders = await api_client.list_orders(limit=5)
    if orders is None:
        await message.answer("Сервис заказов временно недоступен. Попробуйте позже.")
        return
    if not orders:
        await message.answer("Активных заказов пока нет.")
        return

    lines = ["Активные заказы:"]
    for order in orders:
        lines.append(f"- {order['id']} | {order['status']} | {order['amount']}")
    first_id = str(orders[0]["id"])
    await message.answer("\n".join(lines), reply_markup=order_actions_keyboard(first_id))


@router.message(Command("subscribe"))
async def subscribe_command(message: Message) -> None:
    payload = {
        "chat_id": message.chat.id,
        "user_id": message.from_user.id if message.from_user else 0,
        "event": "subscribe",
    }
    ok = await publisher.publish_telegram_notification(payload)
    if ok:
        await message.answer("Подписка на уведомления активирована.")
    else:
        await message.answer("Не удалось связаться с очередью уведомлений. Попробуйте позже.")


@router.message(Command("status"))
async def status_command(message: Message) -> None:
    text = message.text or ""
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /status <order_id>")
        return

    order_id = parts[1].strip()
    status = await api_client.get_order_status(order_id)
    if status is None:
        await message.answer("Сервис заказов временно недоступен. Попробуйте позже.")
        return
    await message.answer(f"Статус заказа {order_id}: {status}")


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "Команды:\n"
        "/start - регистрация\n"
        "/orders - список активных заказов\n"
        "/subscribe - подписка на уведомления\n"
        "/status <order_id> - статус заказа\n"
        "/help - помощь"
    )

from aiogram import Router
from aiogram.types import CallbackQuery
from structlog import get_logger

from src.bot.services import BotNotificationPublisher

router = Router()
logger = get_logger(__name__)
publisher = BotNotificationPublisher()


@router.callback_query()
async def callback_handler(query: CallbackQuery) -> None:
    callback_data = query.data or ""
    action, _, order_id = callback_data.partition(":")
    if action in {"cancel", "status"} and order_id:
        ok = await publisher.publish_telegram_notification(
            {
                "chat_id": query.message.chat.id if query.message else 0,
                "user_id": query.from_user.id if query.from_user else 0,
                "action": action,
                "order_id": order_id,
            }
        )
        if not ok:
            await query.answer("Очередь недоступна", show_alert=True)
            return

    await query.answer("OK")

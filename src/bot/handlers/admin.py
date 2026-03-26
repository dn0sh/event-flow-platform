from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.config.settings import get_settings

router = Router()
settings = get_settings()


@router.message(Command("admin"))
async def admin_panel(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else -1
    if user_id not in settings.telegram_admin_id_set:
        await message.answer("Доступ запрещен.")
        return
    await message.answer("Админ-панель: управление операторами и очередями.")

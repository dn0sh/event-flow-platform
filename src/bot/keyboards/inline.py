from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def order_actions_keyboard(order_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Просмотр", callback_data=f"view:{order_id}"),
                InlineKeyboardButton(text="Обновить статус", callback_data=f"status:{order_id}"),
                InlineKeyboardButton(text="Отменить", callback_data=f"cancel:{order_id}"),
            ]
        ]
    )

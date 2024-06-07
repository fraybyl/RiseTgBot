from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_personal_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data="back_personal"),
            ]
        ]
    )
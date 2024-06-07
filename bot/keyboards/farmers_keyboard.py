from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_farmers_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Подсчитать стратегию", callback_data="strategy"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_farmers"),
            ]
        ]
    )

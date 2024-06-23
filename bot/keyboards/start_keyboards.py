from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Магазин", callback_data="shop"),
                InlineKeyboardButton(text="Фермерам", callback_data="farmers"),
            ],
            [
                InlineKeyboardButton(text="Личный кабинет", callback_data="personal"),
            ],
            [
                InlineKeyboardButton(text="Отзывы", url='https://t.me/risemarket'),
                InlineKeyboardButton(text="Поддержка", url='https://t.me/RiseMarket_support'),
            ]
        ]
    )

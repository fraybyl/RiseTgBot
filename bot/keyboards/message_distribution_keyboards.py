from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_ban_dump_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Закрыть❌", callback_data="cancel_dump_accounts"),
            ]
        ]
    )
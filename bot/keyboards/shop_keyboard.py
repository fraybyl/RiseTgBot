from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_shop_kb() -> InlineKeyboardMarkup: # shop
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Аккаунты LIMIT", callback_data="limit_accounts"),
            ],
            [
                InlineKeyboardButton(text="Steam Gift Code", callback_data="steam_gift_code"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_shop"),
            ]
        ]
    )
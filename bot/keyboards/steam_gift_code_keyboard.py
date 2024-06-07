from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_steam_gift_code_kb() -> InlineKeyboardMarkup: # steam_gift_code
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="5$", callback_data="gift_5"),
            ],
            [
                InlineKeyboardButton(text="10$", callback_data="gift_10"),
            ],
            [
                InlineKeyboardButton(text="15$", callback_data="gift_15"),
            ],
            [
                InlineKeyboardButton(text="20$", callback_data="gift_20"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_gift_code"),
            ]
        ]
    )

def get_currency_gift_code_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Купить", callback_data="buy_gift"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_gift_list"),
            ]
        ]
    )

def get_payment_gift_code_kb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Отмена", callback_data="cancel_gift_code"),
            ]
        ]
    )
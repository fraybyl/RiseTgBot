from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_limit_accounts_kb() -> InlineKeyboardMarkup: # limit_accounts
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Аккаунты без SDA", callback_data="non_sda_accounts"),
            ],
            [
                InlineKeyboardButton(text="Аккаунты с SDA", callback_data="sda_accounts"),
            ],
            [
                InlineKeyboardButton(text="Аккаунты с SDA + 2 lvl", callback_data="sda_2lvl_accounts"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_limit_acc"),
            ]
        ]
    )
    
def get_currency_limit_acc_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Купить", callback_data="buy_limit_acc"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_limit_acc_list"),
            ]
        ]
    )

def get_payment_limit_acc_kb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Отмена", callback_data="cancel_limit_acc"),
            ]
        ]
    )
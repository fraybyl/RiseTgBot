from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_cancel_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Отмена", callback_data="cancel_buy"),
            ]
        ]
    )
        
def get_payment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Оплатить", callback_data="make_payment")
            ],
            [
                InlineKeyboardButton(text="Использовать бонусы", callback_data="use_bonus_payment")
            ],
            [
                InlineKeyboardButton(text="Отмена", callback_data="cancel_buy"),
            ]
        ]
    )
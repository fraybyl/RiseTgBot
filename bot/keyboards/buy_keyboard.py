from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_cancel_buy_kb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Отмена", callback_data="cancel_buy"),
            ]
        ]
    )
        
def get_payment_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Оплатить", callback_data="payment")
            ],
            [
                InlineKeyboardButton(text="Использовать бонусы", callback_data="use_bonuse_payment")
            ],
            [
                InlineKeyboardButton(text="Отмена", callback_data="cancel_buy"),
            ]
        ]
    )
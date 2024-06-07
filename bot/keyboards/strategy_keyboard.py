from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_strategy_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Консервативная стратегия", callback_data="conservative_strategy"),
            ],
            [
                InlineKeyboardButton(text="Умеренная стратегия", callback_data="moderate_strategy"),
            ],
            [
                InlineKeyboardButton(text="Агрессивная стратегия", callback_data="aggressive_strategy"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_strategy"),
            ]
        ]
    )
    
def get_calculated_cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Отмена", callback_data="cancel_strategy")
            ]
        ]
    )
    
def get_calculated_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data="back_strategy")
            ]
        ]
    )
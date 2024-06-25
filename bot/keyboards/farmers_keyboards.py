from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_farmers_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Подсчитать стратегию", callback_data="strategy"),
            ],
            [
                InlineKeyboardButton(text="Подсчитать инвентарь", callback_data="inventory"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_start"),
            ]
        ]
    )


def get_strategy_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Агрессивная стратегия", callback_data="aggressive_strategy")
            ],
            [
                InlineKeyboardButton(text="Умеренная стратегия", callback_data="moderate_strategy"),
            ],
            [
                InlineKeyboardButton(text="Консервативная стратегия", callback_data="conservative_strategy"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_farmers"),
            ]
        ]
    )


def get_cancel_strategy_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='В начало', callback_data='back_farmers')
            ],
            [
                InlineKeyboardButton(text='Назад', callback_data="back_strategy")
            ]
        ]
    )


def get_inventory_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Личная статистика", callback_data="personal_accounts")
            ],
            [
                InlineKeyboardButton(text='Назад', callback_data="back_farmers")
            ]
        ]
    )


def get_personal_inventory_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Добавить аккаунты", callback_data="add_accounts")
            ],
            [
                InlineKeyboardButton(text="Получить аккаунты", callback_data="get_accounts")
            ],
            [
                InlineKeyboardButton(text="Удалить аккаунты", callback_data="remove_accounts")
            ],
            [
                InlineKeyboardButton(text='Назад', callback_data="back_inventory")
            ]
        ]
    )


def get_personal_inventory_settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Назад', callback_data="back_personal_inventory")
            ]
        ]
    )

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
                InlineKeyboardButton(text="Общая статистика", callback_data="accounts_statistics")
            ],
            [
                InlineKeyboardButton(text='Добавить аккаунты', callback_data="add_accounts")
            ],
            [
                InlineKeyboardButton(text='Действия с аккаунтами', callback_data="accounts_actions")
            ],
            [
                InlineKeyboardButton(text='Назад', callback_data="back_farmers")
            ]
        ]
    )


def get_inventory_settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data="back_inventory"),
            ]
        ]
    )


def get_accounts_settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Получить список аккаунтов", callback_data="dump_accounts")
            ],
            [
                InlineKeyboardButton(text="Удалить аккаунты", callback_data="remove_accounts")
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_inventory"),
            ]
        ]
    )

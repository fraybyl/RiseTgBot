from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_personal_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад↩️", callback_data="back_start"),
            ]
        ]
    )

def get_admins_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="админ панель", callback_data="admin_panel"),
            ],
            [
                InlineKeyboardButton(text="Назад↩️", callback_data="back_start"),
            ]
        ]
    )

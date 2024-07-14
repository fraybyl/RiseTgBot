from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.db_requests import get_all_categories, get_products_by_category, get_product_by_id

def get_admins_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Добавить товары📉", callback_data="add_products"),
            ],
            [
                InlineKeyboardButton(text="Создать рассылку🔗", callback_data="mailing_list"),
            ],
            [
                InlineKeyboardButton(text="Закрыть❌", callback_data="personal"),
            ]
        ]
    )

# def get_categories_kb() -> InlineKeyboardMarkup:
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(text="кагеория 1", callback_data="add"),
#             ],
#             [
#                 InlineKeyboardButton(text="кагеория 2", callback_data="category_2"),
#             ],
#             [
#                 InlineKeyboardButton(text="новая залупа", callback_data="category_new"),
#             ],
#             [
#                 InlineKeyboardButton(text="Назад", callback_data="admin_panel"),
#             ]
#         ]
#     )

async def get_categories_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    categories = await get_all_categories()
    kb.row(InlineKeyboardButton(text="Новая категория", callback_data="adding_new"))
    kb.row(InlineKeyboardButton(text="Удалить категорию", callback_data="adding_delete"))
    for category in categories:
        kb.row(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))


    kb.row(InlineKeyboardButton(text="назад", callback_data="admin_panel"))

    return kb.as_markup()

async def get_all_categories_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    categories = await get_all_categories()

    for category in categories:
        kb.row(InlineKeyboardButton(text=category.name, callback_data=f"dell_{category.name}"))
    kb.row(InlineKeyboardButton(text="назад", callback_data="admin_panel"))

    return kb.as_markup()

def get_mailing_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Редактировать", callback_data="edit_mail")
            ],
            [
                InlineKeyboardButton(text="Отправить", callback_data="send_mail")
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="close_mail")
            ],
        ]
    )
def get_close_category_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data="add_products")
            ]
        ]
    )

def get_close_mailing_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data="admin_panel")
            ]
        ]
    )

def add_category_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Отправить", callback_data="send_adding")
            ]
        ]
    )


def confirmation_delete_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Удалить", callback_data="delete_name")
            ],
            [
                InlineKeyboardButton(text="назад", callback_data="add_products")
            ]
        ]
    )
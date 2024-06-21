from aiogram import Router
from aiogram.types import CallbackQuery

from bot.database.db_requests import get_category_by_id
from bot.keyboards.shop_keyboards import get_products_kb
from bot.utils.edit_media import edit_message_media

router = Router(name=__name__)


@router.callback_query(lambda query: query.data.startswith("category_"))
async def handle_products_category(query: CallbackQuery):
    category_id = int(query.data.split("_")[1])
    category = await get_category_by_id(category_id)
    await edit_message_media(query, category.photo_filename, await get_products_kb(category_id))
    await query.answer()


@router.callback_query(lambda query: query.data.startswith("back_product_"))
async def handle_back_products(query: CallbackQuery):
    category_id = int(query.data.split("_")[2])
    category = await get_category_by_id(category_id)
    await edit_message_media(query, category.photo_filename, await get_products_kb(category_id))
    await query.answer()

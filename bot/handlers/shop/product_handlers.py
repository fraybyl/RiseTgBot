from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.database.db_requests import get_product_by_id
from bot.keyboards.shop_keyboards import get_product_desc_kb
from bot.utils.edit_media import edit_message_media

router = Router(name=__name__)


@router.callback_query(lambda query: query.data.startswith("product_"))
async def handle_product(query: CallbackQuery):
    product_id = int(query.data.split("_")[1])
    product = await get_product_by_id(product_id)
    await edit_message_media(query, product.photo_filename, await get_product_desc_kb(product_id),
                             caption=product.label)


@router.callback_query(lambda query: query.data.startswith("back_order_"))
async def handle_back_products(query: CallbackQuery, state: FSMContext):
    product_id = int(query.data.split("_")[2])
    product = await get_product_by_id(product_id)
    await state.clear()
    await edit_message_media(query, product.photo_filename, await get_product_desc_kb(product_id),
                             caption=product.label)

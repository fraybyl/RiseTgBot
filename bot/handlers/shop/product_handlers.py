from aiogram import Router
from aiogram.types import Message, CallbackQuery
from bot.keyboards.user_kb import get_products_kb, get_buy_order_kb
from fluent.runtime import FluentLocalization
from aiogram.fsm.context import FSMContext
from bot.database.db_requests import get_category_by_id, get_product_by_id
from bot.utils import utils

router = Router(name=__name__)

@router.callback_query(lambda query: query.data.startswith("category_"))
async def handle_products_category(query: CallbackQuery):
    category_id = int(query.data.split("_")[1])
    category = await get_category_by_id(category_id)
    await utils.edit_message_media(query, category.photo_filename, await get_products_kb(category_id))
    await query.answer()

@router.callback_query(lambda query: query.data.startswith("product_"))
async def handle_product(query: CallbackQuery):
    product_id = int(query.data.split("_")[1])
    product = await get_product_by_id(product_id)
    await utils.edit_message_media(query, product.photo_filename, await get_buy_order_kb(product_id), caption=product.label)
    await query.answer()
    
@router.callback_query(lambda query: query.data.startswith("back_product_"))
async def handle_back_products(query: CallbackQuery):
    category_id = int(query.data.split("_")[2])
    category = await get_category_by_id(category_id)
    await utils.edit_message_media(query, category.photo_filename, await get_products_kb(category_id))
    await query.answer()
    
@router.callback_query(lambda query: query.data.startswith("back_order_"))
async def handle_back_products(query: CallbackQuery, state: FSMContext):
    product_id = int(query.data.split("_")[2])
    product = await get_product_by_id(product_id)
    await state.clear()
    await utils.edit_message_media(query, product.photo_filename, await get_buy_order_kb(product_id), caption=product.label)
    await query.answer()
    
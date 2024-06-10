# handlers/steam_gift_code_handlers.py
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.utils.photo_answer_util import edit_message_media
from bot.keyboards.shop_keyboard import get_shop_kb
from bot.keyboards.steam_gift_code_keyboard import get_steam_gift_code_kb, get_currency_gift_code_kb, get_payment_gift_code_kb
from bot.database.db_requests import get_product_by_name
from bot.states.order_states import OrderStates
from bot.utils.utils import escape_characters
from loader import bot

router = Router()

@router.callback_query(lambda query: query.data in ["steam_gift_code", "gift_5", "gift_10", "gift_15", "gift_20"])
async def handle_gift_code_callback(query: CallbackQuery, state: FSMContext):
    if query.data == "steam_gift_code":
        await edit_message_media(query, "RISE_GIFT_CODE", get_steam_gift_code_kb())
    else:
        await state.update_data(order_name=query.data)
        await edit_message_media(query, "RISE_GIFT_CODE", get_currency_gift_code_kb())

@router.callback_query(lambda query: query.data == "buy_gift")
async def handle_buy_gift_code_callback(query: CallbackQuery, state: FSMContext):
    order_name = (await state.get_data()).get('order_name')
    product = await get_product_by_name(order_name)
    chat_id, message_id = await edit_message_media(
        query, "RISE_GIFT_CODE", get_payment_gift_code_kb(), 
        caption=escape_characters(f"Введите желаемое количество.\n В наличии: {product.quantity}.")
    )
    await state.set_state(OrderStates.WAITING_QUANTITY)
    await state.update_data(chat_id=chat_id, message_id=message_id)

@router.callback_query(lambda query: query.data in ["back_gift_code", "back_gift_list", "cancel_gift_code"])
async def handle_back_gift_code_callback(query: CallbackQuery, state: FSMContext):
    await state.clear()
    if query.data == "back_gift_code":
        await edit_message_media(query, "RISE_SHOP", get_shop_kb())
    else:
        await edit_message_media(query, "RISE_GIFT_CODE", get_steam_gift_code_kb())
# handlers/steam_limit_accounts_handlers.py
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.utils.photo_answer_util import edit_message_media
from bot.keyboards.steam_limit_accounts_keyboard import get_limit_accounts_kb, get_currency_limit_acc_kb, get_cancel_limit_acc_kb
from bot.database.db_requests import get_product_by_name
from bot.keyboards.shop_keyboard import get_shop_kb
from bot.states.order_states import OrderStates
from bot.utils.utils import escape_characters
from loader import bot

router = Router()

@router.callback_query(lambda query: query.data in ["limit_accounts", "non_sda_accounts", "sda_accounts", "sda_2lvl_accounts"])
async def handle_limit_accounts_callback(query: CallbackQuery, state: FSMContext):
    if query.data == "limit_accounts":
        await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_limit_accounts_kb())
    else:
        await state.update_data(order_name=query.data)
        await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_currency_limit_acc_kb())

@router.callback_query(lambda query: query.data == "buy_limit_acc")
async def handle_buy_limit_acc_callback(query: CallbackQuery, state: FSMContext):
    order_name = (await state.get_data()).get('order_name')
    product = await get_product_by_name(order_name)
    chat_id, message_id = await edit_message_media(
        query, "RISE_LIMIT_ACCOUNT", get_cancel_limit_acc_kb(), 
        caption=escape_characters(f"Введите желаемое количество.\n В наличии: {product.quantity}.")
    )
    await state.set_state(OrderStates.WAITING_QUANTITY)
    await state.update_data(chat_id=chat_id, message_id=message_id)

@router.callback_query(lambda query: query.data in ["back_limit_acc_list", "cancel_limit_acc", "back_limit_acc"])
async def handle_back_limit_acc_callback(query: CallbackQuery, state: FSMContext):
    await state.clear()
    if query.data == "back_limit_acc":
        await edit_message_media(query, "RISE_SHOP", get_shop_kb())
    else:
        await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_limit_accounts_kb())

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.steam_gift_code_keyboard import get_steam_gift_code_kb, get_currency_gift_code_kb, get_payment_gift_code_kb
from bot.keyboards.shop_keyboard import get_shop_kb
from bot.utils.photo_answer_util import edit_message_media
from bot.states.order_states import OrderStates
from loader import bot

router = Router()

@router.callback_query(lambda query: query.data == "steam_gift_code")
async def handle_steam_gift_code_callback(query: CallbackQuery):
    await edit_message_media(query, "RISE_GIFT_CODE", get_steam_gift_code_kb())
    
@router.callback_query(lambda query: query.data == "gift_5")
async def handle_gift_code_five_callback(query: CallbackQuery, state: FSMContext):
    await state.update_data(order_name=query.data)
    await edit_message_media(query, "RISE_GIFT_CODE", get_currency_gift_code_kb())

@router.callback_query(lambda query: query.data == "gift_10")
async def handle_gift_code_ten_callback(query: CallbackQuery, state: FSMContext):
    await state.update_data(order_name=query.data)
    await edit_message_media(query, "RISE_GIFT_CODE", get_currency_gift_code_kb())
    
@router.callback_query(lambda query: query.data == "gift_15")
async def handle_gift_code_fifteen_callback(query: CallbackQuery, state: FSMContext):
    await state.update_data(order_name=query.data)
    await edit_message_media(query, "RISE_GIFT_CODE", get_currency_gift_code_kb())
    
@router.callback_query(lambda query: query.data == "gift_20")
async def handle_gift_code_twenty_callback(query: CallbackQuery, state: FSMContext):
    await state.update_data(order_name=query.data)
    await edit_message_media(query, "RISE_GIFT_CODE", get_currency_gift_code_kb())
    
@router.callback_query(lambda query: query.data == "buy_gift")
async def handle_buy_gift_code_callback(query: CallbackQuery, state: FSMContext):
    chat_id, message_id = await edit_message_media(query, "RISE_GIFT_CODE", get_payment_gift_code_kb(), caption="Введите желамое количество\\. В наличие: \\.")
    await state.set_state(OrderStates.WAITING_QUANTITY)
    await state.update_data(chat_id=chat_id, message_id=message_id)

@router.callback_query(lambda query: query.data in ["back_gift_code", "back_gift_list", "cancel_gift_code"])
async def handle_back_limit_acc_callback(query: CallbackQuery, state: FSMContext):
    await state.clear()
    if query.data == "back_gift_code":
        await edit_message_media(query, "RISE_SHOP", get_shop_kb())
    else:
        await edit_message_media(query, "RISE_GIFT_CODE", get_steam_gift_code_kb())
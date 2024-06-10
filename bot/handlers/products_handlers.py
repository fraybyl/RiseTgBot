from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards.user_kb import get_limit_acc_kb, get_buy_order_kb, get_gift_code_kb
from bot.handlers.error_handlers import handle_error_back
from fluent.runtime import FluentLocalization
from bot.utils import utils
router = Router()

valid_products = ['buy_sda_non', 'buy_sda', 'buy_sda_2lvl', 'buy_gift_5', 'buy_gift_10', 'buy_gift_15', 'buy_gift_20']

@router.callback_query(lambda query: query.data in ["limit_accounts", "steam_gift_code"])
async def handle_product_categories(query: CallbackQuery):
    keyboard_map = {
        "limit_accounts": (get_limit_acc_kb(), "RISE_LIMIT_ACCOUNT"),
        "steam_gift_code": (get_gift_code_kb(), "RISE_GIFT_CODE")
    }
    keyboard, media_type = keyboard_map[query.data]
    await utils.edit_message_media(query, media_type, keyboard)

@router.callback_query(lambda query: query.data in valid_products)
async def handle_product_selection(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    if not(query.data in valid_products):
        await handle_error_back(query, state)
        return
    else:
        await state.update_data(current_product=query.data)
        
        if('sda' in query.data):
            media_type = 'RISE_LIMIT_ACCOUNT'
        elif('gift' in query.data):
            media_type = 'RISE_GIFT_CODE'

        await utils.edit_message_media(query, media_type, get_buy_order_kb(), caption=l10n.format_value('product-select', {'productLabel': query.data}))


@router.callback_query(lambda query: query.data == "back_categories")
async def handle_back_categories_gift(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_product = data.get('current_product')
    
    if(not isinstance(current_product, str) or current_product is None):
        await handle_error_back(query, state)
        return
    
    if(current_product in ['buy_gift_5', 'buy_gift_10', 'buy_gift_15', 'buy_gift_20']):        
        await state.clear()
        await utils.edit_message_media(query, "RISE_GIFT_CODE", get_gift_code_kb())
        
    elif(current_product in ['buy_sda_non', 'buy_sda', 'buy_sda_2lvl']):
        await state.clear()
        await utils.edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_limit_acc_kb())
        
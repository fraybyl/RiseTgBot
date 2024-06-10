from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from bot.keyboards.user_kb import get_buy_order_kb, get_cancel_order_kb, get_gift_code_kb, get_limit_acc_kb
from fluent.runtime import FluentLocalization
from bot.states.order_states import OrderStates
from bot.handlers.error_handlers import handle_error_back
from bot.utils import utils

router = Router()

@router.callback_query(lambda query: query.data == "buy_product")
async def handle_buy_product(query: CallbackQuery, l10n: FluentLocalization, state: FSMContext):  
    
    data = await state.get_data()
    current_product: str = data.get('current_product')

    if(not isinstance(current_product, str) or current_product is None):
        await handle_error_back(query, state)
        return
    
    image_to_use: str
    
    if(current_product.startswith('buy_sda')):
        image_to_use = "RISE_LIMIT_ACCOUNT"
        
    elif(current_product.startswith('buy_gift')):
        image_to_use = "RISE_GIFT_CODE"
        
    else:
        await handle_error_back(query, state)
        return
    
    await utils.edit_message_media(query, image_to_use, get_cancel_order_kb(), 
                                   caption=l10n.format_value("product-info", {'productQuantity': 123, 'productPrice': 15}))
    
    await state.set_state(OrderStates.WAITING_QUANTITY)
    await state.update_data(previous_state=OrderStates.WAITING_QUANTITY)

@router.message(OrderStates.WAITING_QUANTITY)
async def process_quantity_input(message: Message, state: FSMContext, l10n: FluentLocalization):
    
    try:
        pass
    except:
        pass
    
@router.callback_query(lambda query: query.data == "back_order")
async def handle_back_order(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_product = data.get('current_product')
    current_state = data.get('previous_state')
    
    if(not isinstance(current_product, str) or current_product is None):
        await handle_error_back(query, state)
        return
    
    if(current_state is None):
        await handle_error_back(query, state)
        return

    if(current_product in ['buy_sda_non', 'buy_sda', 'buy_sda_2lvl']):
        if(current_state == OrderStates.WAITING_QUANTITY):
            await state.clear()
            await utils.edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_limit_acc_kb())
        elif(current_state in OrderStates.WAITING_PAYMENT | OrderStates.WAITING_BONUS_USE):
            await state.set_state(current_state)
            await utils.edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_limit_acc_kb(), caption=query.message.caption)
            
    if(current_product in ['buy_gift_5', 'buy_gift_10', 'buy_gift_15', 'buy_gift_20']):
        if(current_state == OrderStates.WAITING_QUANTITY):
            await state.clear()
            await utils.edit_message_media(query, "RISE_GIFT_CODE", get_gift_code_kb())
        elif(current_state in OrderStates.WAITING_PAYMENT | OrderStates.WAITING_BONUS_USE):
            await state.set_state(current_state)
            await utils.edit_message_media(query, "RISE_GIFT_CODE", get_gift_code_kb(), caption=query.message.caption)
    
    
    
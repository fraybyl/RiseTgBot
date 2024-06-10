from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from bot.keyboards.user_kb import get_buy_order_kb, get_cancel_order_kb, get_gift_code_kb, get_limit_acc_kb, get_payment_order_kb
from fluent.runtime import FluentLocalization
from bot.states.order_states import OrderStates
from bot.handlers.error_handlers import handle_error_back
from bot.utils import utils
from loader import bot, configJson
from bot.database.db_requests import get_product_by_name, get_user_by_telegram_id

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
    
    product = await get_product_by_name(current_product)
    
    message_id = await utils.edit_message_media(query, image_to_use, get_cancel_order_kb(), 
                                   caption=l10n.format_value("product-info", {'productQuantity': product.quantity, 'productPrice': product.price}))
    
    await state.set_state(OrderStates.WAITING_QUANTITY)
    await state.update_data(message_id=message_id)


@router.message(OrderStates.WAITING_QUANTITY)
async def process_product_quantity_input(message: Message, state: FSMContext, l10n: FluentLocalization):
    try:
        data = await state.get_data()
        message_id  = data.get('message_id')
        
        minimal_price = await configJson.get_config_value('minimal_price')
        min_quantity = 1
        
        await message.delete()
        if not message.text.isdigit() or int(message.text) < min_quantity:
            await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                           caption=l10n.format_value('buy-input', {'minQuantity': min_quantity, 'minimalPrice': minimal_price}),
                                           reply_markup=get_cancel_order_kb())
            return
        
        quantity_product = int(message.text)
        await state.update_data(quantity_product=quantity_product)
        
        await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                        caption=l10n.format_value('use-bonus', {'productLabel': "ХУЙ", 'quantity': quantity_product, 'bonusQuantity': 0}),
                                        reply_markup=get_payment_order_kb())
        
        await state.set_state(OrderStates.WAITING_PAYMENT)
    except:
        pass
    
@router.callback_query(lambda query: query.data == 'bonus_use_product', OrderStates.WAITING_PAYMENT)
async def handle_bonus_use(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    data = await state.get_data()
    current_product = data.get('current_product')
    
    product = await get_product_by_name(current_product)
    user = await get_user_by_telegram_id(query.from_user.id)
    
    minimal_price = await configJson.get_config_value('minimal_price')
    
    try:
        if not user.bonus_points:
            await query.message.edit_caption(caption=l10n.format_value('not-bonus'), reply_markup=get_payment_order_kb())
            return
        
        max_bonus = 10
        if max_bonus <= 0:
            await query.message.edit_caption(caption=l10n.format_value('cant-use-bonus', {'minimalPprice': minimal_price}), reply_markup=get_payment_order_kb())
            return
        
        await query.message.edit_caption(caption=l10n.format_value('choose-bonus', {'maxBonus': max_bonus}), reply_markup=get_cancel_order_kb())
        await state.set_state(OrderStates.WAITING_BONUS_USE)
        await state.update_data(previous_state=OrderStates.WAITING_PAYMENT)
    except:
        pass
    
@router.message(OrderStates.WAITING_BONUS_USE)
async def process_bonus_quantity_input(message: Message, state: FSMContext, l10n: FluentLocalization):
    data = await state.get_data()
    current_product = data.get('current_product')
    message_id = data.get('message_id')
    quantity_product = data.get('quantity_product')
    
    product = await get_product_by_name(current_product)
    
    try:
        await message.delete()
        if not message.text.isdigit() or int(message.text) < 0:
            await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                           caption=l10n.format_value('error-choose-bonus', {'maxBonus': 10}),
                                           reply_markup=get_cancel_order_kb())
            return
        
        bonus_use = int(message.text)
        await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                       caption=l10n.format_value('use-bonus', {'productLabel': product.label, 'quantity': quantity_product, 'bonusQuantity': bonus_use}),
                                       reply_markup=get_payment_order_kb())
        await state.update_data(bonus_use = bonus_use)
        await state.set_state(OrderStates.WAITING_PAYMENT)
    except:
        pass
    
@router.callback_query(lambda query: query.data == 'payment_product', OrderStates.WAITING_PAYMENT)
async def handle_payment_product(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    data = await state.get_data()
    current_product = data.get('current_product')
    quantity_product =  data.get('quantity_product')
    bonus_use =  data.get('bonus_use')
    await query.message.edit_caption(caption=f'{current_product}\n{quantity_product}\n{bonus_use or 0}', reply_markup=get_cancel_order_kb(), parse_mode="html")  
    

    
@router.callback_query(lambda query: query.data == "back_order")
async def handle_back_order(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    data = await state.get_data()
    current_product = data.get('current_product')
    previous_state = data.get('previous_state')
    current_state = await state.get_state()
    quantity_product = data.get('quantity_product')
    bonus_use = data.get('bonus_use')
    
    product = await get_product_by_name(current_product)
    
    print(current_state)
    if(not isinstance(current_product, str) or current_product is None):
        await handle_error_back(query, state)
        return
    
    if(current_state is None):
        await handle_error_back(query, state)
        return

    if(current_product in ['buy_sda_non', 'buy_sda', 'buy_sda_2lvl']):
        media_type = "RISE_LIMIT_ACCOUNT"
        
    if(current_product in ['buy_gift_5', 'buy_gift_10', 'buy_gift_15', 'buy_gift_20']):    
        media_type = "RISE_GIFT_CODE"
    
    if(current_state == OrderStates.WAITING_QUANTITY):
        await state.set_state(state=None)
        await state.update_data(current_product=current_product)
        await utils.edit_message_media(query, media_type, get_buy_order_kb())
    elif(current_state in [OrderStates.WAITING_BONUS_USE, OrderStates.WAITING_PAYMENT]):
        await state.set_state(previous_state)
        await utils.edit_message_media(query, media_type, get_payment_order_kb(), 
                                        caption=l10n.format_value('use-bonus', {'productLabel': product.label, 'quantity': quantity_product, 'bonusQuantity': bonus_use or 0}))
        
    
    
    
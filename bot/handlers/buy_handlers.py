import math
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.buy_keyboard import get_cancel_buy_kb, get_payment_kb
from bot.keyboards.shop_keyboard import get_shop_kb
from bot.utils.photo_answer_util import edit_message_media
from bot.states.order_states import OrderStates
from bot.utils.calculated_minimal_price import calculate_quantity_for_min_price, calculate_discount_for_price
from bot.database.db_requests import get_product_by_name, get_user_by_telegram_id
from loader import bot, configJson

router = Router()


@router.message(OrderStates.WAITING_QUANTITY)
async def handle_quantity_order(message: Message, state:FSMContext):
    data = await state.get_data()
    chatid = data.get('chat_id')
    messageid = data.get('message_id')
    
    order_name = data.get('order_name')
    minimal_price = await configJson.get_config_value('minimal_price')
    
    print(order_name)
    
    user = await get_user_by_telegram_id(message.from_user.id)
    product = await get_product_by_name(order_name)
    
    
    try:
        await message.delete()
        quantity = int(message.text)
        
        quantity_min = calculate_quantity_for_min_price(minimal_price, product.price, user.discount_percentage)
        if(quantity < quantity_min):
            await bot.edit_message_caption(chat_id=chatid, 
                                           message_id=messageid, 
                                           caption=character_escaped(f"Пожалуйста, введите количество не меньше {quantity_min}.\nТелеграмм не даст купить меньше, чем на {minimal_price}rub"),
                                           reply_markup=get_cancel_buy_kb())
            return
        await state.update_data(quantity_product=quantity)

        await bot.edit_message_caption(chat_id=chatid, 
                                       message_id=messageid, 
                                       caption=character_escaped(f"Вы выбрали {product.label}, количество: {quantity}. Нажмите 'Оплатить' для оплаты."), 
                                       reply_markup=get_payment_kb())
        await state.set_state(OrderStates.WAITING_PAYMENT)
    except ValueError:
        await bot.edit_message_caption(chat_id=chatid, message_id=messageid, caption="Пожалуйста, введите число\\.", reply_markup=get_cancel_buy_kb())
        
@router.callback_query(lambda query: query.data == 'use_bonuse_payment')
async def handle_bonus_use_callback(query: CallbackQuery, state: FSMContext):
    user = await get_user_by_telegram_id(query.from_user.id)
    
    if(not user.bonus_points):
        await query.message.edit_caption(caption="У вас нет бонусов для использования\\.", reply_markup=get_payment_kb())
        return
    
    data = await state.get_data()
    quantity_product = data.get('quantity_product')
    minimal_price = await configJson.get_config_value('minimal_price')
    order_name = data.get('order_name')
    
    product = await get_product_by_name(order_name)
    if(((calculate_discount_for_price(product.price, user.discount_percentage) * quantity_product) - minimal_price) <= 0):
        await query.message.edit_caption(caption=character_escaped(f"Вы не можете использовать бонусы для данной покупки.\nТелеграмм не даст купить меньше, чем на {minimal_price}rub"),
                                         reply_markup=get_payment_kb())
        return
    
    max_bonus_to_use = ((calculate_discount_for_price(product.price, user.discount_percentage) * quantity_product) - minimal_price)
    
    await state.set_state(OrderStates.WAITING_BONUS_USE)
    await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_cancel_buy_kb(), caption=character_escaped(f"Введите количество бонусов. Вы можете использовать: {math.trunc(max_bonus_to_use)}."))
    
@router.message(OrderStates.WAITING_BONUS_USE)
async def process_bonus_quantity_buy(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    data = await state.get_data()
    chatid = data.get('chat_id')
    messageid = data.get('message_id')    
    
    quantity_product = data.get('quantity_product')
    minimal_price = await configJson.get_config_value('minimal_price')
    order_name = data.get('order_name')
    
    product = await get_product_by_name(order_name)
    
    try:
        await message.delete()
        quantity = int(message.text)

            
        if quantity <= 0:
            await bot.edit_message_caption(chat_id=chatid, 
                                           message_id=messageid, 
                                           caption="Пожалуйста, введите положительное число\\.", 
                                           reply_markup=get_cancel_buy_kb())
            return
        
        max_bonus_to_use = ((calculate_discount_for_price(product.price, user.discount_percentage) * quantity_product) - minimal_price)
        
        if quantity > ((calculate_discount_for_price(product.price, user.discount_percentage) * quantity_product) - minimal_price):
            await bot.edit_message_caption(chat_id=chatid, 
                                           message_id=messageid, 
                                           caption=character_escaped(f"Пожалуйста, введите число не больше число {math.trunc(max_bonus_to_use)}."), 
                                           reply_markup=get_cancel_buy_kb())
            return
        
        await state.update_data(bonus=quantity)
        await bot.edit_message_caption(chat_id=chatid, 
                                message_id=messageid, 
                                caption=character_escaped(f"Вы используете: {quantity} бонусов. Нажмите 'Оплатить' для оплаты."), 
                                reply_markup=get_payment_kb())
        await state.set_state(OrderStates.WAITING_PAYMENT)
    except ValueError:
        await bot.edit_message_caption(chat_id=chatid, message_id=messageid, caption="Пожалуйста, введите число\\.", reply_markup=get_cancel_buy_kb())
        
@router.callback_query(OrderStates.WAITING_PAYMENT, lambda query: query.data == "payment")
async def handle_payment_callback(query: CallbackQuery, state: FSMContext):
    print('оплата')
        
def character_escaped(text: str):
    return text.replace('.', '\\.').replace('-', '\\-').replace('_', '\\_')


from aiogram import Router
from aiogram.types import Message, CallbackQuery
from bot.keyboards.user_kb import get_product_by_id, get_payment_order_kb, get_cancel_order_kb, get_payment_settings_kb
from fluent.runtime import FluentLocalization
from bot.database.db_requests import get_category_by_id, get_product_by_id, get_user_by_telegram_id
from aiogram.fsm.context import FSMContext
from bot.states.order_states import OrderStates
from bot.states.state_func import pop_state, push_state
from bot.utils.finance_math import calculate_quantity, calculate_max_bonus
from loader import bot, configJson

router = Router()

@router.callback_query(lambda query: query.data.startswith("buy_product_"))
async def handle_buy_product(query: CallbackQuery, state: FSMContext):
    product_id = int(query.data.split("_")[2])
    product = await get_product_by_id(product_id)
    user = await get_user_by_telegram_id(query.from_user.id)
    
    minimal_price = await configJson.get_config_value('minimal_price')
    min_quantity = calculate_quantity(product.price, user.discount_percentage, minimal_price)
    
    message = await query.message.edit_caption(caption=f"Введите количество не меньше {min_quantity}", reply_markup=get_cancel_order_kb(product_id))
    
    await state.set_state(OrderStates.WAITING_PRODUCT_QUANTITY)
    await state.update_data(min_quantity=min_quantity)
    await state.update_data(product=product)
    await state.update_data(user=user)
    await state.update_data(minimal_price=minimal_price)
    await state.update_data(message_id=message.message_id)
    
@router.message(OrderStates.WAITING_PRODUCT_QUANTITY, lambda message: message.text.isdigit() and int(message.text) > 0)
async def process_product_quantity(message: Message, state: FSMContext):
    data = await state.get_data()
    product = data.get('product')
    quantity_msg = int(message.text)
    message_id = data.get('message_id')
    min_quantity = data.get('min_quantity')
    await message.delete()
    
    if(quantity_msg < min_quantity):
        return
    
    await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, reply_markup=get_payment_order_kb(), caption=f"Число: {quantity_msg}")
    await state.update_data(quantity_product=quantity_msg)
    await state.update_data(previous_state=OrderStates.WAITING_PRODUCT_QUANTITY)
    await state.set_state(state=None)
    
@router.callback_query(lambda query: query.data == "bonus_use_product")
async def handle_bonus_use(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quantity_product = data.get('quantity_product')
    product = data.get('product')
    user = data.get('user')
    minimal_price = data.get('minimal_price')
    
    max_bonus = calculate_max_bonus(product.price * quantity_product, user.discount_percentage, minimal_price)
    
    await query.message.edit_caption(caption=f"Введите количество не больше {max_bonus}", reply_markup=get_payment_settings_kb())
    
    await state.update_data(max_bonus=max_bonus)
    await state.set_state(OrderStates.WAITING_BONUS_QUANTITY)
    
    
@router.message(OrderStates.WAITING_BONUS_QUANTITY, lambda message: message.text.isdigit() and int(message.text) > 0)
async def proccess_bonus_quantity(message: Message, state: FSMContext):
    data = await state.get_data()
    quantity_product = data.get('quantity_product')
    quantity_msg = int(message.text)
    message_id = data.get('message_id')
    max_bonus = data.get('max_bonus')
    
    await message.delete()
    
    if(quantity_msg > max_bonus):
        return
    
    await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, reply_markup=get_payment_order_kb(), caption=f"Число товара: {quantity_product}, Бонусы: {quantity_msg}")
    await state.update_data(quantity_bonus=quantity_msg)
    await state.update_data(previous_state=OrderStates.WAITING_BONUS_QUANTITY)
    await state.set_state(state=None)

@router.callback_query(lambda query: query.data == 'payment_product')
async def handle_payment_product(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quantity_product = data.get('quantity_product')
    quantity_bonus = data.get('quantity_bonus')
    await query.message.edit_caption(caption=f"Продукта {quantity_product}\n Бонусов: {quantity_bonus or 0}", reply_markup=get_payment_order_kb())

@router.callback_query(lambda query: query.data == "back_payment")
async def handle_back_payment(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_state = await state.get_state() 
    
    if(current_state is None):
        product = data.get('product')
        min_quantity = data.get('min_quantity')
        await query.message.edit_caption(caption=f"Введите количество не меньше {min_quantity}", reply_markup=get_cancel_order_kb(product.id))
        await state.update_data(quantity_product=None)
        await state.update_data(quantity_bonus=None)
        await state.set_state(OrderStates.WAITING_PRODUCT_QUANTITY)

    if(current_state == OrderStates.WAITING_BONUS_QUANTITY):
        quantity_product = data.get('quantity_product')
        quantity_bonus = data.get('quantity_bonus')
        caption=f"Число товара: {quantity_product}"
        if(quantity_bonus):
            caption=f"Число товара: {quantity_product}, Бонусы: {quantity_bonus}"
        await query.message.edit_caption(caption=caption, reply_markup=get_payment_order_kb())
        await state.set_state(state=None)
        


    

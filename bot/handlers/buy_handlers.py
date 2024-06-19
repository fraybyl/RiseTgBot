from aiogram import Router
from aiogram.types import Message, CallbackQuery
from bot.keyboards.user_kb import get_product_by_id, get_payment_order_kb, get_cancel_order_kb, get_payment_settings_kb
from fluent.runtime import FluentLocalization
from bot.database.db_requests import get_category_by_id, get_product_by_id, get_user_by_telegram_id
from aiogram.fsm.context import FSMContext
from bot.states.order_states import OrderStates
from bot.states.state_func import pop_state, push_state
from bot.utils.finance_math import calculate_quantity, calculate_max_bonus
from bot.filters.correct_number import CorrectNumberFilter
from fluent.runtime.types import FluentNumber, FluentNone
from loader import bot, configJson

router = Router()

@router.callback_query(lambda query: query.data.startswith("buy_product_"))
async def handle_buy_product(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    product_id = int(query.data.split("_")[2])
    product = await get_product_by_id(product_id)
    user = await get_user_by_telegram_id(query.from_user.id)
    
    minimal_price = configJson.get_config_value('minimal_price')
    min_quantity = calculate_quantity(product.price, user.discount_percentage, minimal_price)
    
    message = await query.message.edit_caption(caption=l10n.format_value('product-quantity', {'quantity': product.quantity, 'min': min_quantity}), reply_markup=get_cancel_order_kb(product_id))
    
    await state.set_state(OrderStates.WAITING_PRODUCT_QUANTITY)
    await state.update_data(min_quantity=min_quantity)
    await state.update_data(product=product)
    await state.update_data(user=user)
    await state.update_data(minimal_price=minimal_price)
    await state.update_data(message_id=message.message_id)
    
@router.message(OrderStates.WAITING_PRODUCT_QUANTITY, lambda message: message.text.isdigit() and int(message.text) > 0)
async def process_product_quantity(message: Message, state: FSMContext, l10n: FluentLocalization):
    data = await state.get_data()
    product = data.get('product')
    quantity_msg = int(message.text)
    message_id = data.get('message_id')
    min_quantity = data.get('min_quantity')
    await message.delete()
    
    if(quantity_msg < min_quantity or quantity_msg > product.quantity):
        return
    
    await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, reply_markup=get_payment_order_kb(), caption=l10n.format_value('product-info', {'name': product.label, 'quantity': quantity_msg, 'bonus': None}))
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
    
    if(user.bonus_points > 0):
        max_bonus = calculate_max_bonus(product.price * quantity_product, user.discount_percentage, minimal_price)
        
        await query.message.edit_caption(caption=f"Введите количество не больше {min(max_bonus, user.bonus_points):.0f}", reply_markup=get_payment_settings_kb())
        
        await state.update_data(max_bonus=min(max_bonus, user.bonus_points))
        await state.set_state(OrderStates.WAITING_BONUS_QUANTITY)
    else:
        await query.message.edit_caption(caption=f"У вас нет бонусов для использования", reply_markup=get_payment_settings_kb())
    
    
@router.message(OrderStates.WAITING_BONUS_QUANTITY, lambda message: message.text.isdigit() and int(message.text) >= 0)
async def proccess_bonus_quantity(message: Message, state: FSMContext, l10n: FluentLocalization):
    data = await state.get_data()
    quantity_msg = int(message.text)
    max_bonus = data.get('max_bonus')
    quantity_product = data.get('quantity_product')
    
    await message.delete()
    
    if(quantity_msg > max_bonus):
        return
    
    message_id = data.get('message_id')
    product = data.get('product')
    
    await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, reply_markup=get_payment_order_kb(), caption=l10n.format_value('product-info', {'name': product.label, 'quantity': quantity_product, 'bonus': quantity_msg}))
    await state.update_data(quantity_bonus=quantity_msg)
    await state.update_data(previous_state=OrderStates.WAITING_BONUS_QUANTITY)
    await state.set_state(state=None)

@router.callback_query(lambda query: query.data == 'payment_product')
async def handle_payment_product(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quantity_product = data.get('quantity_product')
    quantity_bonus = data.get('quantity_bonus')
    await query.message.edit_caption(caption=f"Продукта {quantity_product}\n Бонусов: {quantity_bonus or 0}", reply_markup=get_payment_settings_kb())
    await state.set_state(OrderStates.WAITING_PAYMENT)

@router.message(CorrectNumberFilter(OrderStates.WAITING_BONUS_QUANTITY, OrderStates.WAITING_PRODUCT_QUANTITY))
async def handle_non_digit_message(message: Message, state: FSMContext):
    await message.delete()

@router.callback_query(lambda query: query.data == "back_payment")
async def handle_back_payment(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    data = await state.get_data()
    current_state = await state.get_state() 
    
    if current_state is None:
        product = data.get('product')
        min_quantity = data.get('min_quantity')
        await query.message.edit_caption(caption=f"Введите количество не меньше {min_quantity}", reply_markup=get_cancel_order_kb(product.id))
        await state.update_data(quantity_product=None)
        await state.update_data(quantity_bonus=None)
        await state.set_state(OrderStates.WAITING_PRODUCT_QUANTITY)

    if(current_state in [ OrderStates.WAITING_BONUS_QUANTITY, OrderStates.WAITING_PAYMENT]):
        quantity_product = data.get('quantity_product')
        quantity_bonus = data.get('quantity_bonus')
        product = data.get('product')
        await query.message.edit_caption(reply_markup=get_payment_order_kb(), caption=l10n.format_value('product-info', {'name': product.label, 'quantity': quantity_product, 'bonus': quantity_bonus or None}))
        await state.set_state(state=None)
        


    

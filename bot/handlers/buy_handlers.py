import math
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.buy_keyboard import get_cancel_keyboard, get_payment_keyboard
from bot.utils.photo_answer_util import edit_message_media
from bot.states.order_states import OrderStates
from bot.utils.calculated_minimal_price import calculate_quantity_for_min_price, calculate_discount_for_price
from bot.database.db_requests import get_product_by_name, get_user_by_telegram_id
from loader import bot, configJson

router = Router()

async def get_order_data(state: FSMContext, user_id: int):
    data = await state.get_data()
    chat_id = data.get('chat_id')
    message_id = data.get('message_id')
    order_name = data.get('order_name')
    minimal_price = await configJson.get_config_value('minimal_price')
    user = await get_user_by_telegram_id(user_id)
    product = await get_product_by_name(order_name)
    return chat_id, message_id, minimal_price, user, product

async def send_error_message(chat_id, message_id, text):
    try:
        await bot.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=escape_characters(text),
            reply_markup=get_cancel_keyboard()
        )
    except Exception as e:
        logging.error(f"Failed to send error message: {e}")

@router.message(OrderStates.WAITING_QUANTITY)
async def handle_quantity_input(message: Message, state: FSMContext):
    chat_id, message_id, minimal_price, user, product = await get_order_data(state, message.from_user.id)
    try:
        await message.delete()
        quantity = int(message.text)
        min_quantity = calculate_quantity_for_min_price(minimal_price, product.price, user.discount_percentage)
        
        if quantity < min_quantity:
            await send_error_message(chat_id, message_id, f"Пожалуйста, введите количество не меньше {min_quantity}. Минимальная сумма заказа {minimal_price} руб.")
            return

        await state.update_data(quantity_product=quantity)
        await bot.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=escape_characters(f"Вы выбрали {product.label}, количество: {quantity}. Нажмите 'Оплатить' для оплаты."),
            reply_markup=get_payment_keyboard()
        )
        await state.set_state(OrderStates.WAITING_PAYMENT)
    except ValueError:
        await send_error_message(chat_id, message_id, "Пожалуйста, введите число.")
    except Exception as e:
        logging.error(f"Error handling quantity input: {e}")
        await send_error_message(chat_id, message_id, "Произошла ошибка. Попробуйте еще раз.")

@router.callback_query(lambda query: query.data == 'use_bonus_payment')
async def handle_bonus_use(query: CallbackQuery, state: FSMContext):
    chat_id, message_id, minimal_price, user, product = await get_order_data(state, query.from_user.id)
    try:
        if not user.bonus_points:
            await bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption="У вас нет бонусов для использования.",
                reply_markup=get_payment_keyboard()
            )
            return

        quantity_product = (await state.get_data()).get('quantity_product')
        discount_price = calculate_discount_for_price(product.price, user.discount_percentage) * quantity_product

        if discount_price <= minimal_price:
            await send_error_message(chat_id, message_id, f"Вы не можете использовать бонусы для данной покупки. Минимальная сумма заказа {minimal_price} руб.")
            return

        max_bonus_to_use = discount_price - minimal_price
        await state.set_state(OrderStates.WAITING_BONUS_USE)
        await edit_message_media(
            query,
            "RISE_LIMIT_ACCOUNT",
            get_cancel_keyboard(),
            caption=escape_characters(f"Введите количество бонусов. Вы можете использовать до {math.trunc(max_bonus_to_use)}.")
        )
    except Exception as e:
        logging.error(f"Error handling bonus use: {e}")
        await send_error_message(chat_id, message_id, "Произошла ошибка. Попробуйте еще раз.")

@router.message(OrderStates.WAITING_BONUS_USE)
async def process_bonus_quantity(message: Message, state: FSMContext):
    chat_id, message_id, minimal_price, user, product = await get_order_data(state, message.from_user.id)
    try:
        await message.delete()
        bonus_quantity = int(message.text)
        
        if bonus_quantity <= 0:
            await send_error_message(chat_id, message_id, "Пожалуйста, введите положительное число.")
            return
        
        quantity_product = (await state.get_data()).get('quantity_product')
        max_bonus_to_use = calculate_discount_for_price(product.price, user.discount_percentage) * quantity_product - minimal_price
        
        if bonus_quantity > max_bonus_to_use:
            await send_error_message(chat_id, message_id, f"Пожалуйста, введите число не больше {math.trunc(max_bonus_to_use)}.")
            return
        
        await state.update_data(bonus=bonus_quantity)
        await bot.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=escape_characters(f"Вы используете: {bonus_quantity} бонусов. Нажмите 'Оплатить' для оплаты."),
            reply_markup=get_payment_keyboard()
        )
        await state.set_state(OrderStates.WAITING_PAYMENT)
    except ValueError:
        await send_error_message(chat_id, message_id, "Пожалуйста, введите число.")
    except Exception as e:
        logging.error(f"Error processing bonus quantity: {e}")
        await send_error_message(chat_id, message_id, "Произошла ошибка. Попробуйте еще раз.")

@router.callback_query(OrderStates.WAITING_PAYMENT, lambda query: query.data == "make_payment")
async def handle_payment(query: CallbackQuery, state: FSMContext):
    try:
        print('оплата')
        # Здесь должна быть реализация логики оплаты
    except Exception as e:
        logging.error(f"Error processing payment: {e}")
        await send_error_message(query.message.chat.id, query.message.message_id, "Произошла ошибка при обработке платежа. Попробуйте еще раз.")

def escape_characters(text: str):
    return text.replace('.', '\\.').replace('-', '\\-').replace('_', '\\_')

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluent.runtime import FluentLocalization
from loguru import logger

from bot.database.db_requests import create_order
from bot.keyboards.shop_keyboards import get_buy_kb
from bot.states.order_states import OrderStates
from bot.utils.payment import initiate_payment

payment_router = Router(name=__name__)


@payment_router.callback_query(lambda query: query.data == 'payment_product')
async def handle_payment_product(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    data = await state.get_data()
    quantity_product = data.get('quantity_product')
    quantity_bonus = data.get('quantity_bonus') or 0.0
    product = data.get('product')
    user = data.get('user')

    try:
        # Создаем заказ
        order = await create_order(user['telegram_id'], product['id'], quantity_product)

        # Инициируем платеж, передавая ID заказа
        payment_url = await initiate_payment(user, quantity_product, product, quantity_bonus, order_id=order.id)
        logger.info(f"Payment URL: {payment_url}")
        logger.info(
            f"Order ID: {order.id}, Quantity: {quantity_product}, Bonus: {quantity_bonus}, Price: {product['price']}, Discount: {user['discount_percentage']}")

        await query.message.edit_caption(caption=l10n.format_value('payment-product'),
                                         reply_markup=get_buy_kb(payment_url))
        await state.set_state(OrderStates.WAITING_PAYMENT)

    except ValueError as e:
        logger.error(f"Error creating order: {e}")
        await query.answer("Ошибка при создании заказа. Пожалуйста, попробуйте снова.", show_alert=True)
    except Exception as e:
        logger.error(f"Unexpected error in handle_payment_product: {e}")
        await query.answer("Произошла неожиданная ошибка. Пожалуйста, попробуйте позже.", show_alert=True)

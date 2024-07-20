from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluent.runtime import FluentLocalization
from loguru import logger

from bot.keyboards.shop_keyboards import get_buy_kb
from bot.states.order_states import OrderStates
from bot.utils.payment import initiate_payment

payment_router = Router(name=__name__)


@payment_router.callback_query(lambda query: query.data == 'payment_product')
async def handle_payment_product(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    data = await state.get_data()
    quantity_product = data.get('quantity_product')
    quantity_bonus = data.get('quantity_bonus')
    product = data.get('product')
    user = data.get('user')

    payment_url = await initiate_payment(user, quantity_product, product, quantity_bonus)
    logger.info(payment_url)

    await query.message.edit_caption(caption=l10n.format_value('payment-product'),
                                     reply_markup=get_buy_kb(payment_url))
    await state.set_state(OrderStates.WAITING_PAYMENT)

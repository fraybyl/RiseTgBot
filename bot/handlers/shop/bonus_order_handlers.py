from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

from bot.core.loader import bot
from bot.keyboards.shop_keyboards import get_payment_settings_kb, get_payment_order_kb
from bot.states.order_states import OrderStates
from bot.utils.buy_math import calculate_max_bonus

bonus_router = Router(name=__name__)


@bonus_router.callback_query(lambda query: query.data == "bonus_use_product")
async def handle_bonus_use(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quantity_product = data.get('quantity_product')
    product = data.get('product')
    user = data.get('user')
    minimal_price = data.get('minimal_price')

    await state.set_state(OrderStates.WAITING_BONUS_QUANTITY)
    if user['bonus_points'] > 0:
        max_bonus = calculate_max_bonus(product['price'] * quantity_product, user['discount_percentage'], minimal_price)

        await query.message.edit_caption(
            caption=f"Введите количество не больше {min(max_bonus, user['bonus_points']):.0f}",
            reply_markup=get_payment_settings_kb())

        await state.update_data(max_bonus=min(max_bonus, user['bonus_points']))
    else:
        await query.message.edit_caption(caption=f"У вас нет бонусов для использования",
                                         reply_markup=get_payment_settings_kb())
        await state.update_data(max_bonus=-1)


@bonus_router.message(
    OrderStates.WAITING_BONUS_QUANTITY,
    lambda message: message.text.isdigit() and int(message.text) >= 0)
async def process_bonus_quantity(message: Message, state: FSMContext, l10n: FluentLocalization):
    data = await state.get_data()
    quantity_msg = int(message.text)
    max_bonus = data.get('max_bonus')
    quantity_product = data.get('quantity_product')

    await message.delete()

    if quantity_msg > max_bonus:
        return

    message_id = data.get('message_id')
    product = data.get('product')

    await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, reply_markup=get_payment_order_kb(),
                                   caption=l10n.format_value('product-info',
                                                             {'name': product['label'], 'quantity': quantity_product,
                                                              'bonus': quantity_msg}))
    await state.update_data(quantity_bonus=quantity_msg)
    await state.update_data(previous_state=OrderStates.WAITING_BONUS_QUANTITY.state)
    await state.set_state(state=None)

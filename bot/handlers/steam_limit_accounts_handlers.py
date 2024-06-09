from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, LabeledPrice
from aiogram.methods import CreateInvoiceLink
from aiogram.fsm.context import FSMContext
from bot.keyboards.steam_limit_accounts_keyboard import get_limit_accounts_kb, get_currency_limit_acc_kb, get_payment_limit_acc_kb, get_cancel_limit_acc_kb
from bot.keyboards.shop_keyboard import get_shop_kb
from bot.utils.photo_answer_util import edit_message_media
from bot.utils.calculated_minimal_price import calculate_quantity_for_min_price
from bot.states.order_states import OrderStates
from bot.config.settings import settings
from bot.database.db_requests import get_product_by_name, get_user_by_telegram_id
import math
from loader import bot, configJson

router = Router()

@router.callback_query(lambda query: query.data == "limit_accounts")
async def handle_steam_limic_acc_callback(query: CallbackQuery):
    await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_limit_accounts_kb())

@router.callback_query(lambda query: query.data == "non_sda_accounts")
async def handle_limic_acc_non_sda_callback(query: CallbackQuery, state: FSMContext):
    await state.update_data(order_name=query.data)
    await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_currency_limit_acc_kb())

@router.callback_query(lambda query: query.data == "sda_accounts")
async def handle_limic_acc_sda_callback(query: CallbackQuery, state: FSMContext):
    await state.update_data(order_name=query.data)
    await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_currency_limit_acc_kb())
    
@router.callback_query(lambda query: query.data == "sda_2lvl_accounts")
async def handle_limic_acc_2lvl_callback(query: CallbackQuery, state: FSMContext):
    await state.update_data(order_name=query.data)
    await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_currency_limit_acc_kb())

@router.callback_query(lambda query: query.data == "buy_limit_acc")
async def handle_buy_limic_acc_callback(query: CallbackQuery, state: FSMContext):
    chat_id, message_id = await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_cancel_limit_acc_kb(), caption="Введите желамое количество\\. В наличие: \\.")
    await state.set_state(OrderStates.WAITING_QUANTITY)
    await state.update_data(chat_id=chat_id, message_id=message_id)
    

# @router.message(OrderStates.WAITING_QUANTITY_LIMIT_ACC)
# async def process_quantity_limit_acc(message: Message, state: FSMContext):
#     data = await state.get_data()
#     chatid = data.get('chat_id')
#     messageid = data.get('message_id')
#     minimal_price = await configJson.get_config_value('minimal_price')
#     limit_acc_type = data.get('order_name')
#     user = await get_user_by_telegram_id(message.from_user.id)
    
    
#     try:
#         await message.delete()
#         quantity = int(message.text)
#         try:
#             product = await get_product_by_name(limit_acc_type)
#         except: 
#             await state.clear()
#             await bot.edit_message_media(chat_id=chatid, message_id=messageid, media="RISE_LIMIT_ACCOUNT", reply_markup=get_limit_accounts_kb())
        
        
#         if (quantity < calculate_quantity_for_min_price(minimal_price, product.price, user.discount_percentage)):
#             await bot.edit_message_caption(chat_id=chatid, 
#                                            message_id=messageid, 
#                                            caption=f"Пожалуйста, введите число не меньше \\{calculate_quantity_for_min_price(minimal_price, product.price, user.discount_percentage)}.".replace('.', '\\.'), 
#                                            reply_markup=get_cancel_limit_acc_kb())
#             return
#         limit_acc = data.get('limit_acc_type')
#         await state.update_data(quantity_product=quantity)
#         await bot.edit_message_caption(chat_id=chatid, 
#                                        message_id=messageid, 
#                                        caption=f"Вы выбрали {limit_acc}, количество: {quantity}\\. Нажмите 'Оплатить' для оплаты\\.".replace('_', r'\_'), 
#                                        reply_markup=get_payment_limit_acc_kb())
#         await state.set_state(OrderStates.WAITING_PAYMENT)
#     except ValueError:
#         await bot.edit_message_caption(chat_id=chatid, message_id=messageid, caption="Пожалуйста, введите число\\.", reply_markup=get_cancel_limit_acc_kb())

# @router.callback_query(lambda query: query.data == 'use_bonuse_limit_acc')
# async def handle_bonus_limit_acc_callback(query: CallbackQuery, state: FSMContext):
#     user = await get_user_by_telegram_id(query.from_user.id)
    
#     if(not user.bonus_points):
#         await query.message.edit_caption(caption="У вас нет бонусов для использования\\.", reply_markup=get_payment_limit_acc_kb())
#         return
#     #не больше
#     await state.set_state(OrderStates.WAITING_BONUS_USE)
#     await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_cancel_limit_acc_kb(), caption="Введите количество бонусов\\. В наличие: \\.")
    
# @router.message(OrderStates.WAITING_BONUS_USE)
# async def process_bonus_limit_acc(message: Message, state: FSMContext):
#     data = await state.get_data()
#     chatid = data.get('chat_id')
#     messageid = data.get('message_id')
    
    
#     try:
#         await message.delete()
#         quantity = int(message.text)

            
#         if quantity <= 0:
#             await bot.edit_message_caption(chat_id=chatid, 
#                                            message_id=messageid, 
#                                            caption="Пожалуйста, введите положительное число\\.", 
#                                            reply_markup=get_cancel_limit_acc_kb())
#             return
#         await state.update_data(bonus=quantity)
#         await bot.edit_message_caption(chat_id=chatid, 
#                                 message_id=messageid, 
#                                 caption=f"Вы используете: {quantity} бонусов\\. Нажмите 'Оплатить' для оплаты\\.".replace('_', r'\_'), 
#                                 reply_markup=get_payment_limit_acc_kb())
#         await state.set_state(OrderStates.WAITING_PAYMENT)
#     except ValueError:
#         await bot.edit_message_caption(chat_id=chatid, message_id=messageid, caption="Пожалуйста, введите число\\.", reply_markup=get_cancel_limit_acc_kb())

# @router.callback_query(OrderStates.WAITING_PAYMENT, lambda query: query.data == "pay_limit_acc")
# async def handle_pay_limit_acc(query: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
    
#     limit_acc_type = data.get('limit_acc_type')
#     quantity_product = int(data.get('quantity_product'))
#     bonus_to_use = data.get('bonus')
    
#     user = await get_user_by_telegram_id(query.from_user.id)
    
    
#     if(bonus_to_use):
#         pass
    
#     try:
#         product = await get_product_by_name(limit_acc_type)
#     except: 
#         await state.clear()
#         await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_limit_accounts_kb())
        
#     product_total_price = product.price * quantity_product * 100
    
#     await query.message.answer_invoice(
#         title=product.name,
#         description=product.description,
#         payload='test',
#         currency=product.currency_type,
#         prices=[
#             LabeledPrice(
#                 label=product.name,
#                 amount=product_total_price,
#             ),
#             LabeledPrice(
#                 label='Скидка',
#                 amount=-(product_total_price / 100 * user.discount_percentage),
#             ),
#             LabeledPrice(
#                 label='Бонус',
#                 amount=-bonus_to_use * 100 if bonus_to_use is not None else 0.0
#             )
#         ],
#         provider_token=settings.PAYMENTS_TOKEN,
#         photo_url=product.photo_url,
#     )

@router.callback_query(lambda query: query.data in ["back_limit_acc_list", "cancel_limit_acc", "back_limit_acc"])
async def handle_back_limit_acc_callback(query: CallbackQuery, state: FSMContext):
    await state.clear()
    if query.data == "back_limit_acc":
        await edit_message_media(query, "RISE_SHOP", get_shop_kb())
    else:
        await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_limit_accounts_kb())
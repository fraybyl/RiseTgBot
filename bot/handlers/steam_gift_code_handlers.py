from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.steam_gift_code_keyboard import get_steam_gift_code_kb, get_currency_gift_code_kb, get_payment_gift_code_kb
from bot.keyboards.shop_keyboard import get_shop_kb
from bot.utils.photo_answer_util import edit_message_media
from bot.states.order_states import OrderStates
from loader import bot

router = Router()

@router.callback_query(lambda query: query.data == "steam_gift_code")
async def handle_steam_gift_code_callback(query: CallbackQuery):
    await edit_message_media(query, "RISE_GIFT_CODE", get_steam_gift_code_kb())
    
@router.callback_query(lambda query: query.data == "gift_5")
async def handle_gift_code_five_callback(query: CallbackQuery, state: FSMContext):
    await state.update_data(gift_currency=query.data)
    await edit_message_media(query, "RISE_GIFT_CODE", get_currency_gift_code_kb())

@router.callback_query(lambda query: query.data == "gift_10")
async def handle_gift_code_ten_callback(query: CallbackQuery, state: FSMContext):
    await state.update_data(gift_currency=query.data)
    await edit_message_media(query, "RISE_GIFT_CODE", get_currency_gift_code_kb())
    
@router.callback_query(lambda query: query.data == "gift_15")
async def handle_gift_code_fifteen_callback(query: CallbackQuery, state: FSMContext):
    await state.update_data(gift_currency=query.data)
    await edit_message_media(query, "RISE_GIFT_CODE", get_currency_gift_code_kb())
    
@router.callback_query(lambda query: query.data == "gift_20")
async def handle_gift_code_twenty_callback(query: CallbackQuery, state: FSMContext):
    await state.update_data(gift_currency=query.data)
    await edit_message_media(query, "RISE_GIFT_CODE", get_currency_gift_code_kb())
    
@router.callback_query(lambda query: query.data == "buy_gift")
async def handle_buy_gift_code_callback(query: CallbackQuery, state: FSMContext):
    chat_id, message_id = await edit_message_media(query, "RISE_GIFT_CODE", get_payment_gift_code_kb(), caption="Введите желамое количество\\. В наличие: \\.")
    await state.set_state(OrderStates.WAITING_QUANTITY_GIFT)
    await state.update_data(chat_id=chat_id, message_id=message_id)
    

@router.message(OrderStates.WAITING_QUANTITY_GIFT)
async def process_quantity_gift_code(message: Message, state: FSMContext):
    data = await state.get_data()
    chatid = data.get('chat_id')
    messageid = data.get('message_id')
    
    try:
        await message.delete()
        quantity = int(message.text)
        if quantity <= 0:
            await bot.edit_message_caption(chat_id=chatid, 
                                           message_id=messageid, 
                                           caption="Пожалуйста, введите положительное число\\.", 
                                           reply_markup=get_payment_gift_code_kb())
            return
        gift_currency = data.get('gift_currency')
        await state.update_data(quantity=quantity)
        await bot.edit_message_caption(chat_id=chatid, 
                                       message_id=messageid, 
                                       caption=f"Вы выбрали {gift_currency}, количество: {quantity}".replace('_', r'\_'), 
                                       reply_markup=get_payment_gift_code_kb())
        
        await state.set_state(OrderStates.WAITING_PAYMENT)
        
        #либо здесь логика оплаты либо в отдельной @router.callbackquery
        #Здесь у тебя есть quantity - это заказанное количество и gift_currency это что за аккаунт на покупку взял человек
        # отдели логику ордера покупки на отдельный файл. полностью. независимый от кнопок или еще чего. Чисто бизнес логика 
        # и подключи его здесь как я полагаю 
        # в любом случае сильно насирать в этом хендлере не надо. После обработки платежа сделай await state.clear()
        # и по идеи тебе понадобятся PAYMENT_PROCCESS или что то типо такого стейта но я не уверен. возможно тебе хватит того что есть
        # то естЬ WAITING_PAYMENT. 
        
    except ValueError:
        await bot.edit_message_caption(chat_id=chatid, message_id=messageid, caption="Пожалуйста, введите число\\.", reply_markup=get_payment_gift_code_kb())



@router.callback_query(lambda query: query.data in ["back_gift_code", "back_gift_list", "cancel_gift_code"])
async def handle_back_limit_acc_callback(query: CallbackQuery, state: FSMContext):
    await state.clear()
    if query.data == "back_gift_code":
        await edit_message_media(query, "RISE_SHOP", get_shop_kb())
    else:
        await edit_message_media(query, "RISE_GIFT_CODE", get_steam_gift_code_kb())
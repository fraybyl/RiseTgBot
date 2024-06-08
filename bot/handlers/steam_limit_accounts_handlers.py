from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.steam_limit_accounts_keyboard import get_limit_accounts_kb, get_currency_limit_acc_kb, get_payment_limit_acc_kb
from bot.keyboards.shop_keyboard import get_shop_kb
from bot.utils.photo_answer_util import edit_message_media
from bot.states.order_states import OrderStates
from loader import bot

router = Router()

@router.callback_query(lambda query: query.data == "limit_accounts")
async def handle_steam_limic_acc_callback(query: CallbackQuery):
    await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_limit_accounts_kb())

@router.callback_query(lambda query: query.data == "non_sda_accounts")
async def handle_limic_acc_non_sda_callback(query: CallbackQuery, state: FSMContext):
    await state.update_data(limit_acc_currency=query.data)
    await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_currency_limit_acc_kb())

@router.callback_query(lambda query: query.data == "sda_accounts")
async def handle_limic_acc_sda_callback(query: CallbackQuery, state: FSMContext):
    await state.update_data(limit_acc_currency=query.data)
    await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_currency_limit_acc_kb())
    
@router.callback_query(lambda query: query.data == "sda_2lvl_accounts")
async def handle_limic_acc_2lvl_callback(query: CallbackQuery, state: FSMContext):
    await state.update_data(limit_acc_currency=query.data)
    await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_currency_limit_acc_kb())

@router.callback_query(lambda query: query.data == "buy_limit_acc")
async def handle_buy_limic_acc_callback(query: CallbackQuery, state: FSMContext):
    chat_id, message_id = await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_payment_limit_acc_kb(), caption="Введите желамое количество\\. В наличие: \\.")
    await state.set_state(OrderStates.WAITING_QUANTITY_LIMIT_ACC)
    await state.update_data(chat_id=chat_id, message_id=message_id)
    

@router.message(OrderStates.WAITING_QUANTITY_LIMIT_ACC)
async def process_quantity_limit_acc(message: Message, state: FSMContext):
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
                                           reply_markup=get_payment_limit_acc_kb())
            return
        limit_acc = data.get('limit_acc_currency')
        await state.update_data(quantity=quantity)
        await bot.edit_message_caption(chat_id=chatid, 
                                       message_id=messageid, 
                                       caption=f"Вы выбрали {limit_acc}, количество: {quantity}".replace('_', r'\_'), 
                                       reply_markup=get_payment_limit_acc_kb())
        
        await state.set_state(OrderStates.WAITING_PAYMENT)
    
        #либо здесь логика оплаты либо в отдельной @router.callbackquery
        #Здесь у тебя есть quantity - это заказанное количество и limit_acc это что за аккаунт на покупку взял человек
        # отдели логику ордера покупки на отдельный файл. полностью. независимый от кнопок или еще чего. Чисто бизнес логика 
        # и подключи его здесь как я полагаю 
        # в любом случае сильно насирать в этом хендлере не надо. После обработки платежа сделай await state.clear()
        # и по идеи тебе понадобятся PAYMENT_PROCCESS или что то типо такого стейта но я не уверен. возможно тебе хватит того что есть
        # то естЬ WAITING_PAYMENT. 
        
    except ValueError:
        await bot.edit_message_caption(chat_id=chatid, message_id=messageid, caption="Пожалуйста, введите число\\.", reply_markup=get_payment_limit_acc_kb())


@router.callback_query(lambda query: query.data in ["back_limit_acc_list", "cancel_limit_acc", "back_limit_acc"])
async def handle_back_limit_acc_callback(query: CallbackQuery, state: FSMContext):
    await state.clear()
    if query.data == "back_limit_acc":
        await edit_message_media(query, "RISE_SHOP", get_shop_kb())
    else:
        await edit_message_media(query, "RISE_LIMIT_ACCOUNT", get_limit_accounts_kb())
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.strategy_keyboard import get_strategy_kb, get_calculated_cancel_kb, get_calculated_kb
from bot.keyboards.farmers_keyboard import get_farmers_kb
from bot.utils.photo_answer_util import edit_message_media
from bot.states.strategy_states import StrategyStates
from bot.utils.investments_calculator import simulate_investment_strategy
from bot.filters.MultipleStateInFilter import MultipleStateInFilter
from loader import logging, bot

router = Router()

@router.callback_query(lambda query: query.data == "strategy")
async def handle_shop_callback(query: CallbackQuery):
    await edit_message_media(query, "RISE_FOR_FARMERS", get_strategy_kb())
    

@router.callback_query(lambda query: query.data in ["conservative_strategy", "moderate_strategy", "aggressive_strategy"])
async def handle_strategy_choose_callback(query: CallbackQuery, state: FSMContext):
    strategies = {
        "aggressive_strategy": {"text": "консервативную стратегию", "float_value": 0.4},
        "moderate_strategy": {"text": "умеренную стратегию", "float_value": 0.6},
        "conservative_strategy": {"text": "агрессивную стратегию", "float_value": 0.8}
    }
    
    strategy_info = strategies.get(query.data, {})
    
    if(strategy_info):
        chosen_strategy_text = strategy_info["text"]
        chosen_strategy_float = strategy_info["float_value"]
        
        chatid, messageid = await edit_message_media(query, "RISE_FOR_FARMERS", get_calculated_cancel_kb(), f"Вы выбрали {chosen_strategy_text}\\.\nВведите количество аккаунтов")
        await state.update_data(chat_id=chatid, message_id=messageid, 
                                reinvest_ration=chosen_strategy_float, chosen_strategy_text=chosen_strategy_text)
        await state.set_state(StrategyStates.INITIAL_ACCOUNTS)
    
@router.message(StrategyStates.INITIAL_ACCOUNTS, lambda message: message.text.isdigit())
async def handle_initial_accounts(message: Message, state: FSMContext):
    chatid, messageid = await get_chat_and_message_ids(state)
    await state.update_data(initial_accounts=message.text)
    await message.delete()
    await bot.edit_message_caption(chat_id=chatid, message_id=messageid, caption="Введите количество недель\\.", reply_markup=get_calculated_cancel_kb())
    await state.set_state(StrategyStates.TOTAL_WEEKS)

@router.message(StrategyStates.TOTAL_WEEKS, lambda message: message.text.isdigit())
async def handle_total_weeks(message: Message, state: FSMContext):
    chatid, messageid = await get_chat_and_message_ids(state)
    await state.update_data(total_weeks=message.text)
    await message.delete()
    await bot.edit_message_caption(chat_id=chatid, message_id=messageid, caption="Введите прибыль за неделю с одного аккаунта\\.", reply_markup=get_calculated_cancel_kb())
    await state.set_state(StrategyStates.WEEKLY_PROFIT)
    
@router.message(StrategyStates.WEEKLY_PROFIT, lambda message: message.text.isdigit())
async def handle_total_weeks(message: Message, state: FSMContext):
    chatid, messageid = await get_chat_and_message_ids(state)
    await state.update_data(weekly_profit=message.text)
    await message.delete()
    await bot.edit_message_caption(chat_id=chatid, message_id=messageid, caption="Введите стоимость одного аккаунта\\.", reply_markup=get_calculated_cancel_kb())
    await state.set_state(StrategyStates.ACCOUNT_COST)
    
@router.message(StrategyStates.ACCOUNT_COST, lambda message: message.text.isdigit())
async def handle_account_cost(message: Message, state: FSMContext):
    try:
        await message.delete()
        data = await state.get_data()
        chatid = data.get('chat_id')
        message_id = data.get('message_id')
        
        account_cost = message.text
        initial_accounts = data.get('initial_accounts')
        weekly_profit_per_account = data.get('weekly_profit')
        total_weeks = data.get('total_weeks')
        ratio = data.get('reinvest_ration')
        chosen_strategy_text = data.get('chosen_strategy_text')    

        calculatingDict = simulate_investment_strategy(initial_accounts, account_cost, weekly_profit_per_account, total_weeks, ratio)
        caption_text = (
                f"Вы выбрали {chosen_strategy_text}.\n"
                f"Количество аккаунтов: {calculatingDict[0][1]}\n"
                f"Накопленная прибыль для реинвестирования: {calculatingDict[0][2]:.2f} рублей\n"
                f"Сохраненная прибыль: {calculatingDict[0][3]:.2f} рублей\n"
        ).replace('.', '\\.')
        
        await bot.edit_message_caption(chat_id=chatid, message_id=message_id, caption=caption_text, reply_markup=get_calculated_kb())
        await state.clear()
    except Exception as e:
        logging.error(f"Ошибка при обработке стоимости аккаунта: {e}")
        await bot.edit_message_caption(chat_id=chatid, message_id=message_id, caption="Произошла ошибка\\. Пожалуйста, попробуйте снова\\.", reply_markup=get_calculated_kb())

@router.message(MultipleStateInFilter(
    StrategyStates.INITIAL_ACCOUNTS,
    StrategyStates.TOTAL_WEEKS,
    StrategyStates.WEEKLY_PROFIT,
    StrategyStates.ACCOUNT_COST
))
async def handle_incorrectly_strategy(message: Message, state: FSMContext):
    chatid, messageid = await get_chat_and_message_ids(state)
    await message.delete()
    await bot.edit_message_caption(chat_id=chatid, message_id=messageid, caption="Пожалуйста, введите число\\!", reply_markup=get_calculated_cancel_kb())

async def get_chat_and_message_ids(state: FSMContext):
    data = await state.get_data()
    return data.get('chat_id'), data.get('message_id')
    
@router.callback_query(lambda query: query.data == "back_strategy")
async def handle_back_shop_callback(query: CallbackQuery):
    await edit_message_media(query, "RISE_FOR_FARMERS", get_farmers_kb())
    
@router.callback_query(lambda query: query.data == "cancel_strategy")
async def handle_cancel_callback(query: CallbackQuery, state: FSMContext):
    await edit_message_media(query, "RISE_FOR_FARMERS", get_strategy_kb())
    await state.clear()
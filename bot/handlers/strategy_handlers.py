from aiogram import Router
from aiogram.types import CallbackQuery, Message
from bot.keyboards.user_kb import get_strategy_kb, get_cancel_strategy_kb
from fluent.runtime import FluentLocalization
from aiogram.fsm.context import FSMContext
from bot.utils import utils
from bot.utils.investments_calculator import simulate_investment_strategy
from bot.states.state_func import push_state, pop_state
from bot.handlers.error_handlers import handle_error_back
from bot.states.strategy_states import StrategyStates
from bot.filters.correct_number import CorrectNumberFilter
from loader import bot, configJson

router = Router()

@router.callback_query(lambda query: query.data == "strategy")
async def handle_shop(query: CallbackQuery):
    await utils.edit_message_media(query, 'RISE_STRATEGY', get_strategy_kb())
    
@router.callback_query(lambda query: query.data in ['aggressive_strategy', 'moderate_strategy', 'conservative_strategy'])
async def handle_strategy_choice(query: CallbackQuery, state: FSMContext):
    if query.data == 'aggressive_strategy':
        float_strategy = 0.8
        text_strategy = 'Агрессивную стратегию'
        media_type = 'AGGRESIVE'
    elif query.data == 'moderate_strategy':
        float_strategy = 0.6
        text_strategy = 'Умеренную стратегию'
        media_type = 'MODERATE'
    elif query.data == 'conservative_strategy':
        float_strategy = 0.4
        text_strategy = 'Консервативную стратегию'
        media_type = 'CONSERVATIVE'
        
    message_id = await utils.edit_message_media(callback_query=query, media=media_type, reply_markup=get_cancel_strategy_kb(), caption=f'Вы выбрали: {text_strategy}.\nПожалуйста, введите количество аккаунтов')
    
    await state.update_data(current_strategy=query.data, media_type=media_type, text_strategy=text_strategy, float_strategy=float_strategy, message_id=message_id)
    await push_state(state, StrategyStates.INITIAL_ACCOUNTS)

@router.message(StrategyStates.INITIAL_ACCOUNTS, lambda message: message.text.isdigit() and int(message.text) > 0)
async def process_initial_accounts(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        message_id = data.get('message_id')
        await state.update_data(initial_accounts=message.text)
        
        await message.delete()
        await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, reply_markup=get_cancel_strategy_kb(),
                                       caption=f"Вы ввели {message.text} аккаунтов.\nВведите количество недель.")
        
        await push_state(state, StrategyStates.TOTAL_WEEKS)
    except Exception as e:
        print(e)

@router.message(StrategyStates.TOTAL_WEEKS, lambda message: message.text.isdigit() and int(message.text) > 0)
async def process_total_weeks(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        message_id = data.get('message_id')
        initial_accounts = data.get('initial_accounts')
        current_strategy = data.get('current_strategy')
        total_weeks = message.text
        account_cost = await configJson.get_config_value('account_price')
        
        await message.delete()
        accounts_after, profit = simulate_investment_strategy(initial_accounts, account_cost, 50.23, total_weeks, 0.8)
        caption_text = (f"Вы выбрали {current_strategy}.\n"
                        f"Вы инвестируете {total_weeks} недель\n"
                        f"Средняя цена дропа: {50}\n"
                        f"Цена аккаунта: {account_cost}\n"
                        f"Количество аккаунтов: {accounts_after}\n"
                        f"Сохраненная прибыль: {profit:.1f} рублей")
        
        await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, reply_markup=get_cancel_strategy_kb(),
                                       caption=caption_text)
        
        await push_state(state, StrategyStates.CALCULATE)
    except Exception as e:
        print(e)

@router.message(CorrectNumberFilter(StrategyStates.INITIAL_ACCOUNTS, StrategyStates.TOTAL_WEEKS))
async def handle_non_digit_message(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('message_id')
    await message.delete()
    try:
        print('бля ну это заглушка канеш но я хуй знает че с этим ещё сделать')
        await bot.edit_message_caption(chat_id=message.from_user.id, message_id=message_id, caption='Пожалуйста, введите корректное число...', reply_markup=get_cancel_strategy_kb())
    except:
        pass

@router.callback_query(lambda query: query.data == 'back_strategy')
async def handle_back_strategy(query: CallbackQuery, state: FSMContext):
    previous_state = await pop_state(state)
    current_state = await state.get_state()
    if current_state is None:
        await handle_error_back(query, state)
        return
    
    data = await state.get_data()
    media_type = data.get('media_type')
    text_strategy = data.get('text_strategy')
    initial_accounts = data.get('initial_accounts')
    
    await state.set_state(previous_state)
    
    if previous_state is None:
        await state.clear()
        await utils.edit_message_media(query, 'RISE_STRATEGY', get_strategy_kb()) 
    elif previous_state == StrategyStates.INITIAL_ACCOUNTS:
        await utils.edit_message_media(query, media_type, get_cancel_strategy_kb(), f'Вы выбрали: {text_strategy}.\nПожалуйста, введите количество аккаунтов')
    elif previous_state == StrategyStates.TOTAL_WEEKS:
        await utils.edit_message_media(query, media_type, get_cancel_strategy_kb(), f'Вы ввели {initial_accounts} аккаунтов.\nВведите количество недель.')
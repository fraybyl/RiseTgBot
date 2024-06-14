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
from bot.utils.avg_price_drop import get_avg_drop
from loader import bot, configJson

router = Router()

@router.callback_query(lambda query: query.data == "strategy")
async def handle_shop(query: CallbackQuery):
    await utils.edit_message_media(query, 'RISE_STRATEGY', get_strategy_kb())
    
@router.callback_query(lambda query: query.data in ['aggressive_strategy', 'moderate_strategy', 'conservative_strategy'])
async def handle_strategy_choice(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    if query.data == 'aggressive_strategy':
        float_strategy = 0.8
        text_strategy = 'агрессивную стратегию'
        media_type = 'AGGRESIVE'
    elif query.data == 'moderate_strategy':
        float_strategy = 0.6
        text_strategy = 'умеренную стратегию'
        media_type = 'MODERATE'
    elif query.data == 'conservative_strategy':
        float_strategy = 0.4
        text_strategy = 'консервативную стратегию'
        media_type = 'CONSERVATIVE'
        
    message_id = await utils.edit_message_media(callback_query=query, media=media_type, reply_markup=get_cancel_strategy_kb(), caption=l10n.format_value('strategy-choose', {"name": text_strategy}))
    
    await state.update_data(current_strategy=query.data, media_type=media_type, text_strategy=text_strategy, float_strategy=float_strategy, message_id=message_id)
    await push_state(state, StrategyStates.INITIAL_ACCOUNTS)

@router.message(StrategyStates.INITIAL_ACCOUNTS, lambda message: message.text.isdigit() and int(message.text) > 0)
async def process_initial_accounts(message: Message, state: FSMContext, l10n: FluentLocalization):
    try:
        data = await state.get_data()
        message_id = data.get('message_id')
        await state.update_data(initial_accounts=message.text)
        
        await message.delete()
        await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, reply_markup=get_cancel_strategy_kb(),
                                       caption=l10n.format_value('strategy-accounts', {'accounts': message.text}))
        
        await push_state(state, StrategyStates.TOTAL_WEEKS)
    except Exception as e:
        print(e)

@router.message(StrategyStates.TOTAL_WEEKS, lambda message: message.text.isdigit() and int(message.text) > 0)
async def process_total_weeks(message: Message, state: FSMContext, l10n: FluentLocalization):
    try:
        data = await state.get_data()
        message_id = data.get('message_id')
        initial_accounts = data.get('initial_accounts')
        text_strategy = data.get('text_strategy')
        float_strategy = data.get('float_strategy')
        total_weeks = message.text
        account_cost = await configJson.get_config_value('account_price')
        avg_price = await get_avg_drop()
        await message.delete()
        
        accounts_after, profit = simulate_investment_strategy(initial_accounts, account_cost, avg_price, total_weeks, float_strategy)
        caption_text = l10n.format_value('strategy-result',
                                         {'name': text_strategy, 
                                          'weeks': total_weeks, 
                                          'price': avg_price, 
                                          'account_price': account_cost,
                                          'accounts': accounts_after,
                                          'profit': round(profit, 1)})
        
        await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, reply_markup=get_cancel_strategy_kb(),
                                       caption=caption_text)
        
        await push_state(state, StrategyStates.CALCULATE)
    except Exception as e:
        print(e)

@router.message(CorrectNumberFilter(StrategyStates.INITIAL_ACCOUNTS, StrategyStates.TOTAL_WEEKS))
async def handle_non_digit_message(message: Message, state: FSMContext):
    await message.delete()

@router.callback_query(lambda query: query.data == 'back_strategy')
async def handle_back_strategy(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    previous_state = await pop_state(state)
    
    data = await state.get_data()
    text_strategy = data.get('text_strategy')
    initial_accounts = data.get('initial_accounts')
    
    await state.set_state(previous_state)
    
    if previous_state is None:
        await state.clear()
        await utils.edit_message_media(query, 'RISE_STRATEGY', get_strategy_kb()) 
    elif previous_state == StrategyStates.INITIAL_ACCOUNTS:
        await query.message.edit_caption(reply_markup=get_cancel_strategy_kb(), caption=l10n.format_value('strategy-choose', {"name": text_strategy}))
    elif previous_state == StrategyStates.TOTAL_WEEKS:
        await query.message.edit_caption(reply_markup=get_cancel_strategy_kb(), caption=l10n.format_value('strategy-accounts', {'accounts': initial_accounts}))
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

from bot.filters.correct_number import CorrectNumberFilter
from bot.keyboards.farmers_keyboards import get_strategy_kb, get_cancel_strategy_kb
from bot.states.state_helper import push_state, pop_state
from bot.states.strategy_states import StrategyStates
from bot.utils.edit_media import edit_message_media
from .initial_accounts_handlers import initial_accounts_router
from .total_weeks_handlers import total_weeks_router

router = Router(name=__name__)
router.include_router(initial_accounts_router)
router.include_router(total_weeks_router)


strategy_mapping = {
    'aggressive_strategy': {
        'float_strategy': 0.8,
        'text_strategy': 'агрессивную стратегию',
        'media_type': 'AGGRESSIVE'
    },
    'moderate_strategy': {
        'float_strategy': 0.6,
        'text_strategy': 'умеренную стратегию',
        'media_type': 'MODERATE'
    },
    'conservative_strategy': {
        'float_strategy': 0.4,
        'text_strategy': 'консервативную стратегию',
        'media_type': 'CONSERVATIVE'
    }
}


def strategy_filter(query):
    return query.data in ['aggressive_strategy', 'moderate_strategy', 'conservative_strategy']


@router.callback_query(lambda query: query.data == "strategy")
async def handle_shop(query: CallbackQuery):
    await edit_message_media(query, 'RISE_STRATEGY', get_strategy_kb())


@router.callback_query(
    strategy_filter)
async def handle_strategy_choice(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    strategy = strategy_mapping[query.data]

    message_id = await edit_message_media(callback_query=query, media=strategy['media_type'],
                                          reply_markup=get_cancel_strategy_kb(),
                                          caption=l10n.format_value('strategy-choose',
                                                                    {"name": strategy['text_strategy']}))

    await state.update_data(current_strategy=query.data, media_type=strategy['media_type'],
                            text_strategy=strategy['text_strategy'],
                            float_strategy=strategy['float_strategy'],
                            message_id=message_id)

    await push_state(state, StrategyStates.INITIAL_ACCOUNTS.state)


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
        await edit_message_media(query, 'RISE_STRATEGY', get_strategy_kb())
    elif previous_state == StrategyStates.INITIAL_ACCOUNTS:
        await query.message.edit_caption(reply_markup=get_cancel_strategy_kb(),
                                         caption=l10n.format_value('strategy-choose', {"name": text_strategy}))
    elif previous_state == StrategyStates.TOTAL_WEEKS:
        await query.message.edit_caption(reply_markup=get_cancel_strategy_kb(),
                                         caption=l10n.format_value('strategy-accounts', {'accounts': initial_accounts}))

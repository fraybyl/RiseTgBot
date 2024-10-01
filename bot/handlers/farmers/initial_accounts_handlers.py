from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from fluent.runtime import FluentLocalization
from loguru import logger

from bot.core.loader import bot
from bot.keyboards.farmers_keyboards import get_cancel_strategy_kb
from bot.states.state_helper import push_state
from bot.states.strategy_states import StrategyStates

initial_accounts_router = Router(name=__name__)


@initial_accounts_router.message(StrategyStates.INITIAL_ACCOUNTS,
                                 lambda message: message.text.isdigit() and int(message.text) > 0)
async def process_initial_accounts(message: Message, state: FSMContext, l10n: FluentLocalization):
    try:
        data = await state.get_data()
        message_id = data.get('message_id')
        await state.update_data(initial_accounts=message.text)

        await message.delete()
        await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                       reply_markup=get_cancel_strategy_kb(),
                                       caption=l10n.format_value('strategy-accounts', {'accounts': message.text}))

        await push_state(state, StrategyStates.TOTAL_WEEKS.state)
    except Exception as e:
        logger.error(e)

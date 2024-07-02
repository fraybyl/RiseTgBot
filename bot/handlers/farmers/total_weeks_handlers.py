from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from fluent.runtime import FluentLocalization

from bot.core.loader import bot
from bot.keyboards.farmers_keyboards import get_cancel_strategy_kb
from bot.services.strategy_services.avg_drop_price import get_avg_drop, get_rub_rate
from bot.states.state_helper import push_state
from bot.states.strategy_states import StrategyStates
from bot.utils.investment_strategy import simulate_investment_strategy

total_weeks_router = Router(name=__name__)


@total_weeks_router.message(StrategyStates.TOTAL_WEEKS,
                            lambda message: message.text.isdigit() and int(message.text) > 0)
async def process_total_weeks(message: Message, state: FSMContext, l10n: FluentLocalization):
    try:
        async with ChatActionSender.typing(message.chat.id, bot, interval=1):
            data = await state.get_data()
            message_id = data.get('message_id')
            initial_accounts = data.get('initial_accounts')
            text_strategy = data.get('text_strategy')
            float_strategy = data.get('float_strategy')
            total_weeks = message.text
            account_cost = 550 / await get_rub_rate(2)# 1 - usd to rub // 2 - uah to rub
            avg_price = await get_avg_drop()
            await message.delete()

            profit = simulate_investment_strategy(
                initial_accounts,
                account_cost,
                avg_price,
                total_weeks,
                float_strategy
            )
            caption_text = l10n.format_value(
                'strategy-result',
                {
                    'name': text_strategy,
                    'weeks': int(total_weeks),
                    'price': float(avg_price),
                    'account_price': float(account_cost),
                    'accounts_profit': int(profit[0]),
                    'profit': round(float(profit[1]), 1),
                }
            )

            await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                           reply_markup=get_cancel_strategy_kb(),
                                           caption=caption_text)

            await push_state(state, StrategyStates.CALCULATE.state)
    except Exception as e:
        print(e)

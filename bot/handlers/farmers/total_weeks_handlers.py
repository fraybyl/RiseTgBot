from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from fluent.runtime import FluentLocalization
from loguru import logger
from orjson import orjson

from bot.core.loader import bot, redis_db
from bot.keyboards.farmers_keyboards import get_cancel_strategy_kb
from bot.services.strategy_services.avg_drop_price import get_avg_drop
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
            text_strategy = data.get('text_strategy')

            initial_accounts = int(data.get('initial_accounts'))
            float_strategy = float(data.get('float_strategy'))
            total_weeks = int(message.text)

            async with redis_db.pipeline() as pipe:
                pipe.hget('exchangeRates', 'RUB')
                pipe.hget('exchangeRates', 'UAH')
                results = await pipe.execute()

            rub_ratio: float = float(results[0].decode('utf-8'))
            uah_ratio: float = float(results[1].decode('utf-8'))
            account_cost: float = round((rub_ratio / uah_ratio) * 550, 2)

            avg_price: float = await get_avg_drop()
            await message.delete()

            final_accounts, final_savings, account_count = simulate_investment_strategy(
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
                    'weeks': total_weeks,
                    'price': avg_price,
                    'account_price': account_cost,
                    'accounts_profit': final_accounts,
                    'accounts_count': account_count,
                    'profit': final_savings,
                }
            )

            await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                           reply_markup=get_cancel_strategy_kb(),
                                           caption=caption_text)

            await push_state(state, StrategyStates.CALCULATE.state)
    except Exception as e:
        logger.error(e)

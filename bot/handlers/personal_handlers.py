from aiogram import Router
from aiogram.types import CallbackQuery
from bot.keyboards.user_kb import get_personal_kb
from fluent.runtime import FluentLocalization
from bot.utils import utils
from aiogram.utils.deep_linking import create_start_link
from bot.database.db_requests import get_user_by_telegram_id
from loader import bot

router = Router()

@router.callback_query(lambda query: query.data == "personal")
async def handle_personal_callback(query: CallbackQuery, l10n: FluentLocalization):
    user = await get_user_by_telegram_id(query.from_user.id)
    link = await create_start_link(bot, query.from_user.id, encode=True)
    
    await utils.edit_message_media(query, 'RISE_PERSONAL', reply_markup=get_personal_kb(),
                             caption=l10n.format_value('personal-info', {'discountPercentage': user.discount_percentage, 'bonusPoints': user.bonus_points, 'link': link}))
    await query.answer()
    
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.deep_linking import create_start_link
from fluent.runtime import FluentLocalization

from bot.core.loader import bot
from bot.core.config import settings
from bot.database.db_requests import get_user_by_telegram_id
from bot.keyboards.personal_keyboards import get_personal_kb, get_admins_kb
from bot.utils.edit_media import edit_message_media


router = Router(name=__name__)


@router.callback_query(lambda query: query.data == "personal")
async def handle_personal_callback(query: CallbackQuery, l10n: FluentLocalization):
    user = await get_user_by_telegram_id(query.from_user.id)
    link = await create_start_link(bot, str(query.from_user.id), encode=True)

    if user.telegram_id == settings.ADMINS:
        await edit_message_media(query, 'RISE_PERSONAL', reply_markup=get_admins_kb(),
                                caption=l10n.format_value('personal-info',
                                                        {'discountPercentage': user.discount_percentage,
                                                            'bonusPoints': user.bonus_points, 'link': link}))
    else:
        await edit_message_media(query, 'RISE_PERSONAL', reply_markup=get_personal_kb(),
                            caption=l10n.format_value('personal-info',
                                                    {'discountPercentage': user.discount_percentage,
                                                        'bonusPoints': user.bonus_points, 'link': link}))

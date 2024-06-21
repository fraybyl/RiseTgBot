from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluent.runtime import FluentLocalization

from bot.database.db_requests import get_steamid64_by_userid
from bot.keyboards.farmers_keyboards import get_inventory_kb, get_inventory_settings_kb
from bot.utils.edit_media import edit_message_media
from bot.utils.statistics import get_personal_statistics, get_general_statistics
from .add_accounts_handlers import add_accounts_router

router = Router(name=__name__)
router.include_router(add_accounts_router)


@router.callback_query(lambda query: query.data == "inventory")
async def handle_inventory(query: CallbackQuery, l10n: FluentLocalization):
    user_accounts = await get_steamid64_by_userid(query.from_user.id)
    if user_accounts:
        statistic = await get_personal_statistics(user_accounts, query.from_user.id, l10n)
        await edit_message_media(query, 'RISE_FOR_FARMERS', get_inventory_kb(), caption=statistic)
    else:
        await edit_message_media(query, 'RISE_FOR_FARMERS', get_inventory_kb(),
                                 caption='У вас нет добавленных аккаунтов. Нажмите кнопку "Добавить аккаунты"')
    await query.answer()


@router.callback_query(lambda query: query.data == 'accounts_statistics')
async def handle_accounts_statistics(query: CallbackQuery, l10n: FluentLocalization):
    statistic = await get_general_statistics(l10n)
    await query.message.edit_caption(caption=statistic, reply_markup=get_inventory_settings_kb())
    await query.answer()


@router.callback_query(lambda query: query.data == 'back_inventory')
async def handle_back_inventory(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    await state.clear()
    await handle_inventory(query, l10n)
    await query.answer()

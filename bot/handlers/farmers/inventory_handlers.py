from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization
from loguru import logger

from bot.database.db_requests import get_steamid64_by_userid, set_steamid64_for_user
from bot.keyboards.farmers_keyboards import get_inventory_kb, get_personal_inventory_kb, \
    get_personal_inventory_settings_kb
from bot.utils.edit_media import edit_message_media
from bot.utils.statistics import get_personal_statistics, get_general_statistics
from bot.core.loader import bot
from bot.states.inventory_states import InventoryStates
from bot.services.steamid.fetch_steamid64 import steam_urls_parse
from bot.services.steam_ban.fetch_steam_ban import add_new_accounts
from bot.utils.dump_accounts import dump_accounts

router = Router(name=__name__)


@router.callback_query(lambda query: query.data == "inventory")
async def handle_inventory(query: CallbackQuery, l10n: FluentLocalization):
    general_stat = await get_general_statistics(l10n)
    await edit_message_media(query, 'RISE_FOR_FARMERS', get_inventory_kb(), caption=general_stat)
    await query.answer()


@router.callback_query(lambda query: query.data == "personal_accounts")
async def handle_personal_accounts(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    steam_ids = await get_steamid64_by_userid(query.from_user.id)
    if steam_ids:
        personal_stat = await get_personal_statistics(steam_ids, query.from_user.id, l10n)
        message = await query.message.edit_caption(caption=personal_stat,
                                                   reply_markup=get_personal_inventory_kb())
    else:
        message = await query.message.edit_caption(caption='У вас нет аккаунтов.\nНажмите кнопку добавить аккаунты',
                                                   reply_markup=get_personal_inventory_kb())
    await state.update_data(message_id=message.message_id)
    await query.answer()


@router.callback_query(lambda query: query.data == "add_accounts")
async def handle_add_accounts(query: CallbackQuery, state: FSMContext):
    message = await query.message.edit_caption(caption="Отправьте файл с аккаунтами...",
                                               reply_markup=get_personal_inventory_settings_kb())

    await state.set_state(InventoryStates.WAITING_ADD_ACCOUNTS)
    await state.update_data(message_id=message.message_id)
    await query.answer()


@router.message(InventoryStates.WAITING_ADD_ACCOUNTS, F.document)
async def process_add_accounts(message: Message, state: FSMContext, l10n: FluentLocalization):
    await bot.send_chat_action(message.chat.id, 'upload_document')

    fileid = await bot.get_file(message.document.file_id)
    if not fileid:
        return

    file = await bot.download(fileid)

    content = file.read().decode('utf-8')

    lines = content.splitlines()

    await message.delete()

    steam_ids = await steam_urls_parse(lines)

    data = await state.get_data()
    message_id = data.get('message_id')
    if not steam_ids:
        await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                       caption='Добавлено 0 аккаунтов',
                                       reply_markup=get_personal_inventory_settings_kb())
        return

    if await set_steamid64_for_user(message.from_user.id, steam_ids):
        await add_new_accounts(steam_ids)
        await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                       caption=f'Добавлено {len(steam_ids)} аккаунтов',
                                       reply_markup=get_personal_inventory_settings_kb())
        return

    # добавить обработку инвентарей


@router.callback_query(lambda query: query.data == "get_accounts")
async def handle_get_accounts(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    current_state = await state.get_state()
    if current_state == InventoryStates.WAITING_DUMP_ACCOUTNS:
        return

    accounts = await get_steamid64_by_userid(query.from_user.id)
    if not accounts:
        await query.message.edit_caption(caption='У вас нет аккаунтов для получение.', reply_markup=get_personal_inventory_kb())
        return
    dump_file = await dump_accounts(accounts)

    document_message_id = await bot.send_document(query.message.chat.id, dump_file, caption='Файл удалиться через 30 секунд')
    #scheduler.add_job(ban_statistics_schedule, IntervalTrigger(hours=1))
    await state.set_state(InventoryStates.WAITING_DUMP_ACCOUTNS)
    await state.update_data(document_message_id=document_message_id.message_id)
    await query.answer()


@router.callback_query(lambda query: query.data == 'back_personal_inventory')
async def handle_back_inventory(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    current_state = await state.get_state()
    data = await state.get_data()
    if data.get('document_message_id'):
        await bot.delete_message(query.message.chat.id, data.get('document_message_id'))

    if current_state == InventoryStates.WAITING_ADD_ACCOUNTS:
        await handle_personal_accounts(query, state, l10n)
        await state.clear()
        return
    elif current_state == InventoryStates.WAITING_REMOVE_ACCOUNTS:
        await handle_personal_accounts(query, state, l10n)
        await state.clear()
        return
    elif current_state == InventoryStates.WAITING_DUMP_ACCOUTNS:
        pass


@router.callback_query(lambda query: query.data == 'back_inventory')
async def handle_back_inventory(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    data = await state.get_data()
    if data.get('document_message_id'):
        await bot.delete_message(query.message.chat.id, data.get('document_message_id'))
    await handle_inventory(query, l10n)
    await state.clear()
    await query.answer()


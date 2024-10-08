from aiogram import Router, F
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.chat_action import ChatActionSender
from fluent.runtime import FluentLocalization
from loguru import logger

from bot.core.loader import bot, config_json, redis_db
from bot.database.db_requests import get_steamid64_by_userid, set_steamid64_for_user, remove_steamid64_for_user
from bot.decorators.dec_throttle import throttle
from bot.keyboards.farmers_keyboards import get_inventory_kb, get_personal_inventory_kb, \
    get_personal_inventory_settings_kb
from bot.services.steam_ban.fetch_steam_ban import add_or_update_player_bans
from bot.services.steam_inventory.steam_inventory import SteamInventory
from bot.services.steamid.fetch_steamid64 import steam_urls_parse
from bot.states.inventory_states import InventoryStates
from bot.utils.dump_accounts import dump_accounts
from bot.utils.edit_media import edit_message_media
from bot.utils.remove_data_steam import remove_data_steam
from bot.utils.statistics import get_personal_statistics, get_general_statistics

router = Router(name=__name__)


@router.callback_query(lambda query: query.data == "inventory")
async def handle_inventory(query: CallbackQuery, l10n: FluentLocalization):
    general_stat = await get_general_statistics(l10n, 'steam', 'last_24h')
    await edit_message_media(query, 'RISE_FOR_FARMERS', get_inventory_kb(), caption=general_stat)


@router.callback_query(lambda query: query.data == "personal_accounts")
async def handle_personal_accounts(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    steam_ids = await get_steamid64_by_userid(query.from_user.id)
    if steam_ids:
        personal_stat = await get_personal_statistics(query.from_user.id, steam_ids, l10n, 'steam', 'last_24h')
        message = await query.message.edit_caption(caption=personal_stat,
                                                   reply_markup=get_personal_inventory_kb())
    else:
        message = await query.message.edit_caption(caption=l10n.format_value('personal-accounts-empty'),
                                                   reply_markup=get_personal_inventory_kb())
    await state.update_data(message_id=message.message_id)


@router.callback_query(lambda query: query.data == "add_accounts")
async def handle_add_accounts(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    message = await query.message.edit_caption(
        caption=l10n.format_value('add-accounts-info'),
        reply_markup=get_personal_inventory_settings_kb())
    await state.set_state(InventoryStates.WAITING_ADD_ACCOUNTS)
    await state.update_data(message_id=message.message_id)


async def process_file_accounts(message: Message, message_id: int, l10n: FluentLocalization):
    file_id = message.document
    text_content = message.text

    if not file_id and not text_content:
        await bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message_id,
            caption=l10n.format_value('error-file-found'),
            reply_markup=get_personal_inventory_settings_kb()
        )
        return

    await bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=message_id,
        caption=l10n.format_value('process-accounts-file'),
        reply_markup=get_personal_inventory_settings_kb()
    )

    try:
        if file_id:
            file = await bot.download(file_id)
            content = file.read().decode('utf-8')
        else:
            content = text_content

        lines = content.splitlines()
        await message.delete()

        return lines
    except Exception as e:
        logger.error('Ошибка при обработке %s' % e)
        await bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message_id,
            caption=l10n.format_value('error-process-accounts-file'),
            reply_markup=get_personal_inventory_settings_kb()
        )


@router.message(InventoryStates.WAITING_ADD_ACCOUNTS, or_f(F.document, F.text))
async def process_add_accounts(message: Message, state: FSMContext, l10n: FluentLocalization):
    async with ChatActionSender.upload_document(message.chat.id, bot, interval=1.0):
        data = await state.get_data()
        message_id = data.get('message_id')
        lines = await process_file_accounts(message, message_id, l10n)
        steam_ids_db = await get_steamid64_by_userid(message.from_user.id)
        limit = await config_json.get_config_value('accounts_per_account_limit')

        if len(lines) + len(steam_ids_db) > limit:
            await bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=message_id,
                caption=l10n.format_value('error-quantity-add-accounts', {'accounts_limit': limit}),
                reply_markup=get_personal_inventory_settings_kb()
            )
            return

        steam_ids = await steam_urls_parse(lines)

        if not steam_ids:
            await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                           caption=l10n.format_value('success_add_accounts',
                                                                     {'accounts': len(steam_ids)}),
                                           reply_markup=get_personal_inventory_settings_kb())
            return

        valid_steam_ids = await set_steamid64_for_user(message.from_user.id, steam_ids)

    await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                   caption=l10n.format_value('success_add_accounts', {'accounts': len(steam_ids)}),
                                   reply_markup=get_personal_inventory_settings_kb())

    if valid_steam_ids:
        await add_or_update_player_bans(steam_ids)
        proxies = await config_json.get_config_value('proxies')
        steam_inventory = SteamInventory(proxies, redis_db)
        async with steam_inventory:
            await steam_inventory.process_inventories(valid_steam_ids)


@router.callback_query(lambda query: query.data == "get_accounts")
@throttle(rate_limit=15)
async def handle_get_accounts(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    accounts = await get_steamid64_by_userid(query.from_user.id)
    if not accounts:
        await query.message.edit_caption(caption=l10n.format_value('error-accounts-dump'),
                                         reply_markup=get_personal_inventory_kb())
        return
    dump_file = await dump_accounts(accounts)

    document_message_id = await bot.send_document(query.message.chat.id, dump_file,
                                                  caption=l10n.format_value('get-accounts-dump'))

    await state.update_data(document_message_id=document_message_id.message_id)


@router.callback_query(lambda query: query.data == "remove_accounts")
async def handle_remove_accounts(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    message = await query.message.edit_caption(caption=l10n.format_value('remove-accounts-info'),
                                               reply_markup=get_personal_inventory_settings_kb())

    await state.set_state(InventoryStates.WAITING_REMOVE_ACCOUNTS)
    await state.update_data(message_id=message.message_id)


@router.message(InventoryStates.WAITING_REMOVE_ACCOUNTS, or_f(F.document, F.text))
async def process_remove_accounts(message: Message, state: FSMContext, l10n: FluentLocalization):
    async with ChatActionSender.upload_document(message.chat.id, bot, interval=1.0):
        data = await state.get_data()
        message_id = data.get('message_id')
        lines = await process_file_accounts(message, message_id, l10n)

        steam_ids = await steam_urls_parse(lines)

        if not steam_ids:
            await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                           caption=l10n.format_value('error-not-steam_ids_dump'),
                                           reply_markup=get_personal_inventory_settings_kb())
            return

        removed_accounts = await remove_steamid64_for_user(message.from_user.id, steam_ids)

        await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                       caption=l10n.format_value('success-remove-accounts',
                                                                 {'length_accounts': len(removed_accounts)}),
                                       reply_markup=get_personal_inventory_settings_kb())

        if removed_accounts:
            await remove_data_steam(removed_accounts)


@router.callback_query(lambda query: query.data == 'back_personal_inventory')
async def handle_back_inventory(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    current_state = await state.get_state()
    data = await state.get_data()

    if current_state == InventoryStates.WAITING_ADD_ACCOUNTS:
        await handle_personal_accounts(query, state, l10n)
        await state.clear()
    elif current_state == InventoryStates.WAITING_REMOVE_ACCOUNTS:
        await handle_personal_accounts(query, state, l10n)
        await state.clear()

    if data.get('document_message_id'):
        await bot.delete_message(query.message.chat.id, data.get('document_message_id'))


@router.callback_query(lambda query: query.data == 'back_inventory')
async def handle_back_inventory(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    await handle_inventory(query, l10n)
    data = await state.get_data()
    if data.get('document_message_id'):
        await bot.delete_message(query.message.chat.id, data.get('document_message_id'))

    await state.clear()

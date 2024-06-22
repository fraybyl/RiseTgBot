from typing import LiteralString

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization
from loguru import logger

from bot.core.loader import bot
from bot.database.db_requests import get_steamid64_by_userid, remove_steamid64_for_user
from bot.keyboards.farmers_keyboards import get_accounts_settings_kb, get_inventory_settings_kb
from bot.services.steamid.fetch_steamid64 import steam_urls_parse
from bot.utils.dump_accounts import dump_accounts
from bot.states.inventory_states import InventoryStates

router = Router(name=__name__)


@router.callback_query(lambda query: query.data == 'accounts_actions')
async def handle_accounts_actions(query: CallbackQuery, l10n: FluentLocalization):
    await query.message.edit_caption(caption='удаляй нахуй давай удаляй', reply_markup=get_accounts_settings_kb())
    await query.answer()


@router.callback_query(lambda query: query.data == 'dump_accounts')
async def handle_dump_accounts(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    data = await state.get_data()
    if data.get('document_id'):
        await query.answer()
        return

    accounts = await get_steamid64_by_userid(query.from_user.id)
    if not accounts:
        await query.message.edit_caption(caption='У вас нет аккаунтов.', reply_markup=get_accounts_settings_kb())
        return

    file = await dump_accounts(accounts)
    message = await bot.send_document(query.message.chat.id, file)

    await query.message.edit_caption(
        caption=query.message.caption + '\nПри нажатие кнопки назад, файл с аккаунтами удалится',
        reply_markup=get_accounts_settings_kb())

    await state.set_state(InventoryStates.GET_DUMP_FILE)
    await state.update_data(document_id=message.message_id)

    await query.answer()


@router.callback_query(lambda query: query.data == 'remove_accounts')
async def handle_accounts_remove(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    message = await query.message.edit_caption(caption='Отправьте файл с аккаунтами, которые НУЖНО удалить',
                                               reply_markup=get_inventory_settings_kb())
    await state.set_state(InventoryStates.WAITING_INVENTORY_REMOVE)
    await state.update_data(query_id=message.message_id)
    await query.answer()


@router.message(InventoryStates.WAITING_INVENTORY_REMOVE)
async def process_accounts_remove(message: Message, state: FSMContext):
    lines: list[LiteralString]

    if message.content_type == ContentType.DOCUMENT:
        document_id = message.document.file_id
        file_info = await bot.get_file(document_id)
        file_path = file_info.file_path
        file = await bot.download_file(file_path)
        content = file.read().decode('utf-8')
        lines = content.splitlines()
    elif message.content_type == ContentType.TEXT:
        text = message.text
        lines = text.splitlines()
    else:
        await message.delete()
        return

    data = await state.get_data()
    message_id = data.get('query_id')

    await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                   reply_markup=get_inventory_settings_kb(),
                                   caption="Идет обработка, пожалуйста подождите...")
    await bot.send_chat_action(message.chat.id, 'upload_document')
    await message.delete()
    try:
        steam_ids = await steam_urls_parse(lines)
        deleted_accounts = await remove_steamid64_for_user(message.from_user.id, steam_ids)
        await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                       reply_markup=get_accounts_settings_kb(),
                                       caption=f"Удалено {len(deleted_accounts) if deleted_accounts is not None else 'None'} аккаунтов")
        document_id = data.get('document_id')
        if document_id:
            await bot.delete_message(message.chat.id, document_id)
    except Exception as e:
        logger.error('Ошибка при удаление аккаунтов: %s' % e)

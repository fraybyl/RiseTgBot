from typing import LiteralString

from aiogram import Router
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

from bot.core.loader import bot, config_json
from bot.database.db_requests import set_steamid64_for_user

from bot.keyboards.farmers_keyboards import get_inventory_settings_kb
from bot.services.steam_ban.fetch_steam_ban import add_new_accounts
from bot.services.steam_inventory.steam_inventory import SteamParser
from bot.services.steamid.fetch_steamid64 import steam_urls_parse
from bot.states.inventory_states import InventoryStates

add_accounts_router = Router(name=__name__)


@add_accounts_router.callback_query(lambda query: query.data == 'add_accounts')
async def handle_add_accounts(query: CallbackQuery, state: FSMContext):
    message_id = await query.message.edit_caption(
        caption='Введите пажэ список инвентарей.\nСписок можно передать в формате steamid64 или ссылками на профиль. Если отправляете сообщением, то не больше 90 строк.',
        reply_markup=get_inventory_settings_kb())
    await state.set_state(InventoryStates.WAITING_INVENTORY_LIST)
    await state.update_data(message_id=message_id.message_id)
    await query.answer()


@add_accounts_router.message(InventoryStates.WAITING_INVENTORY_LIST)
async def process_inventory_list(message: Message, state: FSMContext, l10n: FluentLocalization):
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
    message_id = data.get('message_id')

    await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                   reply_markup=get_inventory_settings_kb(),
                                   caption="Идет обработка, пожалуйста подождите...")
    await bot.send_chat_action(message.chat.id, 'upload_document')

    try:
        successful_result = await steam_urls_parse(lines)
        await message.delete()
        await set_steamid64_for_user(message.from_user.id, successful_result)
        #await add_new_accounts(successful_result)
        await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                       reply_markup=get_inventory_settings_kb(),
                                       caption=f"Добавлено {len(successful_result)} аккаунт\nнажмите кнопку назад")
        await state.clear()
        #proxies = await config_json.get_config_value('proxies')
        #steam_parser = SteamParser(proxies)
        #await steam_parser.process_inventories(successful_result)
    except Exception as e:
        print(f"Error processing inventory list: {e}")
        await message.reply("There was an error processing your file.")

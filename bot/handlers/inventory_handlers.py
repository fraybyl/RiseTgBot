import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ContentType
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization
from bot.keyboards.user_kb import get_inventory_kb, get_inventory_settings_kb
from bot.utils import utils
from bot.utils.steamid import steam_urls_parse, get_accounts_statistics
from bot.states.inventory_states import InventoryStates
from loader import bot
from bot.handlers.error_handlers import handle_error_back
from bot.database.db_requests import  get_steamid64_by_userid, set_steamid64_for_user, get_all_steamid64

router = Router()

@router.callback_query(lambda query: query.data == "inventory")
async def handle_inventory(query: CallbackQuery):
    user_accs = await get_steamid64_by_userid(query.from_user.id)
    if user_accs:
        await utils.edit_message_media(query, 'RISE_FOR_FARMERS', get_inventory_kb(), caption=f"Ваши аккаунты: {len(user_accs)}")
    else:
        await utils.edit_message_media(query, 'RISE_FOR_FARMERS', get_inventory_kb(), caption='У вас нет добавленных аккаунтов. Нажмите кнопку "Добавить аккаунты"')
    


    
@router.callback_query(lambda query: query.data == 'add_accounts')
async def handle_add_accounts(query: CallbackQuery, state: FSMContext):
    message_id = await query.message.edit_caption(caption='Введите пажэ список инвентарей.\nСписок можно передать в формате steamid64 или ссылками на профиль. Если отправляете сообщением, то не больше 90 строк.', reply_markup=get_inventory_settings_kb())
    await state.set_state(InventoryStates.WAITING_INVENTORY_LIST)
    await state.update_data(message_id=message_id.message_id)
    
@router.callback_query(lambda query: query.data == 'accounts_statistics')
async def handle_accounts_statistics(query: CallbackQuery, l10n: FluentLocalization):
    all_accounts = await get_all_steamid64()
    personal_accounts = await get_steamid64_by_userid(query.from_user.id)
    personal_bans, personal_vac, personal_community, personal_game_bans, personal_bans_last_week = await get_accounts_statistics(personal_accounts)
    total_bans, total_vac, total_community, total_game_bans, bans_last_week = await get_accounts_statistics(all_accounts)
    text = l10n.format_value('general-accounts-info', {'personal_accounts': len(personal_accounts),
                                                'personal_bans': personal_bans,
                                                'personal_vac': personal_vac,
                                                'personal_community': personal_community, 
                                                'personal_gameban': personal_game_bans,
                                                'personal_bans_in_last_week': personal_bans_last_week,
                                                'accounts': len(all_accounts), 
                                                'total_bans': total_bans, 
                                                'total_vac': total_vac, 
                                                'total_community': total_community, 
                                                'total_gameban': total_game_bans,  
                                                'bans_in_last_week': bans_last_week})
    await query.message.edit_caption(caption=text, reply_markup=get_inventory_settings_kb())
    

@router.callback_query(lambda query: query.data == 'back_inventory')
async def handle_back_inventory(query:CallbackQuery, state: FSMContext):
    await state.clear()
    await handle_inventory(query)    
        
@router.message(InventoryStates.WAITING_INVENTORY_LIST)
async def process_inventory_list(message: Message, state: FSMContext):
    
    if(message.content_type == ContentType.DOCUMENT):
        document_id = message.document.file_id
        file_info = await bot.get_file(document_id)
        file_path = file_info.file_path
        file = await bot.download_file(file_path)
        content = file.read().decode('utf-8')
        lines = content.splitlines()
    elif(message.content_type == ContentType.TEXT):
        text = message.text
        lines = text.splitlines()
    
    data = await state.get_data()
    message_id = data.get('message_id')
    
    await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, reply_markup=get_inventory_settings_kb(), caption="Идет обработка, пожалуйста подождите...")
    await bot.send_chat_action(message.chat.id, 'upload_document')
    
    try:
        successful_result = await steam_urls_parse(lines)
        await message.delete()
        await set_steamid64_for_user(message.from_user.id, successful_result) 
        await bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, reply_markup=get_inventory_kb(), caption=f"Ваши аккаунты: ")
        await state.clear()
    except Exception as e:
        print(f"Error processing inventory list: {e}")
        await message.reply("There was an error processing your file.")


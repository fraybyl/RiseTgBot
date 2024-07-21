import os
import json
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from fluent.runtime import FluentLocalization
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from loguru import logger

from bot.core.loader import bot
from bot.database.db_requests import get_all_users, set_categories, get_category_by_name, delete_categories
from bot.keyboards.admin_keyboards import get_admins_kb, get_categories_kb, get_close_category_kb, add_category_kb, get_all_categories_kb, confirmation_delete_kb
from bot.states.admins_state import AdminState
from bot.core.config import settings
from bot.states.state_helper import push_state, pop_state
from bot.utils.edit_media import edit_message_media

router = Router(name=__name__)
PHOTO_DIR = 'data/photos'
FILE_IDS_JSON = 'data/file_ids.json'

async def download_and_save_photo(file_id: str, photo_filename: str):
    file = await bot.get_file(file_id)
    file_path = file.file_path
    if not photo_filename.endswith('.jpg'):
        photo_filename += '.jpg'
        photo_filename.replace(' ', '_')    
    destination = os.path.join(PHOTO_DIR, photo_filename)    
    await bot.download_file(file_path, destination)
    update_file_ids(photo_filename, destination)
    return destination

def update_file_ids(photo_filename, path):
    if photo_filename.endswith('.jpg'):
        photo_filename = photo_filename[:-4]
    photo_filename = photo_filename.replace(' ', '_')
    path = path.replace('\\', '/')
    with open(FILE_IDS_JSON, 'r', encoding='utf-8') as file:
        file_ids = json.load(file)
    file_ids[photo_filename] = {
        "path": path
    }
    with open(FILE_IDS_JSON, 'w', encoding='utf-8') as file:
        json.dump(file_ids, file, ensure_ascii=False, indent=4)

    logger.success(f"Файл {photo_filename} успешно добавлен в file_ids.json")


@router.callback_query(lambda query: query.data == "admin_panel")
async def amdin_panel_handlers(query: CallbackQuery, l10n: FluentLocalization):
    users = await get_all_users()
    await edit_message_media(query, 'RISE_PERSONAL', reply_markup=get_admins_kb(), caption=l10n.format_value('admin-info', {'members': len(users)}))

@router.callback_query(lambda query: query.data =="add_products")
async def add_proudcts_handlers (query: CallbackQuery):
    await edit_message_media(query, 'RISE_PERSONAL', caption="Пожалуйста, выберите категорию, которую вы хотите изменить", reply_markup=await get_categories_kb())

@router.callback_query(lambda query: query.data == "adding_new")
async def category_new_handlers(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    await edit_message_media(query, 'RISE_PERSONAL', caption="ПАЖЭ ВВЕДИ НАЗВАНИЕ КАТЕГОРИИ", reply_markup=get_close_category_kb())
    await push_state(state, AdminState.ADD_CATEGORY_STATE.state)

@router.message(AdminState.ADD_CATEGORY_STATE)
async def category_new_message(message: Message, state: FSMContext):
    name_category = message.text
    await state.update_data(name_category=name_category)
    await message.delete()
    await message.answer(text=f"название категории: {name_category}\nТеперь введите PHOTO_FILENAME или отправьте фото", reply_markup=get_close_category_kb())
    await push_state(state, AdminState.ADD_PHOTO_FILENAME_STATE.state)

@router.message(AdminState.ADD_PHOTO_FILENAME_STATE)
async def photo_filename_message(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    name_category = data.get('name_category')
    
    if message.photo:
        photo_filename = name_category

        await download_and_save_photo(file_id=photo, photo_filename=photo_filename)

        await state.update_data(photo_filename=photo_filename, photo_file_id=photo,name_category=name_category)

        await message.delete()
        await message.answer_photo(photo=photo, caption=f"Категория: {name_category}\nФото загружено", reply_markup=add_category_kb())
    else:
        photo_filename = message.text
        await state.update_data(photo_filename=photo_filename,name_category=name_category)  # Сохраняем имя файла фото в состоянии
        await message.delete()
        await message.answer(text=f"Имя файла фото: {photo_filename}\nТеперь отправьте фото", reply_markup=get_close_category_kb())


@router.callback_query(lambda query: query.data == "send_adding")
async def set_new_category_handlers(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name_category = data.get('name_category')
    photo_filename = data.get('photo_filename')
    photo = data.get('photo_file_id')   

    try:
        await set_categories(name_category, photo_filename)
        await query.message.answer_photo(photo=photo, caption=f"Категория: {name_category}\n\nДанные успешно добавлены в базу данных", reply_markup=get_close_category_kb())
        await state.clear()
    except Exception as e:
        await query.message.answer(text=f"Произошла ошибка при добавлении категории: {e}", reply_markup=get_close_category_kb())
        await state.clear()
    


@router.callback_query(lambda query: query.data == "adding_delete")
async def adding_delete_handlers(query: CallbackQuery, state: FSMContext):
    await edit_message_media(query, "RISE_PERSONAL", caption="ПАЖЭ НАЖМИ НА КАТЕГОРИЮ КОТОРУЮ ХОЧ УДАЛИТЬ", reply_markup=await get_all_categories_kb())

@router.callback_query(lambda query: query.data.startswith("dell_"))
async def category_handlers(query: CallbackQuery, state: FSMContext):
    await push_state(state, AdminState.DELETE_CATEGORY_STATE.state)
    category_name = query.data.split("_")[1]
    category = await get_category_by_name(category_name)

    if category:
        await state.update_data(category_name=category.name)
        confirmation_text = f"Вы выбрали категорию '{category.name}'. Вы действительно хотите её удалить?"
        await edit_message_media(query, "RISE_PERSONAL", caption=confirmation_text, reply_markup=confirmation_delete_kb())


@router.callback_query(lambda query: query.data == "delete_name")
async def confirm_delete_handlers(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_name = data.get('category_name')

    if category_name:
        deleted = await delete_categories(category_name)

        if deleted:
            await edit_message_media(query, "RISE_PERSONAL", caption=f"Категория '{category_name}' успешно удалена", reply_markup=get_close_category_kb())
            await pop_state(state)
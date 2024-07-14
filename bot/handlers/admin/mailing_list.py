from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from loguru import logger

from bot.core.loader import bot
from bot.database.db_requests import get_all_users
from bot.keyboards.admin_keyboards import get_close_mailing_kb, get_mailing_kb
from bot.states.admins_state import AdminState
from bot.core.config import settings
from bot.states.state_helper import push_state, pop_state
from bot.utils.edit_media import edit_message_media

router = Router(name=__name__)

@router.callback_query(lambda query: query.data in ["mailing_list", "edit_mail"])
async def mailing_list_handlers(query: CallbackQuery, state: FSMContext):
    print(f"Received callback data: {query.data}")
    await edit_message_media(query,'RISE_PERSONAL', caption="Напишите текст рассылки", reply_markup=get_close_mailing_kb())
    await push_state(state, AdminState.MAILING_LIST_STATE.state)

@router.message(AdminState.MAILING_LIST_STATE)
async def add_mailing_message(message: Message, state: FSMContext):
    print(message.photo)
    if message.photo:
        photo = message.photo[-1].file_id
        text = message.caption if message.caption else ""
        await state.update_data(mailing_photo=photo, mailing_text=text)
        await message.delete()
        await message.answer_photo(photo=photo, caption=f"Текст рассылки:\n\n{text}", reply_markup=get_mailing_kb())
    elif message.text:
        text = message.text
        await state.update_data(mailing_text=text)
        await message.delete()
        await message.answer(text=f"Текст рассылки\n\n{text}", reply_markup=get_mailing_kb())
    else:
        await message.answer("Пожалуйста, отправьте текст или фотографию для рассылки.")

@router.callback_query(lambda query: query.data == "send_mail")
async def send_mailing_handler(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photo = data.get("mailing_photo", None)
    text = data.get("mailing_text", "")

    if not (photo or text):
        await query.message.answer("Текст или фотография для рассылки не найдены. Пожалуйста, начните с начала.")
        return

    users = await get_all_users()
    for user in users:
        try:
            chat_id = user.telegram_id
            if photo:
                await bot.send_photo(chat_id=chat_id, photo=photo, caption=text)
            else:
                await bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю с telegram_id {chat_id}: {e}")

    await query.message.answer(text="Рассылка отправлена!", reply_markup=get_close_mailing_kb())

    previous_state = await pop_state(state)
    logger.info(f"Возвращение к предыдущему состоянию: {previous_state}")

@router.callback_query(lambda query: query.data == "close_mail")
async def close_mail_handlers(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.clear()
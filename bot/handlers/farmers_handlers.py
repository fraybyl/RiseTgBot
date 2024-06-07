from aiogram import Router
from aiogram.types import CallbackQuery
from bot.keyboards.farmers_keyboard import get_farmers_kb
from bot.keyboards.start_keyboard import get_start_kb
from bot.utils.photo_answer_util import edit_message_media

router = Router()

@router.callback_query(lambda query: query.data == "farmers")
async def handle_farmers_callback(query: CallbackQuery):
    await edit_message_media(query, "RISE_FOR_FARMERS", get_farmers_kb())
    
@router.callback_query(lambda query: query.data == "back_farmers")
async def handle_back_farmers_callback(query: CallbackQuery):
    await edit_message_media(query, "RISE_BACKGROUND", get_start_kb())
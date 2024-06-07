from aiogram import Router
from aiogram.types import CallbackQuery
from bot.keyboards.shop_keyboard import get_shop_kb
from bot.keyboards.start_keyboard import get_start_kb
from bot.utils.photo_answer_util import edit_message_media

router = Router()

@router.callback_query(lambda query: query.data == "shop")
async def handle_shop_callback(query: CallbackQuery):
    await edit_message_media(query, "RISE_SHOP", get_shop_kb())
    
@router.callback_query(lambda query: query.data == "back_shop")
async def handle_back_shop_callback(query: CallbackQuery):
    await edit_message_media(query, "RISE_BACKGROUND", get_start_kb())
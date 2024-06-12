from aiogram import Router
from aiogram.types import Message, CallbackQuery
from bot.keyboards.user_kb import get_shop_kb
from fluent.runtime import FluentLocalization
from bot.utils import utils


router = Router()

@router.callback_query(lambda query: query.data == "shop")
async def handle_shop(query: CallbackQuery):
    await utils.edit_message_media(query, 'RISE_SHOP', await get_shop_kb())
    
    
@router.callback_query(lambda query: query.data == "back_shop")
async def handle_back_shop(query: CallbackQuery):
    await utils.edit_message_media(query, 'RISE_SHOP', await get_shop_kb())
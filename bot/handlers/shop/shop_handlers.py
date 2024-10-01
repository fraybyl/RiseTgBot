from aiogram import Router
from aiogram.types import CallbackQuery

from bot.keyboards.shop_keyboards import get_shop_kb
from bot.utils.edit_media import edit_message_media

router = Router(name=__name__)


@router.callback_query(lambda query: query.data == "shop")
async def handle_shop(query: CallbackQuery):
    await edit_message_media(query, 'RISE_SHOP', await get_shop_kb())


@router.callback_query(lambda query: query.data == "back_shop")
async def handle_back_shop(query: CallbackQuery):
    await edit_message_media(query, 'RISE_SHOP', await get_shop_kb())

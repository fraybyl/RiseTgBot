from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.farmers_keyboards import get_farmers_kb
from bot.utils.edit_media import edit_message_media

router = Router(name=__name__)


@router.callback_query(lambda query: query.data == "farmers")
async def handle_farmers(query: CallbackQuery):
    await edit_message_media(query, 'RISE_FOR_FARMERS', get_farmers_kb())



@router.callback_query(lambda query: query.data == "back_farmers")
async def handle_back_farmers(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await edit_message_media(query, 'RISE_FOR_FARMERS', get_farmers_kb())

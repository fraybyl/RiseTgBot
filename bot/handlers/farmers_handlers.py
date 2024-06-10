from aiogram import Router
from aiogram.types import CallbackQuery
from bot.keyboards.user_kb import get_farmers_kb
from bot.utils import utils


router = Router()

@router.callback_query(lambda query: query.data == "farmers")
async def handle_farmers(query: CallbackQuery):
    await utils.edit_message_media(query, 'RISE_FOR_FARMERS', get_farmers_kb())
    
    
        
    
@router.callback_query(lambda query: query.data == "back_farmers")
async def handle_back_farmers(query: CallbackQuery):
    await utils.edit_message_media(query, 'RISE_FOR_FARMERS', get_farmers_kb())
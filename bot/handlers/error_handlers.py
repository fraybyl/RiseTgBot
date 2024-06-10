from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards.user_kb import get_start_kb, get_cancel_order_kb
from fluent.runtime import FluentLocalization
from bot.states.order_states import OrderStates
from bot.utils import utils
from loader import bot, logging

async def handle_error_back(query: CallbackQuery, state: FSMContext):
        if(state):
                await state.clear()
                
        await utils.edit_message_media(query, "RISE_BACKGROUND", get_start_kb())
        
async def send_error_order_message(chat_id, message_id, text):
    try:
        await bot.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=text,
            reply_markup=get_cancel_order_kb()
        )
    except Exception as e:
        logging.error(f"Failed to send error message: {e}")
        

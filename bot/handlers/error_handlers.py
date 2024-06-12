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
        

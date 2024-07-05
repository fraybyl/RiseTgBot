from aiogram import Router
from aiogram import F
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization
from aiogram.fsm.context import FSMContext

from bot.core.loader import bot
from bot.database.db_requests import *
from bot.keyboards.personal_keyboards import *
from bot.utils.edit_media import *
from bot.states.admins_state import AdminState
from bot.core.config import BotSettings
router = Router(name=__name__)

@router.message(AdminState.ADMIN_MESSAGE, lambda message: message.text == "/admin" and F.from_user.id  == BotSettings.ADMINS)
async def admin_message(message: Message, state: FSMContext, l10n: FluentLocalization):
 await message.answer()
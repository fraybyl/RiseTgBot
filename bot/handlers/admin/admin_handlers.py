from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from fluent.runtime import FluentLocalization

from bot.core.config import BotSettings
from bot.states.admins_state import AdminState

router = Router(name=__name__)


@router.message(AdminState.ADMIN_MESSAGE,
                lambda message: message.text == "/admin" and F.from_user.id == BotSettings.ADMINS)
async def admin_message(message: Message, state: FSMContext, l10n: FluentLocalization):
    await message.answer()

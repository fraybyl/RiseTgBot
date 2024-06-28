from aiogram import Router
from aiogram.types import CallbackQuery

from bot.core.loader import bot
from bot.keyboards.message_distribution_keyboards import get_ban_dump_kb
from bot.utils.dump_accounts import dump_accounts

router = Router(name=__name__)


async def send_message_ban(user_id: int, steam_ids: list[int]) -> None:
    file = await dump_accounts(steam_ids)
    await bot.send_document(user_id, file, caption=f'У вас есть забаненные аккаунты!!\n{len(steam_ids)} аккаунтов', reply_markup=get_ban_dump_kb())


@router.callback_query(lambda query: query.data == "cancel_dump_accounts")
async def get_ban_dump(query: CallbackQuery):
    await query.message.delete()

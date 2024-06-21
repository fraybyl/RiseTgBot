from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.utils.payload import decode_payload
from loguru import logger

from bot.database import db_requests
from bot.core.loader import config_json
from bot.utils.edit_media import edit_message_media
from bot.keyboards.start_keyboards import get_start_kb

router = Router(name=__name__)


@router.message(CommandStart())
async def command_start_handler(message: Message, command: CommandObject) -> None:
    args = command.args
    payload = decode_payload(args) if args else None
    await db_requests.set_user(message.from_user.id, message.from_user.username, payload)

    if await config_json.has_file_id("RISE_BACKGROUND"):
        await message.answer_photo(photo=await config_json.get_file_id("RISE_BACKGROUND"), reply_markup=get_start_kb())
    else:
        file = await config_json.get_file_path("RISE_BACKGROUND")
        if file:
            photo = FSInputFile(file)
            sent_photo = await message.answer_photo(photo=photo, reply_markup=get_start_kb())
            file_id = sent_photo.photo[-1].file_id
            await config_json.save_file_id(file_id, "RISE_BACKGROUND")
        else:
            logger.error("файл не найден. starthandlers")


@router.callback_query(lambda query: query.data == "back_start")
async def handle_back_start(query: CallbackQuery):
    await edit_message_media(query, 'RISE_BACKGROUND', get_start_kb())
    await query.answer()

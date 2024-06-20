from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, FSInputFile, CallbackQuery
from loader import fileIds, logging
from aiogram.utils.deep_linking import decode_payload
from bot.keyboards.user_kb import get_start_kb
from fluent.runtime import FluentLocalization
from bot.utils import utils
from bot.database import db_requests

router = Router(name=__name__)

@router.message(CommandStart())
async def command_start_handler(message: Message, command: CommandObject, l10n: FluentLocalization) -> None:
    args = command.args
    payload = decode_payload(args) if args else None
    await db_requests.set_user(message.from_user.id, message.from_user.username, payload)
    
    if fileIds.has_file_id("RISE_BACKGROUND"):
        await message.answer_photo(photo=fileIds.get_file_id("RISE_BACKGROUND"), reply_markup=get_start_kb())
    else:
        file = fileIds.get_file_path("RISE_BACKGROUND")
        if file:
            photo = FSInputFile(file)
            sent_photo = await message.answer_photo(photo=photo, reply_markup=get_start_kb())
            file_id = sent_photo.photo[-1].file_id
            fileIds.save_file_id(file_id, "RISE_BACKGROUND")
        else:
            logging.error("файл не найден. starthandlers")
            
@router.callback_query(lambda query: query.data == "back_start")
async def handle_back_start(query: CallbackQuery):
    await utils.edit_message_media(query, 'RISE_BACKGROUND', get_start_kb())
    await query.answer()
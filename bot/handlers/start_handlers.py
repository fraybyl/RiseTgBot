from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from bot.keyboards.start_keyboard import  get_start_kb
from aiogram.fsm.context import FSMContext
from loader import fileIds, logging

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
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


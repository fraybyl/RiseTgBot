import logging
from aiogram.types import FSInputFile, CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup
from loader import fileIds

async def edit_message_media(callback_query: CallbackQuery, media=None, reply_markup=None, caption=None):
    try:
        file_id = fileIds.get_file_id(media)
        if file_id:
            sent_message = await callback_query.message.edit_media(
                media=InputMediaPhoto(media=file_id, caption=caption),
                reply_markup=reply_markup
            )
        else:
            file_path = fileIds.get_file_path(media)
            if file_path:
                photo = FSInputFile(file_path)
                sent_message = await callback_query.message.edit_media(
                    media=InputMediaPhoto(media=photo, caption=caption),
                    reply_markup=reply_markup
                )
                fileIds.save_file_id(sent_message.photo[-1].file_id, media)
            else:
                raise FileNotFoundError('Не удалось найти путь к файлу.')
        return sent_message.message_id
    except Exception as e:
        logging.error(f'Произошла непредвиденная ошибка: {e}')


from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InputMediaPhoto, FSInputFile
from bot.core.loader import config_json
from loguru import logger


async def edit_message_media(callback_query: CallbackQuery, media: str = None,
                             reply_markup: InlineKeyboardMarkup = None, caption: str = None) -> int | None:
    try:
        file_id = await config_json.get_file_id(media)
        if file_id:
            sent_message = await callback_query.message.edit_media(
                media=InputMediaPhoto(media=file_id, caption=caption),
                reply_markup=reply_markup
            )
        else:
            file_path = await config_json.get_file_path(media)
            if file_path:
                photo = FSInputFile(file_path)
                sent_message = await callback_query.message.edit_media(
                    media=InputMediaPhoto(media=photo, caption=caption),
                    reply_markup=reply_markup
                )
                await config_json.save_file_id(sent_message.photo[-1].file_id, media)
            else:
                raise FileNotFoundError('Не удалось найти путь к файлу.')
        return sent_message.message_id
    except Exception as e:
        logger.error(f'Произошла непредвиденная ошибка: {e}')
        return None

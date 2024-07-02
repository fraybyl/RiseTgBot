from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InputMediaPhoto, FSInputFile
from loguru import logger

from bot.core.loader import config_json


async def edit_message_media(
        callback_query: CallbackQuery,
        media: str = None,
        reply_markup: InlineKeyboardMarkup = None,
        caption: str = None
) -> int | None:
    """
    Асинхронно редактирует медиа-сообщение в ответ на callback_query.

    Args:
        callback_query (CallbackQuery): Объект callback_query.
        media (str, optional): Имя или путь к медиа-файлу. Defaults to None.
        reply_markup (InlineKeyboardMarkup, optional): Объект InlineKeyboardMarkup для сообщения. Defaults to None.
        caption (str, optional): Подпись к медиа-файлу. Defaults to None.

    Returns:
        int | None: ID отредактированного сообщения или None в случае ошибки.
    """
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

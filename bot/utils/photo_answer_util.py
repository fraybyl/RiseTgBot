import logging
from typing import Dict, Optional, Union
from aiogram.methods import EditMessageMedia
from aiogram.types import FSInputFile, CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup
from loader import fileIds, bot

async def edit_message_media(callbackQuery: CallbackQuery, media: str = None,  reply_markup: Optional[InlineKeyboardMarkup] = None, caption: str = None) -> Dict[int, int]:
    try:
        if media in fileIds.file_ids:
            if fileIds.has_file_id(media):  
                sent_message = await callbackQuery.message.edit_media(media=InputMediaPhoto(media=fileIds.get_file_id(media), caption=caption), reply_markup=reply_markup)
                return sent_message.chat.id, sent_message.message_id
            else:
                file_path = fileIds.get_file_path(media)
                if file_path:
                    photo = FSInputFile(file_path)
                    sent_message = await callbackQuery.message.edit_media(media=InputMediaPhoto(media=photo, caption=caption), reply_markup=reply_markup)
                    file_id = sent_message.photo[-1].file_id  
                    fileIds.save_file_id(file_id, media)
                    return sent_message.chat.id, sent_message.message_id
                else:
                    logging.error('Не удалось изменить медиа')
        else:
            logging.error('Не удалось найти фото')
    except Exception as e: 
        logging.error(f'Произошла непредвиденная ошибка: {e}')  
        
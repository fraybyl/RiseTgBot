import logging
from aiogram.types import FSInputFile, CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup
from steam import steamid
from loader import fileIds
import concurrent.futures
from typing import Union
from functools import lru_cache

async def edit_message_media(callback_query: CallbackQuery, media: str = None, reply_markup: InlineKeyboardMarkup = None, caption: str = None) -> int:
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

@lru_cache(maxsize=65536)
def convert_to_steamid64(line: str) -> Union[int, None]:
    try:
        if line.isdigit() and len(line) == 17:
            return int(line)
        
        steam_id = steamid.from_url(line)
        if steam_id:
            return steam_id.as_64
        else:
            return None
    except Exception as e:
        print(f"Error converting line '{line}' to SteamID64: {e}")
        return None

def process_lines_multithread(lines: list[str]) -> list[Union[int, None]]:
    responses = []
    
    def process_line(line):
        return convert_to_steamid64(line)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_line, line) for line in lines]
        
        for future in concurrent.futures.as_completed(futures):
            response = future.result()
            if(response):
                responses.append(response)
    
    return responses
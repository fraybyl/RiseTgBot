import asyncio
from aiogram.types import BufferedInputFile

def convert_steamid_to_link(steam_id: int) -> str:
    """
    Преобразует SteamID в ссылку на профиль Steam Community.

    Args:
        steam_id (int): SteamID пользователя.

    Returns:
        str: Ссылка на профиль Steam Community.
    """
    return f"https://steamcommunity.com/profiles/{steam_id}"

async def process_bytes(steam_ids: list[int]) -> bytes:
    """
    Обрабатывает список SteamID и формирует строку с ссылками.

    Args:
        steam_ids (list[int]): Список SteamID пользователей.

    Returns:
        bytes: Строка, содержащая ссылки на профили Steam Community в формате bytes.
    """
    links = [convert_steamid_to_link(steam_id) for steam_id in steam_ids]
    steam_ids_str = '\n'.join(links) + '\n'
    return steam_ids_str.encode('utf-8')

async def dump_accounts(steam_ids: list[int], chunk_size: int = 1000) -> BufferedInputFile:
    """
    Формирует файл для загрузки со списком SteamID в формате txt.

    Args:
        steam_ids (list[int]): Список SteamID пользователей.
        chunk_size (int, optional): Размер чанка для обработки. Defaults to 1000.

    Returns:
        BufferedInputFile: Объект BufferedInputFile для асинхронной загрузки файла.
    """
    chunks = [steam_ids[i:i + chunk_size] for i in range(0, len(steam_ids), chunk_size)]
    tasks = [process_bytes(chunk) for chunk in chunks]
    results = await asyncio.gather(*tasks)
    steam_id_to_dump = b"".join(results)
    return BufferedInputFile(steam_id_to_dump, 'accounts_dump.txt')

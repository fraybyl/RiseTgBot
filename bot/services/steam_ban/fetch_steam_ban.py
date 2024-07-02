import asyncio
import aiohttp
from loguru import logger

from bot.core.loader import redis_db, config_json
from bot.types.AccountInfo import AccountInfo

lock = asyncio.Lock()


async def fetch_get_player_bans(
        session: aiohttp.ClientSession,
        url: str,
        semaphore: asyncio.Semaphore
) -> list[AccountInfo]:
    """
    Асинхронная функция для получения информации о банах игроков по API Steam и сохранения её в Redis.

    Аргументы:
    - session (aiohttp.ClientSession): Сессия aiohttp для выполнения запросов.
    - url (str): URL для запроса информации о банах игроков.
    - semaphore (asyncio.Semaphore): Семафор для ограничения числа параллельных запросов.

    Возвращает:
    - list[AccountInfo]: Список объектов AccountInfo, содержащих информацию о банах игроков.

    Исключения:
    - Возможны различные исключения при выполнении запросов или обработке данных.
    """
    async with semaphore:
        try:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                async with redis_db.pipeline() as pipe:
                    data = await response.json()
                    players = data.get('players', [])
                    accounts_info = list(map(AccountInfo.from_dict, players))
                    for account_info in accounts_info:
                        pipe.hset(f'data::{account_info.SteamId}', 'ban', account_info.to_json())
                    await pipe.execute()
            return accounts_info
        except Exception as e:
            logger.error(f"Ошибка фетча fetch_get_player_bans: {e}")
            return []


async def add_or_update_player_bans(
        steam_ids: list[int],
        is_update: bool = False,
        max_concurrent_requests: int = 2
) -> list[AccountInfo]:
    """
    Асинхронная функция для добавления или обновления информации о банах игроков в Redis.

    Аргументы:
    - steam_ids (list[int]): Список Steam ID игроков.
    - is_update (bool, optional): Флаг, указывающий, обновлять ли существующие записи. По умолчанию False.
    - max_concurrent_requests (int, optional): Максимальное число параллельных запросов. По умолчанию 2.

    Возвращает:
    - list[AccountInfo]: Список объектов AccountInfo, содержащих информацию о банах игроков.

    Исключения:
    - Возможны различные исключения при выполнении запросов или обработке данных.
    """
    async with lock:
        api_key = await config_json.get_config_value('steam_web_api_key')
        semaphore = asyncio.Semaphore(max_concurrent_requests)
        tasks = []

        async with aiohttp.ClientSession() as session:
            if not is_update:
                async with redis_db.pipeline() as pipe:
                    [pipe.hexists(f'data::{steam_id}', 'ban') for steam_id in steam_ids]
                    exists_results = await pipe.execute()

                steam_ids = [steam_id for steam_id, exists in zip(steam_ids, exists_results) if not exists]

            for i in range(0, len(steam_ids), 100):
                steam_ids_chunk = steam_ids[i:i + 100]
                if not steam_ids_chunk:
                    continue

                url = (
                    f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/'
                    f'?key={api_key}&steamids={",".join(map(str, steam_ids_chunk))}'
                )
                tasks.append(fetch_get_player_bans(session, url, semaphore))

            results = await asyncio.gather(*tasks, return_exceptions=True)
            results_account_info = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"ОШИБКА В ФЕТЧЕ ОБНОВЛЕНИЕ БАНОВ: {result}")
                elif isinstance(result, list):
                    results_account_info.extend(result)
            return results_account_info

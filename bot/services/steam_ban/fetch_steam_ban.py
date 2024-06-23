import asyncio
import itertools

import aiohttp
from orjson import orjson
from loguru import logger

from bot.core.loader import redis_db, config_json
from bot.types.AccountInfo import AccountInfo

lock = asyncio.Lock()


async def fetch_get_player_bans(
        session: aiohttp.ClientSession,
        url: str,
        semaphore: asyncio.Semaphore
) -> list[AccountInfo]:
    async with semaphore:
        try:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                players = data.get('players', [])
                return list(map(AccountInfo.from_dict, players))
        except Exception as e:
            logger.error(f"Ошибка фетча fetch_get players: {e}")
            return []


async def add_player_bans(
        steam_ids: list[int],
        max_concurrent_requests: int = 2
) -> list[AccountInfo]:
    async with lock:
        api_key = await config_json.get_config_value('steam_web_api_key')
        semaphore = asyncio.Semaphore(max_concurrent_requests)
        tasks = []

        async with aiohttp.ClientSession() as session:
            for i in range(0, len(steam_ids), 100):
                steam_ids_chunk = steam_ids[i:i + 100]
                url = (
                    f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/'
                    f'?key={api_key}&steamids={",".join(map(str, steam_ids_chunk))}'
                )
                tasks.append(fetch_get_player_bans(session, url, semaphore))

            results = await asyncio.gather(*tasks, return_exceptions=True)
            flat_results = list(itertools.chain.from_iterable(
                result for result in results if isinstance(result, list)
            ))
        return flat_results


async def set_player_bans(steam_ids: list[int], user_id: int) -> None:
    redis_key = f"telegram_user::{user_id}"
    results = await add_player_bans(steam_ids)

    current_data_json = await redis_db.hget(redis_key, 'ban_stat')
    current_data = orjson.loads(current_data_json) if current_data_json else []

    current_data.extend(results)

    await redis_db.hset(redis_key, 'ban_stat', orjson.dumps(current_data))


async def remove_player_bans(steam_ids: list[int], user_id: int):
    redis_key = f"telegram_user::{user_id}"
    steam_ids_set = set(steam_ids)

    ban_stat_bytes = await redis_db.hget(redis_key, 'ban_stat')

    if ban_stat_bytes is not None:
        ban_stat_json = orjson.loads(ban_stat_bytes)

        ban_stat_json = [
            ban_stat_dict for ban_stat_dict in ban_stat_json
            if int(ban_stat_dict['SteamId']) not in steam_ids_set
        ]

        await redis_db.hset(redis_key, 'ban_stat', orjson.dumps(ban_stat_json))
    return

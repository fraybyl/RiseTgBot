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
) -> bool:
    async with semaphore:
        try:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                async with redis_db.pipeline() as pipe:
                    data = await response.json()
                    players = data.get('players', [])
                    accounts_info = list(map(AccountInfo.from_dict, players))
                    for account_info in accounts_info:
                        pipe.hset(f'data::{account_info.steam_id}', 'ban', account_info.to_dict())
                    await pipe.execute()
            return True
        except Exception as e:
            logger.error(f"Ошибка фетча fetch_get players: {e}")
            return False


async def add_player_bans(
        steam_ids: list[int],
        max_concurrent_requests: int = 2
) -> None:
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


async def main() -> None:
    await add_player_bans([
        76561198037717949,
        76561198965030463,
        76561198997994621,
        76561198986923662,
        76561198069678468,
        76561198855186239,
        76561198007241107
    ])

if __name__ == '__main__':
    asyncio.run(main())
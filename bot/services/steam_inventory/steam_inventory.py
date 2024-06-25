import asyncio

from loguru import logger

from bot.services.steam_inventory.inventory_process import InventoryProcess
from bot.types.InventoryAsset import InventoryAsset
from bot.types.InventoryDescription import InventoryDescription
from redis.asyncio import Redis
from aiolimiter import AsyncLimiter
import ua_generator
import aiohttp
import orjson


class SteamInventory:
    def __init__(
            self,
            proxies: list[str],
            redis_db: Redis,
            rate_period: float = 5.0,
            blacklist_ttl: int = 28800
    ) -> None:
        self.sessions: dict[str, dict] = {}
        self.proxies = proxies
        self.redis_db = redis_db
        self.blacklist_ttl = blacklist_ttl
        self.rate_period = rate_period

    async def __aenter__(self):
        for proxy in self.proxies:
            headers = ua_generator.generate(browser=('chrome', 'firefox')).headers.get()
            session = aiohttp.ClientSession(headers=headers)
            limiter = AsyncLimiter(max_rate=1.0, time_period=self.rate_period)
            self.sessions[proxy] = {'session': session, 'limiter': limiter}
        return self

    async def __aexit__(self, exc_type, exc, tb):
        for proxy, data in self.sessions.items():
            await data['session'].close()

    async def get_inventory(
            self,
            steam_id: int,
            proxy: str
    ) -> bool:
        inventory_url = f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=english&count=1999"
        session_data = self.sessions.get(proxy)

        if not session_data:
            return False

        limiter = self.sessions[proxy]['limiter']
        session = self.sessions[proxy]['session']

        async with limiter:
            async with session.get(inventory_url, proxy=proxy) as response:
                print(f'fetch with {proxy} {steam_id}')

                if response.status == 200:
                    data = await response.json(encoding='utf-8', loads=orjson.loads)
                    assets_data = data.get('assets', [])
                    descriptions_data = data.get('descriptions', [])

                    assets = InventoryAsset.from_list(assets_data)
                    descriptions = InventoryDescription.from_list(descriptions_data)

                    inventory_process = InventoryProcess(self.redis_db)
                    steam_id_inventory = await inventory_process.parse_inventory_data(assets, descriptions)
                    if steam_id_inventory:
                        await self.redis_db.hset(f'data::{steam_id}', 'inventory', steam_id_inventory.to_json())
                        return True

                    return False

                elif response.status in {401, 403}:
                    await self.redis_db.setex(f"blacklist::{steam_id}", self.blacklist_ttl, "")
                    return False

                elif response.status == 429:
                    logger.error(f'429 ошибка при фетче инвентаря с прокси {proxy}')
                    await session.close()
                    self.proxies.remove(proxy)
                    self.sessions.pop(proxy, None)
                    return False

                return False

    async def process_inventories(
            self,
            steam_ids: list[int],
            is_update=False
    ) -> None:
        while steam_ids:
            if not self.proxies:
                logger.error(f'Закончились прокси, осталось {len(steam_ids)} аккаунтов для проверки. АЛАРМ')
                break

            tasks = []
            for proxy in self.proxies[:len(steam_ids)]:
                steam_id = steam_ids.pop(0)

                if not is_update and await self.redis_db.hexists(f'data::{steam_id}', 'inventory'):
                    continue

                if await self.redis_db.exists(f'blacklist::{steam_id}'):
                    continue

                task = self.get_inventory(steam_id, proxy)
                tasks.append(task)

            await asyncio.gather(*tasks)

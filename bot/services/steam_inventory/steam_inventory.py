import asyncio

import aiohttp
import orjson
import ua_generator
from aiolimiter import AsyncLimiter
from loguru import logger
from redis.asyncio import Redis

from bot.services.steam_inventory.inventory_process import InventoryProcess
from bot.types.InventoryAsset import InventoryAsset
from bot.types.InventoryDescription import InventoryDescription


class SteamInventory:
    """
    Класс для работы с инвентарем Steam через API и сохранения данных в Redis.

    Атрибуты:
    - proxies (list[str]): Список прокси-серверов для отправки запросов.
    - redis_db (Redis): Асинхронный клиент Redis для выполнения операций с базой данных.
    - rate_period (float): Период ограничения скорости запросов к API Steam. По умолчанию 4.0.
    - blacklist_ttl (int): Время жизни записи в Redis о наличии в черном списке. По умолчанию 28800 секунд.
    - max_retries (int): Максимальное количество повторных попыток запроса при ошибках. По умолчанию 3.

    Методы:
    - __aenter__(self):
      Асинхронный контекстный менеджер для инициализации сессий и лимитеров для каждого прокси.

    - __aexit__(self, exc_type, exc, tb):
      Асинхронный метод для закрытия сессий при завершении работы с контекстным менеджером.

    - get_inventory(self, steam_id: int, proxy: str, retries: int = 0) -> bool:
      Асинхронно получает данные инвентаря указанного пользователя Steam и сохраняет их в Redis.

    - process_inventories(self, steam_ids: list[int], is_update=False) -> None:
      Асинхронно обрабатывает инвентари пользователей Steam из списка steam_ids.
    """

    def __init__(
            self,
            proxies: list[str],
            redis_db: Redis,
            rate_period: float = 4.0,
            blacklist_ttl: int = 28800,
            max_retries: int = 3,
    ) -> None:
        """
        Инициализирует объект класса SteamInventory.

        Аргументы:
        - proxies (list[str]): Список прокси-серверов для отправки запросов.
        - redis_db (Redis): Асинхронный клиент Redis для выполнения операций с базой данных.
        - rate_period (float, optional): Период ограничения скорости запросов к API Steam. По умолчанию 4.0.
        - blacklist_ttl (int, optional): Время жизни записи в Redis о наличии в черном списке. По умолчанию 28800 секунд.
        - max_retries (int, optional): Максимальное количество повторных попыток запроса при ошибках. По умолчанию 3.
        """
        self.sessions: dict[str, dict] = {}
        self.proxies = proxies
        self.redis_db = redis_db
        self.blacklist_ttl = blacklist_ttl
        self.rate_period = rate_period
        self.retry_queue = asyncio.Queue()
        self.max_retries = max_retries

    async def __aenter__(self):
        """
        Асинхронный контекстный менеджер для инициализации сессий и лимитеров для каждого прокси.
        """
        for proxy in self.proxies:
            ua = ua_generator.generate(browser=('chrome', 'firefox')).headers.get()
            additional = {'Connection': 'close', 'Accept-Encoding': 'gzip, deflate, br, zstd'}
            headers = ua | additional
            session = aiohttp.ClientSession(headers=headers)
            limiter = AsyncLimiter(max_rate=1.0, time_period=self.rate_period)
            self.sessions[proxy] = {'session': session, 'limiter': limiter}
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """
        Асинхронный метод для закрытия сессий при завершении работы с контекстным менеджером.
        """
        for proxy, data in self.sessions.items():
            await data['session'].close()

    async def get_inventory(
            self,
            steam_id: int,
            proxy: str,
            retries: int = 0
    ) -> bool:
        """
        Асинхронно получает данные инвентаря указанного пользователя Steam и сохраняет их в Redis.

        Аргументы:
        - steam_id (int): Steam ID пользователя.
        - proxy (str): Прокси-сервер для отправки запроса.
        - retries (int, optional): Количество повторных попыток запроса при ошибках. По умолчанию 0.

        Возвращает:
        - bool: True, если данные инвентаря успешно получены и сохранены, иначе False.
        """
        inventory_url = f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=english&count=2000"
        session_data = self.sessions.get(proxy)

        if not session_data:
            return False

        limiter = self.sessions[proxy]['limiter']
        session = self.sessions[proxy]['session']

        async with limiter:
            async with session.get(inventory_url, proxy=proxy) as response:
                logger.debug(f'Fetch with {proxy} {steam_id}')

                if response.status == 200:
                    data = await response.json(encoding='utf-8', loads=orjson.loads)
                    assets_data = data.get('assets', [])
                    descriptions_data = data.get('descriptions', [])

                    assets = InventoryAsset.from_list(assets_data)
                    descriptions = InventoryDescription.from_list(descriptions_data)

                    inventory_process = InventoryProcess()
                    steam_id_inventory = await inventory_process.parse_inventory_data(assets, descriptions)
                    if steam_id_inventory:
                        await self.redis_db.hset(
                            f'data::{steam_id}',
                            'inventory',
                            orjson.dumps(steam_id_inventory).decode('utf-8')
                        )
                        return True

                    return False

                elif response.status in {401, 403}:
                    await self.redis_db.setex(f"blacklist::{steam_id}", self.blacklist_ttl, "")
                    return False

                elif response.status == 429:
                    logger.error(f'429 ошибка при фетче инвентаря с прокси {proxy}')
                    if retries < self.max_retries:
                        await self.retry_queue.put((steam_id, retries + 1))
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
        """
        Асинхронно обрабатывает инвентари пользователей Steam из списка steam_ids.

        Аргументы:
        - steam_ids (list[int]): Список Steam ID пользователей.
        - is_update (bool, optional): Флаг, указывающий на необходимость обновления инвентаря. По умолчанию False.
        """
        for steam_id in steam_ids:
            await self.retry_queue.put((steam_id, 0))

        while not self.retry_queue.empty():
            if not self.proxies:
                logger.error(f'Закончились прокси, осталось {self.retry_queue.qsize()} аккаунтов для проверки. АЛАРМ')
                break

            tasks = []
            while len(tasks) < len(self.proxies):
                if self.retry_queue.empty():
                    break

                steam_id, retries = await self.retry_queue.get()

                if not is_update and await self.redis_db.hexists(f'data::{steam_id}', 'inventory'):
                    continue

                if await self.redis_db.exists(f'blacklist::{steam_id}'):
                    continue

                proxy = self.proxies[len(tasks) % len(self.proxies)]
                task = self.get_inventory(steam_id, proxy, retries)
                tasks.append(task)

            await asyncio.gather(*tasks)

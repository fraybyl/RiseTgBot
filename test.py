import asyncio
import time

import redis
import redis.asyncio as Redis
import ua_generator
from aiogram.client.session import aiohttp
from yarl import URL
from aiolimiter import AsyncLimiter
from loguru import logger
import urllib.parse

from bot.core.loader import redis_db
from bot.types.Item import Item


class SteamItemFetch:
    def __init__(
            self,
            proxies: list[str],
            redis: Redis,
            rate_period: float = 0.25,
            currency: int = 5,
            appid: int = 730
    ) -> None:
        self.sessions: dict[str, aiohttp.ClientSession] = {}
        self.proxies = proxies
        self.redis = redis
        self.currency = currency
        self.rate_period = rate_period
        self.appid = appid

    async def __aenter__(self):
        for proxy in self.proxies:
            headers = {'Accept-Encoding': 'br', 'Connection': 'close'}
            session = aiohttp.ClientSession(headers=headers)
            self.sessions[proxy] = session
        return self

    async def __aexit__(self, exc_type, exc, tb):
        for proxy, session in self.sessions.items():
            await session.close()
        self.sessions.clear()

    def convert_price(self, price: str) -> float:
        if self.currency == 5:
            price = price.replace(' pуб.', '').replace(',', '.')
            return float(price)
        elif self.currency == 1:
            price = price.replace('$', '')
            return float(price)
        else:
            return float(price)

    async def __fetch_item_price(
            self,
            item_hash_name: str,
            proxy: str
    ) -> Item | None:
        item_url = URL(
            f"https://steamcommunity.com/market/priceoverview?appid={self.appid}&currency={self.currency}&market_hash_name={self.convert_hash_to_url(item_hash_name)}",
            encoded=True)
        session = self.sessions[proxy]
        async with session.get(url=item_url, proxy=proxy) as response:
            if response.status == 200:
                logger.info(f'ФЕТЧ ИТЕМА {response.url} - {item_hash_name}')
                data = await response.json()
                price = data.get('lowest_price') or data.get('median_price') or None
                sell_count = data.get('volume', 0)
                if price:
                    price = self.convert_price(price)
                    item = Item(f'market::{item_hash_name}', price, sell_count)
                    await self.redis.hset(item.item_name, mapping={
                        'price': item.price,
                        'sell_count': item.sell_count,
                    })
                    return item
            else:
                logger.error(f'Ошибка фетча предмета {response.status} - {item_hash_name}')
                return None

    @staticmethod
    def convert_hash_to_url(hash: str) -> str:
        hash_first = hash.replace(' ', '%20')
        hash_secod = hash_first.replace('&', '%26')
        hash_result = hash_secod.replace('|', '%7C')

        return hash_result

    async def get_hash_names_prices(
            self,
            hash_names: list[str],
            is_update: bool = False,
    ) -> None:
        while hash_names:
            if not self.proxies:
                logger.error(f'Закончились прокси, осталось {len(hash_names)} аккаунтов для проверки. АЛАРМ')
                break

            tasks = []

            for proxy in self.proxies[:len(hash_names)]:
                hash_name = hash_names.pop(0)

                if not is_update and await self.redis.exists(f'market::{hash_name}'):
                    continue

                task = self.__fetch_item_price(hash_name, proxy)
                tasks.append(task)

            await asyncio.gather(*tasks)


async def main():
    steam = SteamItemFetch(
        ["http://teiqogrk-rotate:md5yfndvjcze@p.webshare.io:80",
         'http://teiqogrk-rotate:md5yfndvjcze@p.webshare.io:1080'],
        redis_db
    )
    with open('sdfds.txt', 'r', encoding='utf-8') as file:
        data = file.read()

    # Загрузка данных как словаря
    data_dict = eval(data)

    # Извлечение ключей и формирование списка строк
    result = list(data_dict.keys())
    start = time.time()
    async with steam:
        await steam.get_hash_names_prices(result)
    print(time.time() - start)
    await redis_db.connection_pool.aclose()


if __name__ == '__main__':
    asyncio.run(main())

import asyncio
import urllib.parse
from itertools import cycle

import aiohttp
import redis.asyncio as Redis

from bot.types.Item import Item
from bot.core.loader import redis_db as rediska


class SteamItemFetch:
    def __init__(self, proxies: list[str], redis_db: Redis, currency: int):
        self.proxies = proxies
        self.redis_db = redis_db
        self.currency = currency
        self.headers = {'Accept-Encoding': 'br'}
        self.sessions: dict[str, dict] = {}

    async def __aenter__(self):
        for proxy in self.proxies:
            session = aiohttp.ClientSession(headers=self.headers)
            self.sessions[proxy] = {'session': session}
        return self

    async def __aexit__(self, exc_type, exc, tb):
        for proxy, data in self.sessions.items():
            await data['session'].close()

    async def fetch_market_hash_name(self, hash_name: str, session: aiohttp.ClientSession):
        hash_name_url = "https://steamcommunity.com/market/priceoverview"
        params = {
            'currency': self.currency,
            'appid': 730,
            'market_hash_name': urllib.parse.quote(hash_name),
        }

        async with session.get(url=hash_name_url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                price = data.get('lowest_price') or data.get('median_price')
                sell_count = data.get('volume', 0)
                item = Item(hash_name, price, sell_count)
                await self.redis_db.set(item.item_name, **item.__dict__)
                return item
            else:
                print(response.status)
                return None

    async def get_market_hash_names(self, hash_names: list[str]):
        sessions = cycle(self.proxies)
        tasks = []
        for hash_name in hash_names:
            session = next(sessions)
            tasks.append(self.fetch_market_hash_name(hash_name, self.sessions[session]['session']))

        results = await asyncio.gather(*tasks)
        return results


async def main():
    proxies = [
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334",
        "https://u02b203ad560d05c5-zone-custom:u02b203ad560d05c5@43.152.115.133:2334"
    ]
    steam = SteamItemFetch(proxies, rediska, 5)
    with open('sdfds.txt', 'r', encoding='UTF-8') as file:
        hash_names = file.read().strip()
    print(hash_names)
    # async with steam as steam:
    #     print(steam.get_market_hash_names())

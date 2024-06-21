import asyncio

import aiohttp
import ua_generator
from aiolimiter import AsyncLimiter
from orjson import orjson
from loguru import logger
import urllib.parse

from bot.core.loader import redis_db


class SteamParser:
    def __init__(self, proxies: list[str], currency: int = 5, rate_limit_seconds: int = 5):
        self.headers = self.generate_headers()
        self.currency = currency
        self.rate_limit_seconds = rate_limit_seconds
        self.proxy_limiters = {}
        self.proxies = proxies

    @staticmethod
    def generate_headers():
        return ua_generator.generate(browser=('chrome', 'edge', 'firefox')).headers.get()

    async def __fetch_inventory_data(self, steam_id: int, proxy: str) -> dict | None:
        inventory_url = f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=english&count=1999"
        if proxy not in self.proxy_limiters:
            self.proxy_limiters[proxy] = AsyncLimiter(max_rate=1, time_period=4)

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with self.proxy_limiters[proxy]:
                async with session.get(inventory_url, proxy=proxy) as response:
                    logger.info('fetch %s with proxy: %s' % (steam_id, proxy))
                    if response.status == 200:
                        return await response.json()
                    elif response.status in {403, 401}:
                        await redis_db.sadd("blacklist", steam_id)
                    logger.error("Failed to fetch inventory data with status: %s" % response.status)
                    return None

    async def __fetch_hash_name_data(self, market_hash_name: str, proxy: str) -> dict | None:
        price_url = f'https://steamcommunity.com/market/priceoverview/?country=RU&currency=5&appid=730&market_hash_name={market_hash_name}'
        if proxy not in self.proxy_limiters:
            self.proxy_limiters[proxy] = AsyncLimiter(max_rate=1, time_period=self.rate_limit_seconds)

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with self.proxy_limiters[proxy]:
                async with session.get(price_url, proxy=proxy) as response:
                    logger.info('fetch %s with proxy: %s' % (market_hash_name, proxy))
                    if response.status == 200:
                        return await response.json()

                    logger.error("Failed to fetch hash name with status: %s", response.status)
                    return None

    async def __parse_hash_name_data(self, market_hash_name: str, proxy: str) -> float | None:
        if await redis_db.sismember('blacklist', market_hash_name):
            return None

        cache_hash = await redis_db.get(f'steam_market::{market_hash_name}')

        if cache_hash:
            cached_data = orjson.loads(cache_hash)
            return cached_data['price']

        encoded_market_hash_name = urllib.parse.quote(market_hash_name)

        data = await self.__fetch_hash_name_data(encoded_market_hash_name, proxy)
        if data:
            price = data.get('lowest_price') or data.get('median_price') or None
            if price:
                try:
                    price_float = float(price.split(' ')[0].replace(',', '.'))
                    return price_float
                except ValueError:
                    logger.error('Failed to parse price for item: %s', market_hash_name)
                    return None

        return None

    async def __parse_inventory_data(self, steamid: int, proxy: str) -> list[tuple[str, int]]:
        cache_key = f"inventory::{steamid}"
        cached_data = await redis_db.get(cache_key)
        if cached_data:
            return orjson.loads(cached_data)

        inventory_data = await self.__fetch_inventory_data(steamid, proxy)

        if not inventory_data:
            logger.error("No inventory data provided.")
            return []

        item_counts = {}
        item_details = {}

        assets = inventory_data.get('assets', [])
        descriptions = inventory_data.get('descriptions', [])

        for item in assets:
            unique_id = f"{item['classid']}_{item['instanceid']}"
            item_counts[unique_id] = item_counts.get(unique_id, 0) + 1

        for desc in descriptions:
            if desc.get('marketable', 0) == 1:
                unique_id = f"{desc['classid']}_{desc['instanceid']}"
                item_details[unique_id] = desc['market_hash_name']

        item_names_with_count = []
        for uid, count in item_counts.items():
            if uid in item_details:
                item_names_with_count.append((item_details[uid], count))

        if not item_names_with_count:
            logger.info("No marketable items found.")

        return item_names_with_count

    async def process_inventory_price(self, steam_id: int, proxies: list[str]) -> tuple[
        int, list[tuple[str, int, float]]]:
        if await redis_db.sismember('blacklist', steam_id):
            return steam_id, []

        inventory_data = await self.__parse_inventory_data(steam_id, proxies[0])
        tasks = []
        for i, (item, count) in enumerate(inventory_data):
            proxy = proxies[i % len(proxies)]
            tasks.append(self.__parse_hash_name_data(item, proxy))

        results = await asyncio.gather(*tasks)

        combined_data = []

        for (item, count), price in zip(inventory_data, results):
            if price is None:
                await redis_db.sadd("blacklist", item)
                continue
            try:
                item_data = {
                    'price': price,
                    'sell_count': 0
                }

                await redis_db.set(f'steam_market::{item}', orjson.dumps(item_data))
                total_price = round(price * count, 2)
                combined_data.append((item, count, total_price))
            except ValueError:
                logger.error('Failed to convert price to number: %s', price)
                combined_data.append((item, count, 0.0))

        return steam_id, combined_data

    @staticmethod
    async def __is_in_cache(steam_id: int):
        return await redis_db.exists(f'inventory::{steam_id}')

    async def process_inventories(self, steam_ids: list[int]) -> list[tuple[int, list[tuple[str, int, float]]]]:
        results = []
        num_proxies = len(self.proxies)
        proxy_index = 0

        steam_ids = [steam_id for steam_id in steam_ids if not await self.__is_in_cache(steam_id)]

        while steam_ids:
            tasks = []
            if len(steam_ids) > num_proxies:
                for steam_id in steam_ids[:num_proxies]:
                    proxies_chunk = [self.proxies[proxy_index % num_proxies]]
                    proxy_index += 1
                    tasks.append(self.process_inventory_price(steam_id, proxies_chunk))
                steam_ids = steam_ids[num_proxies:]
            else:
                num_proxies_per_task = num_proxies // len(steam_ids)
                remainder = num_proxies % len(steam_ids)

                start_index = 0
                for i, steam_id in enumerate(steam_ids):
                    count = num_proxies_per_task + (1 if i < remainder else 0)
                    proxies_chunk = self.proxies[start_index:start_index + count]
                    start_index += count
                    tasks.append(self.process_inventory_price(steam_id, proxies_chunk))
                steam_ids.clear()

            results_batch = await asyncio.gather(*tasks)
            for steam_id, result in results_batch:
                if result:
                    await redis_db.set(f"inventory::{steam_id}", orjson.dumps(result))
            results.extend(results_batch)

        return results

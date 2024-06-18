import orjson
import ua_generator
import aiohttp
import logging
import urllib.parse
from loader import redis_db
from aiolimiter import AsyncLimiter
import asyncio

class SteamParser:
    def __init__(self, proxies: dict[str], currency: int = 5, rate_limit_seconds: int = 5):
        self.headers = self.generate_headers()
        self.currency = currency
        self.rate_limit_seconds = rate_limit_seconds
        self.proxy_limiters = {}
        self.proxies = proxies
        
    def generate_headers(self):
        return ua_generator.generate(browser=('chrome', 'edge', 'firefox')).headers.get()
    
    async def __fetch_inventory_data(self, steam_id: int, proxy: str) -> dict:
        inventory_url = f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=english&count=1999"
        if proxy not in self.proxy_limiters:
            self.proxy_limiters[proxy] = AsyncLimiter(max_rate=1, time_period=4) # яебал тут лимит  1 запрос в 4 сек ставить
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with self.proxy_limiters[proxy]:
                async with session.get(inventory_url, proxy=proxy) as response:
                    logging.info('fetch %s with proxy: %s' % (steam_id, proxy))
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 403 or response.status == 401:
                        await redis_db.sadd("blacklist", steam_id)
                    logging.error("Failed to fetch inventory data with status: %s", response.status)
                    return None

    async def __fetch_hash_name_data(self, market_hash_name: str, proxy: str) -> dict:
        price_url = f'https://steamcommunity.com/market/priceoverview/?country=RU&currency=5&appid=730&market_hash_name={market_hash_name}'
        if proxy not in self.proxy_limiters:
            self.proxy_limiters[proxy] = AsyncLimiter(max_rate=1, time_period=self.rate_limit_seconds)
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with self.proxy_limiters[proxy]:
                async with session.get(price_url, proxy=proxy) as response:
                    logging.info('fetch %s with proxy: %s' % (market_hash_name, proxy))
                    if response.status == 200:
                        return await response.json()
                    
                    logging.error("Failed to fetch hash name with status: %s", response.status)
                    return None
                
    async def __parse_hash_name_data(self, market_hash_name: str, proxy: str) -> float:
        if await redis_db.sismember('blacklist', market_hash_name):
            return None
        
        cache_hash = await redis_db.get(f'steam_market::{market_hash_name}')
        
        if(cache_hash):
            return cache_hash
        
        encoded_market_hash_name = urllib.parse.quote(market_hash_name)
        
        data = await self.__fetch_hash_name_data(encoded_market_hash_name, proxy)
        if data:
            price = data.get('lowest_price') or data.get('median_price') or None
            if price:
                try:
                    price_float = float(price.split(' ')[0].replace(',', '.'))
                    item_data = {
                            'price': price_float,
                            'sell_count': 0
                    }
                    
                    await redis_db.set(f'steam_market::{market_hash_name}', orjson.dumps(item_data))
                    return orjson.dumps(item_data)
                except ValueError:
                    logging.error('Не преобразовало епта: %s', market_hash_name)
                    return None

        return None

    async def __parse_inventory_data(self, steamid: int, proxy: str) -> list[tuple[str, int]]:
        cache_key = f"inventory::{steamid}"
        cached_data = await redis_db.get(cache_key)
        if cached_data:
            return orjson.loads(cached_data)  # Unserialize cached data
        
        inventory_data = await self.__fetch_inventory_data(steamid, proxy)
        
        if not inventory_data:
            logging.error("No inventory data provided.")
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
            logging.info("No marketable items found.")
            
        await redis_db.set(cache_key, orjson.dumps(item_names_with_count))

        return item_names_with_count
    
    async def process_inventory_price(self, steam_id: int, proxies: list[str]) -> tuple[str, int, float]:
        """Смотрит цену 1 инвентаря

        Args:
            steam_id (int): стим айди че тупень
            proxies (list[str]): лист прокси

        Returns:
            list[tuple[str, int, float]]: вернет название, количество, цену
        """
        
        if await redis_db.sismember('blacklist', steam_id):
            return []
        
        inventory_data = await self.__parse_inventory_data(steam_id, proxies[0])
        tasks = []
        for i, (item, count) in enumerate(inventory_data):
            proxy = proxies[i % len(proxies)]
            tasks.append(self.__parse_hash_name_data(item, proxy))
            
        results = await asyncio.gather(*tasks)
        
        combined_data = []
        
        for (item, count), price_str in zip(inventory_data, results):
            if(price_str is None):
                await redis_db.sadd("blacklist", item)
                continue
            try:
                price_str = price_str.decode('utf-8')
                price_dict = orjson.loads(price_str)
                price = round(price_dict.get('price'), 2)
                total_price = float(price) * count
                combined_data.append((item, count, total_price))
            except ValueError:
                logging.error('Не удалось преобразовать цену в число: %s', price)
                combined_data.append((item, count, 0.0))  
        
        return combined_data
                
    async def process_inventories(self, steam_ids: list[int]) -> list[tuple[str, int, float]]:
        """
        Смотрит цену всех инвентарей.
        Args:
            steam_ids (list[int]): лист стим айди

        Returns:
            list[tuple[str, int, float]]: вернет лист с кортежом с названием, количеством, ценой.
        """
        results = []
        num_proxies = len(self.proxies)
        num_steam_ids = len(steam_ids)
        proxy_index = 0

        while steam_ids:
            tasks = []
            if num_steam_ids > num_proxies:
                # Если steam_ids больше чем прокси, распределяем прокси циклически
                for steam_id in steam_ids[:num_proxies]:
                    proxies_chunk = [self.proxies[proxy_index % num_proxies]]
                    proxy_index += 1
                    tasks.append(self.process_inventory_price(steam_id, proxies_chunk))
                steam_ids = steam_ids[num_proxies:]
            else:
                # Если прокси больше или равно количеству steam_ids, распределяем прокси равномерно
                num_proxies_per_task = num_proxies // num_steam_ids
                remainder = num_proxies % num_steam_ids

                start_index = 0
                for i, steam_id in enumerate(steam_ids):
                    count = num_proxies_per_task + (1 if i < remainder else 0)
                    proxies_chunk = self.proxies[start_index:start_index + count]
                    start_index += count
                    tasks.append(self.process_inventory_price(steam_id, proxies_chunk))
                steam_ids.clear()

            # Выполнение задач текущей порции
            results.extend(await asyncio.gather(*tasks))
            num_steam_ids = len(steam_ids)

        return results
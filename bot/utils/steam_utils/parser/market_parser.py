import datetime
import orjson
import ua_generator
import aiohttp
from loader import redis_db, logging
import asyncio

class SteamMarketParser:
    def __init__(self, proxies: dict[str]) -> None:
        """
        Инициализация SteamMaketParser.
        :app_id: ID приложения.
        """
        self.offset = 0
        self.url = f"https://steamcommunity.com/market/search/render/?query=appid%3A730"
        self.proxies = proxies
        self.headers = self.generate_headers()

    def generate_headers(self):
        return ua_generator.generate(browser=('chrome', 'edge', 'firefox')).headers.get()
    
    async def fetch_page(self, session, proxy: str, start: int, page_number: int, batch_size: int) -> list[dict[str, str]]:
        """
        Получает страницу данных с использованием указанного прокси.

        :session: Сессия aiohttp.
        :proxy: Прокси для использования.
        :start: Начальный индекс.
        :page_number: Номер страницы.
        :batch_size: Количество элементов на странице.
        :return: Список словарей с данными.
        """
        query = {
            'start': start,
            'count': batch_size,
            'norender': 1
        }
        
        try:
            async with session.get(self.url, params=query, proxy=proxy, timeout=5) as response:
                if response.status == 429:
                    logging.warning(f"Got 429 Too Many Requests error for proxy: {proxy}. Sleeping for 180 seconds.")
                    await asyncio.sleep(180)
                    return []

                response.raise_for_status()
                response_json = await response.json()
                items = response_json.get('results', [])

                result = []
                for item in items:
                    if 'sell_price_text' in item:
                        item_name = item.get('hash_name')
                        price = item.get('sell_price_text')
                        sell_count = item.get('sell_listings')

                        item_data = {
                            'name': item_name,
                            'price': price,
                            'sell_count': sell_count
                        }

                        result.append(item_data)
                        await redis_db.set(f'steam_market::{item_name}', str(item_data))

                return result

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logging.error(f"Failed to fetch page {page_number} due to error: {e}")
            asyncio.create_task(self.retry_fetch_page(session, proxy, start, page_number, batch_size))
            return []

    async def retry_fetch_page(self, session, proxy: str, start: int, page_number: int, batch_size: int):
        await asyncio.sleep(180)  # 3 minutes
        await self.fetch_page(session, proxy, start, page_number, batch_size)

    async def page_iterator(self, start_page: int, end_page: int, proxies: list[str]) -> list[dict[str, str]]:
        """
        Итератор по страницам с использованием списка прокси.

        :param start_page: Начальная страница.
        :param end_page: Конечная страница.
        :param proxies: Список прокси.
        :return: Список данных.
        """
        result = []
        tasks = []

        async with aiohttp.ClientSession(headers=self.headers) as session:
            for i in range(start_page, end_page):
                proxy = proxies[i % len(proxies)]
                start = i * 100
                tasks.append(self.fetch_page(session, proxy, start, i, 100))
            
            pages_data = await asyncio.gather(*tasks)

        for page_data in pages_data:
            result.extend(page_data)

        return result

    async def fetch_all_pages(self) -> list[dict[str, str]]:
        """
        Получает данные со всех страниц, используя заданный список прокси.

        :param proxies: Список прокси.
        :return: Список данных.
        """
        results = []
        start_page = 0

        while True:
            batch_results = await self.page_iterator(start_page, start_page + len(self.proxies), self.proxies)
            results.extend(batch_results)

            # Check if the number of items retrieved is less than expected
            if len(batch_results) < 100 * len(self.proxies):
                logging.info(f"Stopping fetching as less than {100 * len(self.proxies)} items were received.")
                break

            start_page += len(self.proxies)
            await asyncio.sleep(5)

        return results

    async def get_price_rub(self, proxy: str) -> dict[str, str]:
        """
        Получает цену в рублях с использованием случайного прокси.

        :return: Словарь с ценой в рублях.
        """
        price_url = "https://api.steam-currency.ru/currency/USD:RUB"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(price_url, timeout=5) as response:
                response.raise_for_status()
                response_json = await response.json()
                data = response_json.get('data', [])
                if not data:
                    return {}
                
                latest_item = max(data, key=lambda x: datetime.strptime(x["created_at"], "%Y-%m-%d %H:%M:%S"))
                rub_price = latest_item.get('close_price')

                return rub_price

    async def get_all_keys(self) -> list[str]:
        """
        Получает все ключи из кеша с использованием SCAN.

        :return: Список ключей.
        """
        keys = []
        cursor = b"0"
        while cursor:
            cursor, data = await redis_db.scan(cursor=cursor, match='steam_market::*')
            keys.extend(data)
        return keys

    async def get_total(self) -> float:
        """
        Рассчитывает общую сумму цен всех элементов.

        :return: Общая сумма.
        """
        total_price = 0.0
        all_keys = await self.get_all_keys()
        
        # Batch fetching cached data
        cached_data_list = await asyncio.gather(*[redis_db.get(key) for key in all_keys])
        
        for cached_data in cached_data_list:
            if cached_data is not None:
                cached_data = orjson.loads(cached_data)
                cached_price = cached_data.get("price")
                cached_count = cached_data.get("sell_count")

                if cached_price is not None and cached_count is not None:
                    cleaned_price = float(cached_price.replace('$', '').replace(',', ''))
                    total_price += cleaned_price * int(cached_count)

        return total_price
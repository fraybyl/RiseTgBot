import aiohttp
from bs4 import BeautifulSoup
import re
from loader import logging, redis_cache, configJson

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            logging.info("запрос")
            if response.status != 200:
                logging.error(f"Запрос не удался, статус код: {response.status}")
                return None
            return await response.text()

async def parse(html):
    soup = BeautifulSoup(html, 'html.parser')

    divs = soup.find_all('div', class_='row')

    for div in divs:
        h2 = div.find('h2')
        if h2 and 'Средняя стоимость дропа:' in h2.text:
            drop_cost = h2.get_text(strip=True)
            cost_value = re.search(r'\d+,\d+', drop_cost)
            if cost_value:
                return float(cost_value.group().replace(',', '.'))
            else:
                logging.error("Не удалось извлечь числовое значение")
                return None
    logging.error("Не удалось найти элемент с средней стоимостью дропа")
    return None

async def get_avg_drop():
    avg_drop = await redis_cache.get("avg_drop")
    if avg_drop:
        return avg_drop.decode('utf-8')
    
    url = 'https://21level.ru/ru'
    html = await fetch(url)
    TTL = configJson.get_config_value('avg_drop_ttl')
    if html:
        cost_value = await parse(html)
        if cost_value:
            await redis_cache.setex("avg_drop", TTL, cost_value)
            return cost_value
    return 0.0
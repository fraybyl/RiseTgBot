import re

import aiohttp
from bs4 import BeautifulSoup
from loguru import logger

from bot.decorators.dec_cache import cached


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            logger.info("запрос на обновление price_drop")
            if response.status != 200:
                logger.error(f"Запрос не удался, статус код: {response.status}")
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
                logger.error("Не удалось извлечь числовое значение")
                return None
    logger.error("Не удалось найти элемент с средней стоимостью дропа")
    return None


@cached(ttl=300)
async def get_avg_drop():
    url = 'https://21level.ru/ru'
    html = await fetch(url)
    if html:
        cost_value = await parse(html)
        if cost_value:
            return cost_value
    return 0.0

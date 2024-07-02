import re
import aiohttp
from bs4 import BeautifulSoup
from loguru import logger
from datetime import datetime
import asyncio
import json
from bot.decorators.dec_cache import cached

async def fetch(url, currency: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            logger.info(f"запрос на обновление {currency}")
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
async def get_avg_drop() -> float:
    url = 'https://21level.ru/ru'
    currency = 'Средний дроп'
    html = await fetch(url,currency)
    if html:
        cost_value = await parse(html)
        if cost_value:
            return cost_value
    return 0.0

@cached(ttl=300)
async def get_rub_rate(currency: int) -> float:
    if currency == 1:
        currency = "USD:RUB"
    elif currency == 2:
        currency = "RUB:UAH"

    url = f"https://api.steam-currency.ru/currency/{currency}"
    response = await fetch(url, currency) 
    data = json.loads(response)

    # Извлечение последнего значения
    price = data['data'][-1]['close_price']
    return float(price)
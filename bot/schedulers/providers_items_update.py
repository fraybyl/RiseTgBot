import os

import aiofiles
import orjson

from bot.core.loader import redis_db
from bot.services.steam_inventory.items_fetch import ItemsFetch


async def providers_items_update():
    """
    Здесь инициализируются провайдеры, которые
    нужно добавить в бд
    Обновляются курсы валют
    Обновляются все цены у provider
    """
    providers_to_fetch = {'steam': 'last_24h', 'csmoney': ''}
    pricing_providers = await _load_file('data/pricing_providers.json')
    items_fetcher = ItemsFetch(redis_db, pricing_providers)
    await items_fetcher.exchanges_rate()
    for key, value in providers_to_fetch.items():
        await items_fetcher.items_prices(key, value)


async def _load_file(path: str) -> dict:
    """Загрузка JSON файла и возврат его содержимого."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл {path} не найден.")
    async with aiofiles.open(path, 'r', encoding='utf-8') as file:
        content = await file.read()
        return orjson.loads(content)

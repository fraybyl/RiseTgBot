import asyncio
import os

import aiofiles
import aiohttp
from loguru import logger
from orjson import orjson
from redis.asyncio import Redis

from bot.types.Item import Item


class ItemsFetch:
    def __init__(self, redis_client: Redis, pricing_providers: dict):
        self.redis_db = redis_client
        self.pricing_providers = pricing_providers


    async def exchanges_rate(self):
        """Получение курсов обмена и сохранение в Redis."""
        url = 'https://prices.csgotrader.app/latest/exchange_rates.json'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    await self.redis_db.hset('exchangeRates', mapping=data)
                else:
                    logger.warning(f"Не удалось получить данные курсов обмена. Статус: {response.status}")

    async def items_prices(self, provider: str, mode: str = None):
        """Получение цен предметов и сохранение в Redis."""
        url = f'https://prices.csgotrader.app/latest/{provider}.json'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Не удалось получить данные от провайдера {provider}. Статус: {response.status}")
                    return
                pricing_mode = None
                data = await response.json()
                prices = {}
                provider_info = self.pricing_providers.get(provider)

                if not provider_info:
                    logger.warning(f"Провайдер {provider} не найден в списке провайдеров.")
                    return

                if provider in ['steam', 'bitskins', 'skinport']:
                    pricing_mode = mode
                    if provider == 'bitskins':
                        pricing_mode = self.pricing_providers['bitskins']['pricing_modes'].get(mode, mode)

                    for key in data:
                        prices[key] = {'price': data[key].get(pricing_mode)}

                elif provider in ['lootfarm', 'csgotm', 'csgoempire', 'swapgg', 'csgoexo', 'skinwallet']:
                    prices = {key: {'price': data[key]} for key in data}

                elif provider in ['csmoney', 'csgotrader', 'cstrade']:
                    for key in data:
                        prices[key] = {'price': data[key]['price'], 'doppler': data[key].get('doppler')}

                elif provider == 'buff163':
                    for key in data:
                        prices[key] = {
                            'price': data[key][mode].get('price'),
                            'doppler': data[key][mode].get('doppler')
                        }

                redis_key = f'prices::{provider}'
                if pricing_mode:
                    redis_key = f'prices::{provider}::{pricing_mode}'

                async with self.redis_db.pipeline() as pipe:
                    for item_name, details in prices.items():
                        item = Item.from_dict(item_name, details)
                        details_dict = {
                            'price': item.price,
                            'doppler_prices': item.doppler_prices
                        }
                        details_json = orjson.dumps(details_dict).decode('utf-8')
                        await pipe.hset(redis_key, item.item_name, details_json)
                    await pipe.execute()

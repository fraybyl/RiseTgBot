import asyncio
from collections import defaultdict

from orjson import orjson

from bot.types.Inventory import Inventory
from bot.types.InventoryAsset import InventoryAsset
from bot.types.InventoryDescription import InventoryDescription
from bot.types.Item import Item


class InventoryProcess:
    def __init__(self, redis_db):
        self.redis_db = redis_db

    async def parse_inventory_data(
            self,
            assets: list[InventoryAsset],
            descriptions: list[InventoryDescription]
    ) -> Inventory | None:
        """
        Парсинг данных инвентаря из assets и descriptions.

        Аргументы:
            assets: Список объектов инвентаря.
            descriptions: Список описаний инвентаря.

        Возвращает:
            Объект Inventory или None, если не найдено валидных предметов.
        """
        item_counts = self._collect_item_counts(assets)
        item_details = self._collect_item_details(descriptions)

        if not item_details or not item_counts:
            return None

        redis_data_dict = await self._fetch_redis_data(item_counts, item_details)
        item_names_with_count = self._build_items_with_count(item_counts, item_details, redis_data_dict)

        if item_names_with_count:
            return Inventory.from_data(item_names_with_count)
        return None

    @staticmethod
    def _collect_item_counts(
            assets: list[InventoryAsset]
    ) -> dict[str, int]:
        """
        Сбор количества предметов из assets.

        Аргументы:
            assets: Список объектов инвентаря.

        Возвращает:
            Словарь с уникальными идентификаторами предметов в качестве ключей и их количеством в качестве значений.
        """
        item_counts = defaultdict(int)
        for item in assets:
            unique_id = f"{item.class_id}_{item.instance_id}"
            item_counts[unique_id] += 1
        return item_counts

    @staticmethod
    def _collect_item_details(
            descriptions: list[InventoryDescription]
    ) -> dict[str, str]:
        """
        Сбор деталей предметов из descriptions.

        Аргументы:
            descriptions: Список описаний инвентаря.

        Возвращает:
            Словарь с уникальными идентификаторами предметов в качестве ключей и их market hash names в качестве значений.
        """
        item_details = {}
        for desc in descriptions:
            if desc.marketable:
                unique_id = f"{desc.class_id}_{desc.instance_id}"
                item_details[unique_id] = desc.market_hash_name
        return item_details

    async def _fetch_redis_data(
            self,
            item_counts: dict[str, int],
            item_details: dict[str, str]
    ) -> dict[str, dict]:
        """
        Получение данных из Redis для данных о предметах.

        Аргументы:
            item_counts: Словарь с уникальными идентификаторами предметов и их количеством.
            item_details: Словарь с уникальными идентификаторами предметов и их market hash names.

        Возвращает:
            Словарь с ключами Redis и декодированными данными.
        """
        redis_keys = [f'steam_market::{item_details[uid]}' for uid in item_counts if uid in item_details]
        redis_data = await asyncio.gather(*[self.redis_db.get(key) for key in redis_keys])
        return {key: orjson.loads(data.decode('utf-8')) for key, data in zip(redis_keys, redis_data)}

    @staticmethod
    def _build_items_with_count(
            item_counts: dict[str, int],
            item_details: dict[str, str],
            redis_data_dict: dict[str, dict]
    ) -> list[tuple]:
        """
        Построение списка предметов с их количеством, используя данные из Redis.

        Аргументы:
            item_counts: Словарь с уникальными идентификаторами предметов и их количеством.
            item_details: Словарь с уникальными идентификаторами предметов и их market hash names.
            redis_data_dict: Словарь с ключами Redis и декодированными данными.

        Возвращает:
            Список кортежей с объектами Item и их количеством.
        """
        items_with_count = []
        for uid, count in item_counts.items():
            if uid in item_details:
                redis_key = f'steam_market::{item_details[uid]}'
                if redis_key in redis_data_dict:
                    market_item_data = redis_data_dict[redis_key]
                    item = Item(item_details[uid], **market_item_data)
                    items_with_count.append((item, count))
        return items_with_count

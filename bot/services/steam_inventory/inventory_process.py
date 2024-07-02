from collections import defaultdict

from bot.types.InventoryAsset import InventoryAsset
from bot.types.InventoryDescription import InventoryDescription


class InventoryProcess:
    async def parse_inventory_data(
            self,
            assets: list[InventoryAsset],
            descriptions: list[InventoryDescription]
    ) -> list[tuple] | None:
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

        item_names_with_count = self._build_items_with_count(item_counts, item_details)

        if item_names_with_count:
            return item_names_with_count
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

    @staticmethod
    def _build_items_with_count(
            item_counts: dict[str, int],
            item_details: dict[str, str],
    ) -> list[tuple]:
        """
        Построение списка предметов с их количеством, используя данные из Redis.

        Аргументы:
            item_counts: Словарь с уникальными идентификаторами предметов и их количеством.
            item_details: Словарь с уникальными идентификаторами предметов и их market hash names.

        Возвращает:
            Список кортежей с названиеями и их количеством.
        """
        items_with_count = []
        for uid, count in item_counts.items():
            if uid in item_details:
                items_with_count.append((item_details[uid], count))
        return items_with_count

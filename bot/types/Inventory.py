from dataclasses import dataclass
from typing import List

from orjson import orjson

from bot.types.Item import Item


@dataclass
class Inventory:
    """Класс для представления инвентаря, содержащего список предметов."""

    items: List[Item]  # Список предметов в инвентаре

    def total_cases(self) -> int:
        """Вычисляет общее количество предметов-кейсов в инвентаре."""
        count = 0
        for item in self.items:
            if 'case' in item.item_name.lower():
                count += 1
        return count

    def total_price(self) -> float:
        """Вычисляет общую стоимость всех предметов в инвентаре."""
        total_prices = 0
        for item in self.items:
            total_prices += item.price
        return total_prices

    @staticmethod
    def from_json_and_prices(inventory_json: str, prices_results: List[Item]) -> 'Inventory':
        """
        Создает объект Inventory из JSON данных и списка предметов с ценами.

        Args:
            inventory_json (str): JSON строка, представляющая инвентарь.
            prices_results (List[Item]): Список предметов с ценами для сопоставления с инвентарем.

        Returns:
            Inventory: Объект Inventory, содержащий предметы с ценами из списка prices_results.
        """
        inventory_dict = orjson.loads(inventory_json)
        items = []
        for item_name, count in inventory_dict.items():
            for price_item in prices_results:
                if item_name == price_item.item_name:
                    for _ in range(count):
                        items.append(
                            Item(
                                item_name=item_name,
                                price=price_item.price,
                                doppler_prices=price_item.doppler_prices
                            )
                        )
                    break
        return Inventory(items=items)

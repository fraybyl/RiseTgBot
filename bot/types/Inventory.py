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
        count = sum(1 for item in self.items if 'case' in item.item_name.lower())
        return count

    def total_price(self) -> float:
        """Вычисляет общую стоимость всех предметов в инвентаре."""
        total_prices = sum(item.price for item in self.items)
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
        inventory_list = orjson.loads(inventory_json)
        price_dict = {item.item_name: item for item in prices_results}

        items = [
            Item(
                item_name=item_name,
                price=price_dict[item_name].price,
                doppler_prices=price_dict[item_name].doppler_prices
            )
            for item_name, count in inventory_list if item_name in price_dict
            for _ in range(count)
        ]

        return Inventory(items=items)

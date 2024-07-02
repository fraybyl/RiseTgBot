from dataclasses import dataclass

from orjson import orjson

from bot.types.Item import Item


@dataclass
class Inventory:
    items: list[Item]

    def total_cases(self) -> int:
        count = 0
        for item in self.items:
            if 'case' in item.item_name.lower():
                count += 1
        return count

    def total_price(self) -> float:
        total_prices = 0
        for item in self.items:
            total_prices += item.price
        return total_prices

    @staticmethod
    def from_json_and_prices(inventory_json: str, prices_results: list[Item]) -> 'Inventory':
        inventory_dict = orjson.loads(inventory_json)
        items = []
        for item_name, count in inventory_dict:
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

import orjson

from bot.types.Item import Item


class Inventory(dict):
    def __init__(self, items: list):
        super().__init__({item.item_name: {'price': item.price, 'count': count} for item, count in items})

    @classmethod
    def from_data(cls, data: list):
        items = [(Item(item_data['item_name'], item_data['price']), count) for item_data, count in data]
        return cls(items)

    @classmethod
    def from_json(cls, json_data: str):
        data = orjson.loads(json_data)
        items = [(Item(name, details['price']), details['count']) for name, details in data.items()]
        return cls(items)

    def to_dict(self):
        return {key: {'price': value['price'], 'count': value['count']} for key, value in self.items()}

    def to_json(self):
        return orjson.dumps(self.to_dict()).decode('utf-8')

    def total_price(self) -> float:
        return sum(details['price'] * details['count'] for details in self.values())

    def total_count(self) -> int:
        return sum(details['count'] for details in self.values())

    def total_case_items(self) -> int:
        return sum(details['count'] for name, details in self.items() if 'case' in name.lower())

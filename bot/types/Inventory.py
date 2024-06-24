import orjson

from bot.types.Item import Item


class Inventory(dict):
    def __init__(self, items: list):
        super().__init__({item.item_name: {'price': item.price, 'count': count} for item, count in items})

    @classmethod
    def from_data(cls, data: list):
        items = [(Item(item_data['item_name'], item_data['price']), count) for item_data, count in data]
        return cls(items)

    def to_dict(self):
        return {key: {'price': value['price'], 'count': value['count']} for key, value in self.items()}

    def to_json(self):
        return orjson.dumps(self.to_dict()).decode('utf-8')

    def total_price(self) -> float:
        return sum(details['price'] * details['count'] for details in self.values())


from bot.types.Item import Item


class Inventory(dict):
    def __init__(self, items: list[Item]):
        super().__init__(items=items)

    @classmethod
    def from_dict(cls, data: dict):
        items = [Item.from_dict(item) for item in data['items']]
        return cls(items)

    def to_dict(self):
        return {'items': [dict(item) for item in self['items']]}

    @property
    def items(self):
        return self['items']

class Item(dict):
    def __init__(
            self,
            item_name: str,
            price: float,
            sell_count: int = 0
    ) -> None:
        super().__init__(
            item_name=item_name,
            price=round(price, 2),
            sell_count=sell_count
        )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            item_name=data.get('item_name', ''),
            price=data.get('price', 0),
            sell_count=data.get('sell_count', 0)
        )

    @property
    def item_name(self) -> str:
        return self['item_name']

    @property
    def price(self) -> float:
        return self['price']

    @property
    def sell_count(self) -> int:
        return self['sell_count']

    def total_capitalization(self) -> float:
        return round(self.price * self.sell_count, 2)

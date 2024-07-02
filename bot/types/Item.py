from dataclasses import dataclass, field

from orjson import orjson


@dataclass
class Item:
    item_name: str
    price: float = field(default=0.0)
    doppler_prices: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, item_name: str, data: dict):
        price = data.get('price', 0.0)
        doppler_prices = data.get('doppler', {})
        return cls(
            item_name=item_name,
            price=round(price, 2),
            doppler_prices=doppler_prices
        )

    @classmethod
    def from_json(cls, item_name: bytes, data: bytes, currency_ratio: float):
        item_name = item_name.decode('utf-8')
        data = orjson.loads(data.decode('utf-8'))
        price = float(data.get('price', 0.0))
        doppler_prices = data.get('doppler', {})# здесь не доделано
        return cls(
            item_name=item_name,
            price=round(price * currency_ratio, 2),
            doppler_prices=doppler_prices
        )

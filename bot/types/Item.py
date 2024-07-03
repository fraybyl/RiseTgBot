from dataclasses import dataclass, field

from orjson import orjson


@dataclass
class Item:
    """
    Класс для представления предмета.

    Attributes:
        item_name (str): Название предмета.
        price (float, optional): Цена предмета (по умолчанию 0.0).
        doppler_prices (dict, optional): Словарь с ценами для доплеров (по умолчанию пустой).

    Methods:
        from_dict(cls, item_name: str, data: dict) -> 'Item':
            Создает объект Item из словаря данных.

        from_json(cls, item_name: bytes, data: bytes, currency_ratio: float) -> 'Item':
            Создает объект Item из JSON данных и коэффициента конвертации валюты.
    """
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
        doppler_prices = data.get('doppler', {})  # здесь не доделано
        return cls(
            item_name=item_name,
            price=round(price * currency_ratio, 2),
            doppler_prices=doppler_prices
        )

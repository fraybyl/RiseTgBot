import math

def calculate_discount_percentage(price, discount):
    """
    Вычисляет процент скидки на основе цены и значения скидки.

    Args:
        price (float): Цена товара до применения скидки.
        discount (float): Величина скидки в процентах.

    Returns:
        float: Цена товара после применения скидки, округленная до двух знаков после запятой.
    """
    discount_percentage = float(price) * (1 - float(discount) / 100)
    discount_percentage = round(discount_percentage, 2)
    return float(discount_percentage)


def calculate_quantity(price, discount, minimal_price):
    """
    Вычисляет необходимое количество товара для достижения минимальной цены.

    Args:
        price (float): Цена товара до применения скидки.
        discount (float): Величина скидки в процентах.
        minimal_price (float): Минимальная цена товара.

    Returns:
        int: Необходимое количество товара, округленное вверх до ближайшего целого числа.
    """
    discount_percentage = calculate_discount_percentage(price, discount)
    quantity = int(minimal_price) / float(discount_percentage)
    quantity = math.ceil(float(quantity))
    return int(quantity)


def calculate_max_bonus(price, discount, minimal_price):
    """
    Вычисляет максимальный бонус от скидки.

    Args:
        price (float): Цена товара до применения скидки.
        discount (float): Величина скидки в процентах.
        minimal_price (float): Минимальная цена товара.

    Returns:
        int: Максимальный бонус от скидки, округленный до ближайшего целого числа. Возвращает 0, если бонус отрицательный.
    """
    discount_percentage = calculate_discount_percentage(price, discount)
    bonus = float(discount_percentage) - float(minimal_price)
    bonus = math.floor(bonus)
    return max(0, bonus)

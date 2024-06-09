import math



def calculate_discount_for_price(base_price, discount):
    try:
        base_price = float(base_price)
        discount = float(discount)
    except ValueError:
        return "Ошибка: Неверный формат чисел."
    
    return (base_price * (1 - discount / 100))
    
def calculate_quantity_for_min_price(min_price, base_price, discount, bonus_points=0):
    # Приведение типов и валидация входных параметров
    try:
        min_price = float(min_price)
        base_price = float(base_price)
        discount = float(discount)
        bonus_points = float(bonus_points)
    except ValueError:
        return "Ошибка: Неверный формат чисел."
    
    # Эффективная цена за один товар после скидки
    effective_price_per_item = calculate_discount_for_price(base_price, discount)

    # Общая стоимость всех товаров с учетом скидки

    # Общая стоимость всех товаров с учетом бонусных очков
    effective_price_per_item -= bonus_points

    # Рассчитываем дополнительное количество товаров, необходимое для достижения минимальной цены
    additional_quantity = math.ceil((min_price / effective_price_per_item))

    return additional_quantity
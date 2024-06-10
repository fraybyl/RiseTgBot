import math

def calculate_discount_percentage(price, discount):
    discount_percentage = float(price) * (1 - float(discount) / 100)
    discount_percentage = round(discount_percentage, 2)
    return float(discount_percentage)

def calculate_quantity(price, discount, minimal_price):
    discount_percentage = calculate_discount_percentage(price, discount)
    quantity = int(minimal_price) / float(discount_percentage)
    quantity = math.ceil(float(quantity))
    return int(quantity)

def calculate_max_bonus(price, discount, minimal_price):
    discount_percentage = calculate_discount_percentage(price, discount)
    bonus = float(discount_percentage) - float(minimal_price)
    bonus = math.floor(bonus)
    return max(0, bonus)
import math

def calculate_discount_for_price(base_price, discount):
    return float(base_price) * (1 - float(discount) / 100)

def calculate_quantity_for_min_price(min_price, base_price, discount, bonus_points=0):
    base_price, discount, min_price, bonus_points = map(float, [base_price, discount, min_price, bonus_points])
    effective_price = calculate_discount_for_price(base_price, discount) - bonus_points
    return math.ceil(min_price / effective_price)

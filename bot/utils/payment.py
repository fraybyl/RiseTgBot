import hashlib
import requests
from bot.core.config import settings
from bot.database.models import Product, User
from bot.utils.buy_math import calculate_discount_percentage


def calculate_amount(quantity_product: int, product: dict[str, any], user: dict[str, any], quantity_bonus=0.0) -> float:
    return calculate_discount_percentage((quantity_product * product['price']), user['discount_percentage']) - quantity_bonus


async def initiate_payment(
        user: dict[str, any],
        quantity_product: int,
        product: dict[str, any],
        quantity_bonus,
        order_id: int
) -> str:
    amount = calculate_amount(quantity_product, product, user, quantity_bonus)
    merchant_id = settings.MERCHANT_ID
    secret_word = settings.SECRET_WORD_1
    currency = 'RUB'

    sign = hashlib.md5(f"{merchant_id}:{amount}:{secret_word}:{currency}:{order_id}".encode()).hexdigest()

    payment_url = (
        f"https://pay.freekassa.com/?m={merchant_id}&oa={amount}&currency={currency}&o={product['label']-quantity_product-order_id}&s={sign}&lang=ru"
    )
    return payment_url

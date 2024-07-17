import hashlib
import requests
from bot.core.config import settings


def calculate_amount(quantity_product: int, price) -> float:
    return quantity_product * price


async def initiate_payment(user_id: int, quantity_product: int) -> str:
    amount = calculate_amount(quantity_product, 100)
    merchant_id = settings.MERCHANT_ID
    secret_word = settings.SECRET_WORD_1
    order_id = f"{user_id}-{quantity_product}"
    currency = 'RUB'

    sign = hashlib.md5(f"{merchant_id}:{amount}:{secret_word}:{currency}:{order_id}".encode()).hexdigest()

    payment_url = (
        f"https://pay.freekassa.com/?m={merchant_id}&oa={amount}&currency={currency}&o={order_id}&s={sign}&lang=ru"
    )
    return payment_url

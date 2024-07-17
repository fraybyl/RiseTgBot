import hashlib
import logging

from aiohttp import web
from bot.core.config import settings
from bot.core.loader import bot


async def verify_signature(data):
    sign = hashlib.md5(
        f"{data['MERCHANT_ID']}:{data['AMOUNT']}:{settings.SECRET_WORD_2}:{data['MERCHANT_ORDER_ID']}".encode()
    ).hexdigest()
    return sign == data['SIGN']


async def handle_payment_notification(request):
    print("Received request")
    data = await request.post()
    print(f"Request data: {data}")
    remote_addr = request.remote
    print(f"Remote address: {remote_addr}")

    if remote_addr not in settings.WHITELISTED_IPS:
        logging.info(f'remote addr: {remote_addr}, whitelist: {settings.WHITELISTED_IPS}')
        print("Forbidden IP")
        return web.Response(status=403, text="Forbidden")

    if not await verify_signature(data):
        print("Wrong signature")
        return web.Response(status=400, text="Wrong signature")

    print("Processing payment")
    merchant_id = data['MERCHANT_ID']
    amount = data['AMOUNT']
    order_id = data['MERCHANT_ORDER_ID']
    payment_id = data['intid']

    user_id, quantity_product = order_id.split('-')
    await bot.send_message(int(user_id), f"Ваш платеж на сумму {amount} RUB успешно обработан!")

    print("Payment processed successfully")
    return web.Response(text="YES")



app = web.Application()
app.router.add_post(settings.WEBHOOK_PATH, handle_payment_notification)

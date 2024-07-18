import hashlib
from aiohttp import web
from bot.core.config import settings
from bot.core.loader import bot


async def verify_signature(data):
    sign = hashlib.md5(
        f"{data['MERCHANT_ID']}:{data['AMOUNT']}:{settings.SECRET_WORD_2}:{data['MERCHANT_ORDER_ID']}".encode()
    ).hexdigest()
    return sign == data['SIGN']


async def handle_payment_notification(request):
    data = await request.post()
    remote_addr = request.headers.get('X-Real-IP', request.remote)
    print(f"remote_addr: {remote_addr}")

    if remote_addr not in settings.WHITELISTED_IPS:
        return web.Response(status=403, text="Forbidden")

    if not await verify_signature(data):
        return web.Response(status=400, text="Wrong signature")

    # Обработка успешного платежа
    merchant_id = data['MERCHANT_ID']
    amount = data['AMOUNT']
    order_id = data['MERCHANT_ORDER_ID']
    payment_id = data['intid']

    user_id, quantity_product = order_id.split('-')
    await bot.send_message(int(user_id), f"Ваш платеж на сумму {amount} RUB успешно обработан!")

    return web.Response(text="YES")


app = web.Application()
app.router.add_post(settings.WEBHOOK_PATH, handle_payment_notification)

import hashlib
from aiohttp import web
from bot.core.config import settings


async def verify_signature(data):
    sign = hashlib.md5(
        f"{data['MERCHANT_ID']}:{data['AMOUNT']}:{settings.SECRET_WORD_2}:{data['MERCHANT_ORDER_ID']}".encode()).hexdigest()
    return sign == data['SIGN']


async def handle_payment_notification(request):
    data = await request.post()
    remote_addr = request.remote
    if remote_addr not in settings.WHITELISTED_IPS:
        return web.Response(status=403, text="Forbidden")

    if await verify_signature(data):
        # Обработка успешного платежа
        return web.Response(text="YES")
    else:
        return web.Response(status=400, text="wrong sign")


app = web.Application()
app.router.add_post(settings.WEBHOOK_PATH, handle_payment_notification)

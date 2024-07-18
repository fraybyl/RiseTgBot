import hashlib
from aiohttp import web
from bot.core.config import settings
from bot.core.loader import bot


async def verify_signature(data):
    expected_sign = hashlib.md5(
        f"{data['MERCHANT_ID']}:{data['AMOUNT']}:{settings.SECRET_WORD_2}:{data['MERCHANT_ORDER_ID']}".encode()
    ).hexdigest()
    return expected_sign == data['SIGN']


async def handle_payment_notification(request):
    try:
        data = await request.post()
        remote_addr = request.headers.get('X-Real-IP', request.remote)
        print(f"Received request from: {remote_addr}")

        if remote_addr not in settings.WHITELISTED_IPS:
            print("IP not whitelisted.")
            return web.Response(status=403, text="Forbidden")

        if not await verify_signature(data):
            print("Signature mismatch.")
            return web.Response(status=400, text="Wrong signature")

        # Validate required parameters
        required_fields = ['MERCHANT_ID', 'AMOUNT', 'MERCHANT_ORDER_ID', 'intid']
        for field in required_fields:
            if field not in data:
                print(f"Missing field: {field}")
                return web.Response(status=400, text=f"Missing field: {field}")

        # Обработка успешного платежа
        merchant_id = data['MERCHANT_ID']
        amount = data['AMOUNT']
        order_id = data['MERCHANT_ORDER_ID']
        payment_id = data['intid']

        # Ensure order_id follows the expected format
        try:
            user_id, quantity_product = order_id.split('-')
        except ValueError:
            print("Order ID format is invalid.")
            return web.Response(status=400, text="Order ID format is invalid")

        # Log payment information
        print(f"Payment received: merchant_id={merchant_id}, amount={amount}, order_id={order_id}, payment_id={payment_id}")

        # Send confirmation message to the user
        await bot.send_message(int(user_id), f"Ваш платеж на сумму {amount} RUB успешно обработан!")

        return web.Response(text="YES")

    except Exception as e:
        print(f"Error processing payment notification: {e}")
        return web.Response(status=500, text="Internal server error")


app = web.Application()
app.router.add_post(settings.WEBHOOK_PATH, handle_payment_notification)
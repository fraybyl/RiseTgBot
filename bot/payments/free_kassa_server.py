import hashlib
from aiohttp import web
from loguru import logger
from bot.core.config import settings
from bot.core.loader import bot
from bot.database.db_requests import get_order_by_id, update_order_payment_id, update_order_status


async def verify_signature(data: dict) -> bool:
    """
    Проверка подписи уведомления о платеже.

    :param data: Словарь с данными платежа
    :return: Булево значение, указывающее, является ли подпись действительной
    """
    expected_sign = hashlib.md5(
        f"{data['MERCHANT_ID']}:{data['AMOUNT']}:{settings.SECRET_WORD_2}:{data['MERCHANT_ORDER_ID']}".encode()
    ).hexdigest()
    return expected_sign == data['SIGN']


async def handle_payment_notification(request: web.Request) -> web.Response:
    """
    Обработка входящего уведомления о платеже.

    :param request: Запрос aiohttp
    :return: Ответ aiohttp
    """
    try:
        data = await request.post()
        remote_addr = request.headers.get('X-Real-IP', request.remote)

        # Проверка на IP-адрес из белого списка
        if remote_addr not in settings.WHITELISTED_IPS:
            return web.Response(status=403, text="Forbidden")

        # Проверка подписи
        if not await verify_signature(data):
            return web.Response(status=400, text="Неверная подпись")

        # Проверка на наличие обязательных параметров
        required_fields = ['MERCHANT_ID', 'AMOUNT', 'MERCHANT_ORDER_ID', 'intid']
        for field in required_fields:
            if field not in data:
                return web.Response(status=400, text=f"Отсутствует поле: {field}")

        order_id = int(data['MERCHANT_ORDER_ID'])
        print(order_id)
        payment_id = data['intid']

        # Получение заказа
        order = await get_order_by_id(order_id)
        if not order:
            logger.error(f"Order not found: {order_id}")
            return web.Response(status=400, text="Order not found")

        # Обновление статуса заказа
        await update_order_status(order_id, 'paid')

        # Обновление payment_id заказа (добавьте эту функцию в ваш код)
        await update_order_payment_id(order_id, payment_id)

        # Отправка подтверждающего сообщения пользователю
        await bot.send_message(order.user_id, f"Ваш платеж на сумму {data['AMOUNT']} RUB успешно обработан!")

    except Exception as e:
        logger.error(f"Ошибка при обработке уведомления о платеже: {e}")
        return web.Response(status=500, text="Внутренняя ошибка сервера")

app = web.Application()
app.router.add_post(settings.WEBHOOK_PATH, handle_payment_notification)
import asyncio
from datetime import datetime
from functools import wraps

from aiogram.types import CallbackQuery


def throttle(rate_limit: int):
    """
    Декоратор, позволяющий пользователям throttle вызываемую функцию.
    :param rate_limit: Ограничение скорости в секундах.
    :return: Декорированная функция.
    """
    def decorator(func):
        @wraps(func)
        async def wrapped(callback_query: CallbackQuery, *args, **kwargs):
            now = datetime.now().timestamp()
            user_id = callback_query.from_user.id

            async with wrapped.lock:
                if user_id in wrapped.last_called:
                    elapsed = now - wrapped.last_called[user_id]
                    if elapsed < rate_limit:
                        await callback_query.answer(
                            f"Много попыток: попробуйте через {rate_limit - int(elapsed)} секунд",
                            show_alert=True
                        )
                        return

                wrapped.last_called[user_id] = now

            return await func(callback_query, *args, **kwargs)

        wrapped.last_called = {}
        wrapped.lock = asyncio.Lock()
        return wrapped

    return decorator

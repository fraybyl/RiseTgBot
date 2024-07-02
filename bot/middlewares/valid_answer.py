from typing import Callable, Dict, Any, Awaitable

import fluent.runtime
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


class ValidateQuantityMiddleware(BaseMiddleware):
    """
    А это вроде не доделано надо доделать
    мидлварь которая проверяет правильный ли введенный текст.
    :params event: Событие
    :returns Если является числом и больше 0, True, иначе False
    """
    def __init__(self, locale: fluent.runtime.FluentLocalization):
        self.locale = locale

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.text.isdigit() and int(event.text) > 0:
            data['valid'] = True
        else:
            await event.answer(self.locale.format_value('invalid_quantity'))
            data['valid'] = False
        return await handler(event, data)


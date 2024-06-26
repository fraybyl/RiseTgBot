from typing import Callable, Dict, Any, Awaitable

import fluent.runtime
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


class ValidateQuantityMiddleware(BaseMiddleware):
    def __init__(self, locale: fluent.runtime.FluentLocalization):
        self.locale = locale

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        state: FSMContext = data['state']
        if event.text.isdigit() and int(event.text) > 0:
            data['valid'] = True
        else:
            await event.answer(self.locale.format_value('invalid_quantity'))
            data['valid'] = False
        return await handler(event, data)


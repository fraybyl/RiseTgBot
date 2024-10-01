from typing import Callable, Dict, Any, Awaitable

import fluent.runtime
from aiogram import BaseMiddleware
from aiogram.types import Message


class L10nMiddleware(BaseMiddleware):
    """
    Регистрирует мидлварь на локализацию в файле Locale.ftl
    :param locale: Принимает локаль из инициализации
    :returns Возвращает локаль из файла locale.ftl
    """

    def __init__(
            self,
            locale: fluent.runtime.FluentLocalization
    ):
        self.locale = locale

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        data["l10n"] = self.locale
        return await handler(event, data)

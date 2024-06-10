from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from fluent.runtime import FluentLocalization


class L10nMiddleware(BaseMiddleware):
    def __init__(
        self,
        locale: FluentLocalization
    ):
        self.locale = locale
        self.original_format_value = self.locale.format_value  # Сохраняем оригинальную функцию

    def escape_format_value(self, message_id: str, args: dict = None) -> str:
        """
        Escape Markdown special characters.
        """
        raw_text = self.original_format_value(message_id, args or {})
        escape_chars = "`*{}[]()#+-.!>_"
        replacements = {char: f'\\{char}' for char in escape_chars}
        return ''.join(replacements.get(char, char) for char in raw_text)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        data["l10n"] = self.locale

        # Заменяем метод форматирования на нашу функцию
        data["l10n"].format_value = self.escape_format_value

        return await handler(event, data)


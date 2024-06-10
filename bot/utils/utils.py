from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_inline_keyboard(buttons):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text, callback_data=data) for text, data in row] for row in buttons])

def escape_characters(text: str) -> str:
    return text.replace('.', '\\.').replace('-', '\\-').replace('_', '\\_')
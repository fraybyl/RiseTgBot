from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.strategy import FSMStrategy
from aiogram.enums import ParseMode
from bot.config import settings
import json
from aiogram.client.default import DefaultBotProperties
import logging

# Включаем логирование, чтобы отслеживать возможные ошибки
logging.basicConfig(level=logging.INFO)

class FileIds:
    def __init__(self, json_path):
        self.json_path = json_path
        self.file_ids = self.load_file_ids()

    def load_file_ids(self):
        try:
            with open(self.json_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_file_id(self, file_id, key):
        self.file_ids[key]['file_id'] = file_id
        with open(self.json_path, 'w') as file:
            json.dump(self.file_ids, file, indent=4)

    def get_file_path(self, key):
        return self.file_ids.get(key, {}).get('path')

    def get_file_id(self, key):
        return self.file_ids.get(key, {}).get('file_id')

    def has_file_id(self, key):
        return 'file_id' in self.file_ids.get(key, {})

fileIds = FileIds('data/file_ids.json')

# Инициализация бота и диспетчера
bot = Bot(
    token=settings.settings.bot_token.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)



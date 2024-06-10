from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.strategy import FSMStrategy
from aiogram.enums import ParseMode
from bot.settings import settings, config
import json
from aiogram.client.default import DefaultBotProperties
import logging
from pathlib import Path
from fluent.runtime import FluentLocalization, FluentResourceLoader
# Включаем логирование, чтобы отслеживать возможные ошибки
logging.basicConfig(level=logging.INFO)

def get_fluent_localization() -> FluentLocalization:
    """
    Загрузка файла с локалями 'locale.ftl' из каталога 'l10n' в текущем расположении
    :return: объект FluentLocalization
    """

    # Проверки, чтобы убедиться
    # в наличии правильного файла в правильном каталоге
    locale_dir = Path(__file__).parent.joinpath("bot/l10n")
    if not locale_dir.exists():
        error = "'l10n' directory not found"
        raise FileNotFoundError(error)
    if not locale_dir.is_dir():
        error = "'l10n' is not a directory"
        raise NotADirectoryError(error)
    locale_file = Path(locale_dir, "locale.ftl")
    if not locale_file.exists():
        error = "locale.txt file not found"
        raise FileNotFoundError(error)

    # Создание необходимых объектов и возврат объекта FluentLocalization
    l10n_loader = FluentResourceLoader(
        str(locale_file.absolute()),
    )
    return FluentLocalization(
        locales=["ru"],
        resource_ids=[str(locale_file.absolute())],
        resource_loader=l10n_loader
    )

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
configJson = config.ConfigManager('data/config.json')

# Инициализация бота и диспетчера
bot = Bot(
    token=settings.settings.bot_token.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)




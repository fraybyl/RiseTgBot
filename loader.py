from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from bot.settings import settings, config
from aiogram.client.default import DefaultBotProperties
from bot.database.redis_db import RedisCache
import logging

logging.basicConfig(level=logging.INFO)

fileIds = config.FileIds('data/file_ids.json')
configJson = config.ConfigManager('data/config.json')

# Инициализация бота и диспетчера
bot = Bot(
    token=settings.settings.bot_token.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

redis_ban_check = RedisCache(db=0)




from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from bot.settings import settings, config
from aiogram.client.default import DefaultBotProperties
import logging
import redis.asyncio as redis

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

pool_db = redis.ConnectionPool().from_url("redis://127.0.0.1", db=0)
pool_cache = redis.ConnectionPool().from_url("redis://127.0.0.1", db=1)

redis_db = redis.Redis(connection_pool=pool_db)
redis_cache = redis.Redis(connection_pool=pool_cache)




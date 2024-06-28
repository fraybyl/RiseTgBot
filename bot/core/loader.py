from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from redis.asyncio import ConnectionPool, Redis

from bot.core.config import settings
from bot.utils.json_config import ConfigFileManager

token = settings.BOT_TOKEN.get_secret_value()

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

redis_db = Redis(
    connection_pool=ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASS,
        db=0
    ), decode_responses=True
)

storage = RedisStorage(
    redis=redis_db,
    key_builder=DefaultKeyBuilder(),
)

config_json = ConfigFileManager('data/config.json', 'data/file_ids.json')

dp = Dispatcher(storage=storage)

import orjson
from loguru import logger

from bot.core.loader import redis_db
from bot.database.db_requests import get_users_with_steam_accounts, get_steamid64_by_userid
from bot.services.steam_ban.fetch_steam_ban import add_player_bans


async def ban_statistics_schedule() -> None:
    logger.info('Обновление статистики банов начато...')
    try:
        all_users = await get_users_with_steam_accounts()
        for user in all_users:
            redis_key = f"telegram_user::{user}"
            accounts = await get_steamid64_by_userid(user)
            results = await add_player_bans(accounts, user)
            await redis_db.hset(redis_key, 'ban_stat', orjson.dumps(results))

        logger.info('Обновление статистики банов завершено')
    except Exception as e:
        logger.error(f"Ошибка в ban_statistics_schedule: {e}")

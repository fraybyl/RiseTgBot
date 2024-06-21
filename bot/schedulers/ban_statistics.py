from loguru import logger

from bot.core.loader import redis_db
from bot.database.db_requests import get_all_steamid64
from bot.services.steam_ban.fetch_steam_ban import get_player_bans, switch_keys


async def ban_statistics_schedule() -> None:
    logger.info('Обновление статистики банов...')
    steam_accounts = await get_all_steamid64()
    temp_and_final_keys = await get_player_bans(steam_accounts, True)
    temp_keys = [pair[0] for pair in temp_and_final_keys if pair[0]]
    final_keys = [pair[1] for pair in temp_and_final_keys if pair[1]]
    async with redis_db.pipeline() as pipe:
        try:
            old_keys = await redis_db.keys('ban_stat::*')
            if old_keys:
                await pipe.delete(*old_keys)
            await switch_keys(temp_keys, final_keys, pipe)
            await pipe.execute()

        except Exception as e:
            logger.error(f"Ошибка при атомарном обновление ban_stat ключей, {e}")

    logger.info('Обновление статистики банов завершено')

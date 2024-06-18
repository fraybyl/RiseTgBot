from bot.database.db_requests import get_all_steamid64
from bot.utils.steam_utils.steamid import get_player_bans, switch_keys
from loader import logging, redis_db



async def ban_stat_schedule() -> None:
    logging.info('Обновление статистики банов...')
    steam_accounts = await get_all_steamid64()
    temp_and_final_keys = await get_player_bans(steam_accounts, True)

    temp_keys = [pair[0] for pair in temp_and_final_keys if pair[0]]
    final_keys = [pair[1] for pair in temp_and_final_keys if pair[1]]
    
    async with redis_db.pipeline(transaction=True) as pipe:
        try:
            old_keys = await redis_db.keys('ban_stat::*')
            if old_keys:
                await pipe.delete(*old_keys)
            await switch_keys(temp_keys, final_keys, pipe)
            await pipe.execute()
        except Exception as e:
            logging.error(f"Error during atomic update of ban_stat keys, {e}")

    logging.info('Обновление статистики банов завершено')
    
    
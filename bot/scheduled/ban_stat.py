from bot.database.db_requests import get_all_steamid64
from bot.utils.steamid import get_player_bans
from loader import configJson, logging

async def ban_stat() -> bool:
    logging.info('Обновление статистики банов...')
    steam_accounts = await get_all_steamid64()
    await get_player_bans(steam_accounts)
    logging.info('Обновление статистики банов завершено')
    
    
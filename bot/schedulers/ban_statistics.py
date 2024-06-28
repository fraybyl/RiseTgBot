from loguru import logger

from bot.core.loader import redis_db
from bot.database.db_requests import get_all_steamid64, get_steamids64_owners
from bot.handlers.message_distributor_handlers import send_message_ban
from bot.services.steam_ban.fetch_steam_ban import add_or_update_player_bans
from bot.types.AccountInfo import AccountInfo


async def fetch_ban_statistics(keys):
    pipeline = redis_db.pipeline()
    for key in keys:
        pipeline.hget(key, 'ban')
    results = await pipeline.execute()
    return [AccountInfo.from_json(result) for result in results if result]


async def ban_statistics_schedule() -> None:
    logger.info('Обновление статистики банов начато...')
    try:
        all_accounts = await get_all_steamid64()
        cursor = '0'
        ban_statistics = {}
        bans = []
        while cursor != 0:
            cursor, keys = await redis_db.scan(cursor=cursor, count=30000, match='data::*')
            if keys:
                ban_infos = await fetch_ban_statistics(keys)
                for ban_info in ban_infos:
                    ban_statistics[ban_info.steam_id] = ban_info

        stat = await add_or_update_player_bans(all_accounts, True)
        for new_ban_statistics in stat:
            if new_ban_statistics != ban_statistics[new_ban_statistics.steam_id]:
                bans.append(int(new_ban_statistics.steam_id))

        if bans:
            user_bans = await get_steamids64_owners(bans)
            for key, value in user_bans.items():
                await send_message_ban(key, value)

        logger.info('Обновление статистики банов завершено')
    except Exception as e:
        logger.error(f"Ошибка в ban_statistics_schedule: {e}")

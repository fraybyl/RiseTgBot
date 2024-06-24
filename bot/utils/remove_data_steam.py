from loguru import logger

from bot.core.loader import redis_db


async def remove_data_steam(steam_ids: list[int]) -> None:
    if isinstance(steam_ids, list):
        for steam_id in steam_ids:
            await redis_db.delete(f'data::{steam_id}')
            logger.info(f'Удален {steam_id}')

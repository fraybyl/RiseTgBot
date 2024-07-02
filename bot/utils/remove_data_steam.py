from bot.core.loader import redis_db


async def remove_data_steam(steam_ids: list[int]) -> None:
    """
    Удаляет данные Steam для указанных steam_id из Redis.

    Args:
        steam_ids (list[int]): Список steam_id, для которых требуется удалить данные.

    Raises:
        TypeError: Если steam_ids не является списком.

    Returns:
        None
    """
    if isinstance(steam_ids, list):
        for steam_id in steam_ids:
            await redis_db.delete(f'data::{steam_id}')

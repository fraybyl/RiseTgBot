from typing import Optional

from fluent.runtime import FluentLocalization
from orjson import orjson
from loguru import logger

from bot.core.loader import redis_cache, redis_db


async def get_accounts_statistics(steam_ids: Optional[list[int]] = None) -> dict[str, int]:
    total_vac_bans = 0
    total_community_bans = 0
    total_game_bans = 0
    bans_last_week = 0
    total_bans = 0
    total_accounts = 0
    steam_ids_set = set(steam_ids) if steam_ids else None
    cursor = '0'

    while cursor != 0:
        cursor, keys = await redis_db.scan(cursor=cursor, count=30000, match='ban_stat::*')
        if keys:
            pipeline = redis_db.pipeline()
            pipeline.mget(keys)
            results = await pipeline.execute()

            for result in results:
                for value in result:
                    try:
                        data_list = orjson.loads(value.decode('utf-8'))
                        for data_dict in data_list:
                            steam_id = int(data_dict.get('SteamId', 0))
                            if steam_ids_set is None or steam_id in steam_ids_set:
                                total_accounts += 1
                                total_vac_bans += data_dict.get('VACBanned', 0)
                                total_game_bans += data_dict.get('NumberOfGameBans', 0)
                                total_community_bans += data_dict.get('CommunityBanned', 0)
                                last_ban = data_dict.get('DaysSinceLastBan', 0)
                                if last_ban > 0:
                                    total_bans += 1
                                    if last_ban <= 7:
                                        bans_last_week += 1

                    except orjson.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                    except Exception as e:
                        logger.error(f"Unexpected error: {e}")

    return {
        'total_accounts': total_accounts,
        'total_bans': total_bans,
        'total_vac_bans': total_vac_bans,
        'total_community_bans': total_community_bans,
        'total_game_bans': total_game_bans,
        'bans_last_week': bans_last_week
    }


async def get_inventories_statistics(steam_ids: Optional[list[int]] = None) -> dict[str, int]:
    total_elements = 0
    sum_price = 0
    filtered_items = 0
    cursor = '0'
    steam_ids_set = set(steam_ids) if steam_ids else None

    while cursor != 0:
        cursor, keys = await redis_db.scan(cursor=cursor, count=30000, match='inventory::*')
        if keys:
            pipeline = redis_db.pipeline()
            for key in keys:
                steam_id = int(key.decode('utf-8').split("::")[1])
                if not steam_ids_set or steam_id in steam_ids_set:
                    pipeline.get(key)
            results = await pipeline.execute()

            for result in results:
                if result:
                    values_list = orjson.loads(result)
                    for list in values_list:
                        item_name, quantity, price = list
                        total_elements += quantity
                        sum_price += price * quantity
                        if 'case' in item_name.lower():
                            filtered_items += quantity
    return {
        'total_elements': total_elements,
        'sum_price': sum_price,
        'total_case': filtered_items
    }


async def get_general_statistics(l10n: FluentLocalization) -> str:
    cache = await redis_cache.get('accounts_statistics')
    if cache:
        return cache

    inventories = await get_inventories_statistics()
    accounts = await get_accounts_statistics()

    text = l10n.format_value('general-accounts-info', {
        'accounts': accounts['total_accounts'],
        'total_bans': accounts['total_bans'],
        'total_vac': accounts['total_vac_bans'],
        'total_community': accounts['total_community_bans'],
        'total_game_ban': accounts['total_game_bans'],
        'bans_in_last_week': accounts['bans_last_week'],
        'items': inventories['total_elements'],
        'cases': inventories['total_case'],
        'prices': inventories['sum_price']
    })

    await redis_cache.setex('accounts_statistics', 120, text)
    return text


async def get_personal_statistics(steam_ids: list[int], user_id: int, l10n: FluentLocalization) -> str:
    cache = await redis_cache.get(f'personal_statistics::{user_id}')
    if cache:
        return cache

    inventories = await get_inventories_statistics(steam_ids)
    accounts = await get_accounts_statistics(steam_ids)
    text = l10n.format_value('personal-accounts-info', {
        'accounts': accounts['total_accounts'],
        'total_bans': accounts['total_bans'],
        'total_vac': accounts['total_vac_bans'],
        'total_community': accounts['total_community_bans'],
        'total_game_ban': accounts['total_game_bans'],
        'bans_in_last_week': accounts['bans_last_week'],
        'items': inventories['total_elements'],
        'cases': inventories['total_case'],
        'prices': inventories['sum_price']
    })

    await redis_cache.setex(f'personal_statistics::{user_id}', 120, text)
    return text

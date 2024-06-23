from typing import Optional

from fluent.runtime import FluentLocalization
from orjson import orjson

from bot.core.loader import redis_cache, redis_db
from bot.types.AccountInfo import AccountInfo


async def process_ban_statistics(ban_stat_json: list[AccountInfo]) -> dict[str, int]:
    total_vac_bans = 0
    total_community_bans = 0
    total_game_bans = 0
    bans_last_week = 0
    total_bans = 0
    total_accounts = 0

    for account in ban_stat_json:
        total_accounts += 1
        total_vac_bans += int(account.vac_banned)
        total_game_bans += account.number_of_game_bans
        total_community_bans += int(account.community_banned)
        last_ban = account.days_since_last_ban
        if last_ban > 0:
            total_bans += 1
            if last_ban <= 7:
                bans_last_week += 1

    return {
        'total_accounts': total_accounts,
        'total_bans': total_bans,
        'total_vac_bans': total_vac_bans,
        'total_community_bans': total_community_bans,
        'total_game_bans': total_game_bans,
        'bans_last_week': bans_last_week
    }


async def get_account_statistic(user_id: int) -> dict[str, int]:
    redis_key = f"telegram_user::{user_id}"
    ban_stat_bytes = await redis_db.hget(redis_key, 'ban_stat')
    if ban_stat_bytes is not None:
        ban_stat_json = orjson.loads(ban_stat_bytes)
        ban_stat_json = [AccountInfo.from_dict(item) for item in ban_stat_json]
        return await process_ban_statistics(ban_stat_json)
    else:
        return {
            'total_accounts': 0,
            'total_bans': 0,
            'total_vac_bans': 0,
            'total_community_bans': 0,
            'total_game_bans': 0,
            'bans_last_week': 0
        }


async def get_all_accounts_statistics() -> dict[str, int]:
    cursor = '0'
    total_statistics = {
        'total_accounts': 0,
        'total_bans': 0,
        'total_vac_bans': 0,
        'total_community_bans': 0,
        'total_game_bans': 0,
        'bans_last_week': 0
    }

    while cursor != 0:
        cursor, keys = await redis_db.scan(cursor, match='telegram_user::*', count=30000)
        if keys:
            pipeline = redis_db.pipeline()
            for key in keys:
                pipeline.hget(key, 'ban_stat')
            ban_stats = await pipeline.execute()
            for ban_stat_bytes in ban_stats:
                if ban_stat_bytes is not None:
                    ban_stat_json = orjson.loads(ban_stat_bytes)
                    ban_stat_json = [AccountInfo.from_dict(item) for item in ban_stat_json]
                    stats = await process_ban_statistics(ban_stat_json)
                    for k, v in stats.items():
                        total_statistics[k] += v

    return total_statistics


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
                    for data_list in values_list:
                        item_name, quantity, price = data_list
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

    # inventories = await get_inventories_statistics()
    accounts = await get_all_accounts_statistics()

    text = l10n.format_value('general-accounts-info', {
        'accounts': accounts['total_accounts'],
        'total_bans': accounts['total_bans'],
        'total_vac': accounts['total_vac_bans'],
        'total_community': accounts['total_community_bans'],
        'total_game_ban': accounts['total_game_bans'],
        'bans_in_last_week': accounts['bans_last_week'],
        'items': 0,
        'cases': 0,
        'prices': 0
    })

    await redis_cache.setex('accounts_statistics', 120, text)
    return text


async def get_personal_statistics(user_id: int, l10n: FluentLocalization) -> str:
    cache = await redis_cache.get(f'personal_statistics::{user_id}')
    if cache:
        return cache

    # inventories = await get_inventories_statistics(user_id)
    accounts = await get_account_statistic(user_id)
    text = l10n.format_value('personal-accounts-info', {
        'accounts': accounts['total_accounts'],
        'total_bans': accounts['total_bans'],
        'total_vac': accounts['total_vac_bans'],
        'total_community': accounts['total_community_bans'],
        'total_game_ban': accounts['total_game_bans'],
        'bans_in_last_week': accounts['bans_last_week'],
        'items': 0,
        'cases': 0,
        'prices': 0
    })

    await redis_cache.setex(f'personal_statistics::{user_id}', 120, text)
    return text

from fluent.runtime import FluentLocalization

from bot.core.loader import redis_cache, redis_db
from bot.types.AccountInfo import AccountInfo
from bot.types.Inventory import Inventory
from bot.types.Statistic import Statistic


async def get_statistic(steam_ids: list[int] = None) -> Statistic:
    cursor = '0'
    steam_ids_set = set(steam_ids) if steam_ids else None
    statistics: Statistic = Statistic()

    while cursor != 0:
        cursor, keys = await redis_db.scan(cursor=cursor, count=30000, match='data::*')
        if keys:
            pipeline = redis_db.pipeline()
            for key in keys:
                steam_id = int(key.decode('utf-8').split("::")[1])
                if not steam_ids_set or steam_id in steam_ids_set:
                    pipeline.hgetall(key)

            results = await pipeline.execute()
            for result in results:
                account_info_json = result.get(b'ban', {})
                inventory_json = result.get(b'inventory', {})

                if account_info_json:
                    account_info = AccountInfo.from_json(account_info_json)
                    statistics.add_account_info(account_info)

                if inventory_json:
                    inventory = Inventory.from_json(inventory_json)
                    statistics.add_inventory_info(inventory)

    return statistics


async def get_general_statistics(l10n: FluentLocalization) -> str:
    cache = await redis_cache.get('accounts_statistics')
    if cache:
        return cache

    statistics = await get_statistic()
    print(statistics)
    text = l10n.format_value('general-accounts-info', {
        'accounts': statistics.total_accounts,
        'total_bans': statistics.total_bans,
        'total_vac': statistics.total_vac,
        'total_community': statistics.total_community,
        'total_game_ban': statistics.total_game_ban,
        'bans_in_last_week': statistics.bans_in_last_week,
        'items': statistics.items,
        'cases': statistics.cases,
        'prices': statistics.prices
    })

    await redis_cache.setex('accounts_statistics', 120, text)
    return text


async def get_personal_statistics(user_id: int, steam_ids: list[int], l10n: FluentLocalization) -> str:
    cache = await redis_cache.get(f'personal_statistics::{user_id}')
    if cache:
        return cache

    statistics = await get_statistic(steam_ids)
    text = l10n.format_value('personal-accounts-info', {
        'accounts': statistics.total_accounts,
        'total_bans': statistics.total_bans,
        'total_vac': statistics.total_vac,
        'total_community': statistics.total_community,
        'total_game_ban': statistics.total_game_ban,
        'bans_in_last_week': statistics.bans_in_last_week,
        'items': statistics.items,
        'cases': statistics.cases,
        'prices': statistics.prices
    })

    await redis_cache.setex(f'personal_statistics::{user_id}', 120, text)
    return text

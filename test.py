import asyncio
import time

from orjson import orjson

from bot.core.loader import redis_db
from bot.types.AccountInfo import AccountInfo
from bot.types.Inventory import Inventory
from bot.types.Item import Item
from bot.types.Statistic import Statistic


async def fetch_price_results(provider: str, mode: str) -> list[Item]:
    cursor = '0'
    prices_results = []
    redis_key = f'prices:{provider}' + (f':{mode}' if mode else '')

    while cursor != 0:
        cursor, fields = await redis_db.hscan(name=redis_key, cursor=cursor, count=30000)
        if fields:
            pipeline = redis_db.pipeline()
            for field in fields:
                pipeline.hget(redis_key, field)

            pipeline_provider_results = await pipeline.execute()
            for field, value in zip(fields.keys(), pipeline_provider_results):
                item = Item.from_json(field, value)
                prices_results.append(item)

    return prices_results

async def get_statistic(provider: str, mode: str = None, steam_ids: list[int] = None) -> Statistic:
    cursor = '0'
    steam_ids_set = set(steam_ids) if steam_ids else None
    statistics = Statistic()

    prices_results = await fetch_price_results(provider, mode)

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

                if account_info_json or inventory_json:
                    statistics.total_accounts += 1

                if account_info_json:
                    account_info = AccountInfo.from_json(account_info_json)
                    statistics.add_account_info(account_info)

                if inventory_json:
                    inventory = Inventory.from_json_and_prices(inventory_json, prices_results)
                    statistics.add_inventory_info(inventory)

    return statistics


async def main():
    statistics = await get_statistic(
        'steam',
        'last_24h',

    )

    print(f"Всего предметов: {statistics.items}")
    print(f"Всего кейсов: {statistics.cases}")
    print(f"Общая цена: {statistics.prices:.2f}$")
    print(f"Всего аккаунтов: {statistics.total_accounts}")
    print(f"Всего банов: {statistics.total_bans}")
    print(f"Всего VAC банов: {statistics.total_vac}")
    print(f"Всего коммьюнити банов: {statistics.total_community}")
    print(f"Всего игровых банов: {statistics.total_game_ban}")
    print(f"Баны за последнюю неделю: {statistics.bans_in_last_week}")

if __name__ == '__main__':
    asyncio.run(main())

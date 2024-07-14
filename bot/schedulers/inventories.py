from bot.core.loader import redis_db, config_json
from bot.database.db_requests import get_all_steamid64
from bot.services.steam_inventory.steam_inventory import SteamInventory


async def update_inventories():
    all_accounts = await get_all_steamid64()
    proxies = await config_json.get_config_value('proxies')

    steam_inventory = SteamInventory(proxies, redis_db)
    async with steam_inventory:
        await steam_inventory.process_inventories(all_accounts, is_update=True)

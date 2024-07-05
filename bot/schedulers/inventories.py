async def update_inventories():
    steam_inventory = SteamInventory(proxies, redis_db)
    async with steam_inventory:
        await steam_inventory.process_inventories(valid_steam_ids, is_update=True)
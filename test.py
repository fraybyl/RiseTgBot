import asyncio
import hashlib
import time
from typing import Optional

import aiohttp
import orjson
from loader import redis_db, logging, configJson, pool_db

semaphore = asyncio.Semaphore(1)

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
                        item_name, quantity = list
                        item_market = await redis_db.get(f"steam_market::{item_name}")
                        if isinstance(item_market, bytes):
                            price = orjson.loads(item_market.decode('utf-8')).get('price', 0)
                            total_elements += quantity
                            sum_price += price * quantity
                            if 'case' in item_name.lower():
                                filtered_items += quantity
    await pool_db.disconnect()
    return {
        'total_elements': total_elements,
        'sum_price': sum_price,
        'total_case': filtered_items
    }
            

steam_ids = [76561198965030463,
76561198986923662,
76561198069678468,
76561198855186239,
76561198007241107,
76561199121686454,
76561198136072517]
    
if __name__ == "__main__":
    print(asyncio.run(get_inventories_statistics()))
    

import asyncio
import time
import orjson
import redis.asyncio as redis

pool = redis.ConnectionPool.from_url("redis://127.0.0.1")
redis_db = redis.Redis.from_pool(pool)


async def get_accounts_statistics():
    total_vac_bans = 0
    total_community_bans = 0
    total_game_bans = 0
    bans_last_week = 0
    total_bans = 0
    total_accounts = 0
    tasks = []
    cursor = '0'
    while cursor != 0:
        cursor, keys = await redis_db.scan(cursor=cursor, count=500, match='player_bans:*')
        if keys:
            tasks.append(fetch_keys(redis_db, keys))
    
    # Собираем результаты
    results = await asyncio.gather(*tasks)
    for result in results:
        for value in result:
            for data_bytes in value:
                # Decode and parse each item in the value list
                data_str = data_bytes.decode('utf-8')
                data_list = orjson.loads(data_str)
                
                for data_dict in data_list:
                    total_accounts += 1
                    total_vac_bans += data_dict.get('VACBanned', 0)
                    total_game_bans += data_dict.get('NumberOfGameBans', 0)
                    total_community_bans += data_dict.get('CommunityBanned', 0)
                    last_ban = data_dict.get('DaysSinceLastBan', 0)
                    
                    if last_ban > 0:
                        total_bans += 1
                        if last_ban <= 7:
                            bans_last_week += 1
    await redis_db.aclose()
    print(total_bans, total_vac_bans, total_community_bans, total_game_bans, bans_last_week, total_accounts)
        
async def fetch_keys(client, keys):
    pipeline = client.pipeline()
    pipeline.mget(keys)
    return await pipeline.execute()
start = time.time()
asyncio.run(get_accounts_statistics())
print(time.time() - start)
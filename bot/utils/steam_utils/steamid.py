import asyncio
import hashlib
import re
import aiohttp
import orjson
from bot.database.db_requests import get_all_steamid64
from loader import configJson, redis_db, logging

# Precompiled patterns
url_pattern = re.compile(
    r'^(?P<clean_url>https?://steamcommunity\.com/(?P<type>profiles|id|gid|groups|user)/(?P<value>[^/?#]+))(/.*)?$'
)

profile_data_pattern = re.compile(r"g_rgProfileData = (?P<json>{.*?});\s*\n")
group_data_pattern = re.compile(r"OpenGroupChat\('(?P<steamid>\d+)'\)")



def is_valid_steamid64(steamid):
    return steamid.isdigit() and len(steamid) == 17 and int(steamid) >= 76561197960265728

async def fetch_page(session, url, http_timeout):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=http_timeout)) as response:
            if response.status == 200:
                return await response.text()
            return None
    except aiohttp.ClientError:
        return None

async def steam64_from_url(session, url, http_timeout=30, semaphore=None):
    if semaphore:
        async with semaphore:
            if is_valid_steamid64(url):
                return int(url)

            match = url_pattern.match(url)
            if not match:
                return None

            text = await fetch_page(session, match.group('clean_url'), http_timeout)
            if not text:
                return None

            if match.group('type') in ('id', 'profiles', 'user'):
                data_match = profile_data_pattern.search(text)
                if data_match:
                    data = orjson.loads(data_match.group('json'))
                    return int(data['steamid'])
            elif match.group('type') in ('gid', 'groups'):
                data_match = group_data_pattern.search(text)
                if data_match:
                    return int(data_match.group('steamid'))
            return None
    else:
        return None

async def steam_urls_parse(lines: list[str], concurrency_limit: int = 500) -> list[int]:
    semaphore = asyncio.Semaphore(concurrency_limit)
    connector = aiohttp.TCPConnector(limit_per_host=concurrency_limit, limit=concurrency_limit * 2)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [steam64_from_url(session, url, semaphore=semaphore) for url in lines if url.strip()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [result for result in results if isinstance(result, int)]
        
async def fetch_get_player_bans(session, url, semaphore, update = True):
    def generate_cache_key(url, temp=False):
        prefix = "ban_stat_temp" if temp else "ban_stat"
        return f"{prefix}::{hashlib.md5(url.encode()).hexdigest()}"

    cache_key_temp = generate_cache_key(url, temp=update)
    cache_key_final = generate_cache_key(url)

    async with semaphore:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()

                try:
                    await redis_db.set(cache_key_temp, orjson.dumps(data.get('players')))
                except Exception as e:
                    logging.error(f"Error setting temp cache for URL: {url}, {e}")

                return cache_key_temp, cache_key_final
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching URL: {url}, {e}")
            return None, None

async def get_player_bans(steam_ids: list[int], update = True, max_concurrent_requests=3):
    api_key = configJson.get_config_value('steam_web_api_key')
    semaphore = asyncio.Semaphore(max_concurrent_requests)
    tasks = []

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(steam_ids), 100):
            steam_ids_chunk = steam_ids[i:i + 100]
            url = (
                f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/'
                f'?key={api_key}&steamids={",".join(map(str, steam_ids_chunk))}'
            )

            task = fetch_get_player_bans(session, url, semaphore, update)
            tasks.append(task)

        temp_and_final_keys = await asyncio.gather(*tasks, return_exceptions=True)

    return temp_and_final_keys

async def add_new_accounts(steam_ids: list[int], semaphore: asyncio.Semaphore):
    async with semaphore:
        steam_ids_set = set(steam_ids)
        cursor = '0'
        try:
            while cursor != 0:
                cursor, keys = await redis_db.scan(cursor=cursor, count=30000, match='ban_stat::*')
                if keys:
                    pipeline = redis_db.pipeline()
                    pipeline.mget(*keys)
                    results = await pipeline.execute()
                    
                    for result in results:
                        if result:
                            try:
                                for bytes in result:
                                    data_str = bytes.decode('utf-8')
                                    data_list = orjson.loads(data_str)
                                    
                                    for data_dict in data_list:
                                        steam_id = int(data_dict.get('SteamId', 0))
                                        if steam_id in steam_ids_set:
                                            steam_ids_set.discard(steam_id)

                            except orjson.JSONDecodeError as e:
                                print(f"JSON decode error: {e}")
                            except Exception as e:
                                print(f"Unexpected error: {e}")
                            
        except Exception as e:
            print(f"Error during Redis scan or key fetching: {e}")
        if steam_ids_set:
            temp_and_final_keys = await get_player_bans(list(steam_ids_set), True)
            temp_keys = [pair[0] for pair in temp_and_final_keys if pair[0]]
            final_keys = [pair[1] for pair in temp_and_final_keys if pair[1]]
            
            pipeline = await redis_db.pipeline()
            await switch_keys(temp_keys, final_keys, pipeline)
            await pipeline.execute()

async def switch_keys(temp_keys, final_keys, pipe):
    for temp_key, final_key in zip(temp_keys, final_keys):
        if temp_key and final_key:
            await pipe.rename(temp_key, final_key)
            
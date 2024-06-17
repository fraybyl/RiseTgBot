import asyncio
import hashlib
import re
import aiohttp
import orjson
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
        
async def fetch_get_player_bans(session, url, semaphore):
    async with semaphore:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()

                try:
                    for player in data.get('players', []):
                        steam_id = player.get('SteamId')
                        del player['SteamId']
                        if steam_id:
                            await redis_db.set(f'ban_stat::{steam_id}', orjson.dumps(player))
                except Exception as e:
                    logging.error(f"Error setting cache for URL: {url}, {e}")

                return data
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching URL: {url}, {e}")
            return None

async def get_player_bans(steam_ids: list[int], max_concurrent_requests=1):
    api_key = await configJson.get_config_value('steam_web_api_key')
    semaphore = asyncio.Semaphore(max_concurrent_requests)
    tasks = []

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(steam_ids), 100):
            steam_ids_chunk = steam_ids[i:i + 100]
            url = (
                f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/'
                f'?key={api_key}&steamids={",".join(map(str, steam_ids_chunk))}'
            )

            task = fetch_get_player_bans(session, url, semaphore)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

    return results

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
        cursor, keys = await redis_db.scan(cursor=cursor, count=20000, match='ban_stat::*')
        if keys:
            tasks.append(fetch_keys(redis_db, keys))
    
    # Собираем результаты
    results = await asyncio.gather(*tasks)
    for account_list in results:
        for data_bytes in account_list:
            for data in data_bytes:
                # Извлекаем данные из байтов в строку
                data_str = data.decode('utf-8')
                # Преобразуем строку JSON в словарь
                data_dict = orjson.loads(data_str)

                total_accounts += 1
                total_vac_bans += data_dict.get('VACBanned', 0)
                total_game_bans += data_dict.get('NumberOfGameBans', 0)
                total_community_bans += data_dict.get('CommunityBanned', 0)
                last_ban = data_dict.get('DaysSinceLastBan', 0)
                
                if last_ban > 0:
                    total_bans += 1
                    if last_ban <= 7:
                        bans_last_week += 1

    return total_bans, total_vac_bans, total_community_bans, total_game_bans, bans_last_week, total_accounts
        
async def fetch_keys(client, keys):
    pipeline = client.pipeline()
    pipeline.mget(keys)
    return await pipeline.execute()
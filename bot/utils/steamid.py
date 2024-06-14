import asyncio
import logging
import re
import aiohttp
import orjson
from loader import configJson

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

async def steam_urls_parse(lines: list[str], concurrency_limit=500) -> list[int]:
    semaphore = asyncio.Semaphore(concurrency_limit)
    connector = aiohttp.TCPConnector(limit_per_host=concurrency_limit, limit=concurrency_limit * 2)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [steam64_from_url(session, url, semaphore=semaphore) for url in lines if url.strip()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [result for result in results if isinstance(result, int)]
    
async def fetch_GetPlayerBans(session, url, semaphore):
    try:
        async with semaphore:
            async with session.get(url) as response:
                response.raise_for_status()  # raise exception for non-200 responses
                return await response.read()  # Use .read() to get bytes response
    except aiohttp.ClientError as e:
        logging.error(f"Error fetching URL: {url}, {e}")
        return None

async def get_player_bans(steam_ids: list[int], api_key, cache):
    semaphore = asyncio.Semaphore(10)
    tasks = []

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(steam_ids), 100):
            steam_ids_chunk = steam_ids[i:i + 100]
            url = f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={api_key}&steamids={steam_ids_chunk}'

            # Check if data exists in cache
            cache_key = f"player_bans:{','.join(map(str, steam_ids_chunk))}"
            cached_data = await cache.get(cache_key)

            if cached_data:
                tasks.append(orjson.loads(cached_data))
            else:
                # Fetch data from API
                data = await fetch_GetPlayerBans(session, url, semaphore)
                if data:
                    decoded_data = orjson.loads(data)
                    tasks.append(decoded_data)
                    # Cache data for 1 hour (3600 seconds)
                    await cache.set(cache_key, orjson.dumps(decoded_data), expire=3600)

    results = await asyncio.gather(*tasks)
    return results

async def get_table(steam_ids: list[int]):
    STEAM_API_KEY = await configJson.get_config_value('steam_web_api_key')
    total_bans = 0
    vac_bans = 0
    community_bans = 0
    game_bans = 0
    bans_in_last_week = 0
    total_accounts = 0

    results = await get_player_bans(steam_ids, STEAM_API_KEY, ban_check_db)
    
    for result in results:
        if result and 'players' in result:
            for player in result['players']:
                total_accounts += 1
                if player.get('NumberOfVACBans', 0) > 0 or player.get('CommunityBanned', False) or player.get('NumberOfGameBans', 0) > 0:
                    total_bans += 1
                    vac_bans += player.get('NumberOfVACBans', 0)
                    community_bans += player.get('CommunityBanned', False)
                    game_bans += player.get('NumberOfGameBans', 0)
                    
                    if player.get('DaysSinceLastBan', 0) <= 7:
                        bans_in_last_week += 1

    # Print or return aggregated statistics
    print(f"Total Bans: {total_accounts}")
    print(f"Total Bans: {total_bans}")
    print(f"Total VAC Bans: {vac_bans}")
    print(f"Total Community Bans: {community_bans}")
    print(f"Total Game Bans: {game_bans}")
    print(f"Bans in Last 7 Days: {bans_in_last_week}")
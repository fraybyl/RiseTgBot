import asyncio
import hashlib
import json
import logging
import re
import aiohttp
import orjson
from bot.database.redis_db import RedisCache
from loader import configJson, redis_ban_check

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
    
async def fetch_get_player_bans(session, url, semaphore, cache, expire=3600):
    def generate_cache_key(url):
        return f"player_bans:{hashlib.md5(url.encode()).hexdigest()}"
    
    cache_key = generate_cache_key(url)
    try:
        cached_response = await cache.get(cache_key)
        if cached_response:
            return orjson.loads(cached_response)  
    except Exception as e:
        logging.error(f"Error accessing cache for URL: {url}, {e}")

    try:
        async with semaphore:
            async with session.get(url) as response:
                response.raise_for_status()  
                data = await response.json()

                try:
                    await cache.set(cache_key, orjson.dumps(data), expire)
                except Exception as e:
                    logging.error(f"Error setting cache for URL: {url}, {e}")

                return data
    except aiohttp.ClientError as e:
        logging.error(f"Error fetching URL: {url}, {e}")
        return None


async def get_player_bans(steam_ids: list[int], api_key, cache: RedisCache):
    """получает информацию по бану пользователей
    

    Args:
        steam_ids (list[int]): принимает лист steam_ids
        api_key (_type_): апи ключ. в configjson
        cache (RedisCache): передать экземпляр RedisCache

    Returns:
        _type_: Выдает json формата players->{SteamId, CommunityBanned, VACBanned, NumberOfVACBans, DaysSinceLastBan, NumberOfGameBans, EconomyBan}
    """
    
    semaphore = asyncio.Semaphore(10)
    tasks = []

    await cache.connect()
    try:
        async with aiohttp.ClientSession() as session:
            for i in range(0, len(steam_ids), 100):
                steam_ids_chunk = steam_ids[i:i + 100]
                url = (
                    f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/'
                    f'?key={api_key}&steamids={",".join(map(str, steam_ids_chunk))}'
                )

                task = fetch_get_player_bans(session, url, semaphore, cache)
                tasks.append(task)

            results = await asyncio.gather(*tasks)
    finally:
        await cache.close()

    return results

async def get_accounts_statistics(steam_ids: list[int]):
    STEAM_API_KEY = await configJson.get_config_value('steam_web_api_key')

    results = await get_player_bans(steam_ids, STEAM_API_KEY, redis_ban_check)
    
    for result in results:
        players = result['players']  # Получаем игроков из текущего результата
        total_vac_bans = sum(1 for player in players if player['VACBanned'])
        total_community_bans = sum(1 for player in players if player['CommunityBanned'])
        total_game_bans = sum(player['NumberOfGameBans'] for player in players)
        bans_last_week = sum(1 for player in players if player['DaysSinceLastBan'] <= 7 and player['DaysSinceLastBan'] > 0)

        # Общее количество забаненных аккаунтов
        total_bans = total_vac_bans + total_community_bans + total_game_bans
        
        return total_bans, total_vac_bans, total_community_bans, total_game_bans, bans_last_week
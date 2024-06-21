# Precompiled patterns
import asyncio
import re

import aiohttp
from orjson import orjson

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

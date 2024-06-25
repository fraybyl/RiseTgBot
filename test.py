import asyncio
import re
import time
import aiohttp
from loguru import logger
from orjson import orjson

url_pattern = re.compile(
    r'^(?P<clean_url>https?://steamcommunity\.com/(?P<type>id|user)/(?P<value>[^/?#]+))(/.*)?$'
)

profile_data_pattern = re.compile(r"g_rgProfileData\s*=\s*(?P<json>{.*?});\s*\n")
profile_url_pattern = re.compile(r"https://steamcommunity\.com/profiles/(?P<value>\d+)")


def is_valid_steamid64(steamid: str) -> bool:
    return steamid.isdigit() and len(steamid) == 17 and int(steamid) >= 0x0110000100000000

async def fetch_page(session: aiohttp.ClientSession, url: str) -> str | None:
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            return None
    except aiohttp.ClientError as e:
        logger.error(f'Ошибка в парсе steamid -> url {url}: {e}')
        return None

async def steam64_from_url(session: aiohttp.ClientSession, url: str) -> int | None:
    if is_valid_steamid64(url):
        return int(url)

    profile_match = profile_url_pattern.match(url)
    if profile_match:
        if is_valid_steamid64(profile_match.group('value')):
            return int(profile_match.group('value'))

    match = url_pattern.match(url)

    if not match:
        return None

    text = await fetch_page(session, match.group('clean_url'))

    if not text:
        return None

    try:
        if match.group('type') in ('id', 'profiles', 'user'):
            data_match = profile_data_pattern.search(text)
            if data_match:
                data = orjson.loads(data_match.group('json'))
                return int(data['steamid'])
    except Exception as e:
        logger.error(f'Ошибка при обработке данных из url {url}: {e}')
    return None

async def steam_urls_parse(urls: list[str], max_concurrent_requests: int = 500) -> list[int]:
    headers = {'Accept-Encoding': 'gzip, deflate, br'}
    connector = aiohttp.TCPConnector(limit=max_concurrent_requests)
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks = [steam64_from_url(session, url.strip()) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [result for result in results if isinstance(result, int)]

async def test_max_concurrent_requests(urls: list[str], test_values: list[int]) -> dict[int, float]:
    results = {}
    for value in test_values:
        start_time = time.time()
        await steam_urls_parse(urls, value)
        end_time = time.time()
        results[value] = end_time - start_time
        print(f"Для {value} параллельных запросов время выполнения: {results[value]:.2f} секунд")
    return results

def load_urls_from_file(file_path: str) -> list[str]:
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

urls = load_urls_from_file('sdfds.txt')

test_values = [200, 300, 400, 500, 1000]

asyncio.run(test_max_concurrent_requests(urls, test_values))

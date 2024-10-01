# Precompiled patterns
import asyncio
import re

import aiohttp
from loguru import logger
from orjson import orjson

url_pattern = re.compile(
    r'^(?P<clean_url>https?://steamcommunity\.com/(?P<type>id|user)/(?P<value>[^/?#]+))(/.*)?$'
)

profile_data_pattern = re.compile(r"g_rgProfileData\s*=\s*(?P<json>{.*?});\s*\n")
profile_url_pattern = re.compile(r"https://steamcommunity\.com/profiles/(?P<value>\d+)")


def is_valid_steamid64(steamid: str) -> bool:
    """
    Проверяет, является ли указанный SteamID64 действительным.

    Аргументы:
    - steamid (str): SteamID64 для проверки.

    Возвращает:
    - bool: True, если SteamID64 является действительным, иначе False.
    """
    return steamid.isdigit() and len(steamid) == 17 and int(steamid) >= 0x0110000100000000


async def fetch_page(session: aiohttp.ClientSession, url: str) -> str | None:
    """
    Асинхронно загружает содержимое веб-страницы по указанному URL.

    Аргументы:
    - session (aiohttp.ClientSession): Сессия клиента aiohttp для отправки запроса.
    - url (str): URL веб-страницы для загрузки.

    Возвращает:
    - str | None: Текст содержимого веб-страницы или None, если возникла ошибка при запросе.
    """
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            return None
    except aiohttp.ClientError as e:
        logger.error(f'Ошибка в парсе steamid -> url {url}: {e}')
        return None


async def steam64_from_url(session: aiohttp.ClientSession, url: str) -> int | None:
    """
    Асинхронно извлекает SteamID64 из указанного URL Steam Community.

    Аргументы:
    - session (aiohttp.ClientSession): Сессия клиента aiohttp для отправки запроса.
    - url (str): URL Steam Community для извлечения SteamID64.

    Возвращает:
    - int | None: SteamID64 пользователя или None, если не удалось извлечь или обработать данные.
    """
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
    """
    Асинхронно парсит список URL Steam Community и извлекает SteamID64 из каждого URL.

    Аргументы:
    - urls (list[str]): Список URL Steam Community для парсинга.
    - max_concurrent_requests (int, optional): Максимальное количество параллельных запросов. По умолчанию 500.

    Возвращает:
    - list[int]: Список SteamID64 пользователей, извлеченных из URL.
    """
    headers = {'Accept-Encoding': 'br'}
    connector = aiohttp.TCPConnector(limit=max_concurrent_requests)
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks = [steam64_from_url(session, url.strip()) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [result for result in results if isinstance(result, int)]

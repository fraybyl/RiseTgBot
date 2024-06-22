import asyncio

from aiogram.types import BufferedInputFile


def convert_steamid_to_link(steam_id: int) -> str:
    return f"https://steamcommunity.com/profiles/{steam_id}"


async def process_bytes(steam_ids: list[int]) -> bytes:
    links = [convert_steamid_to_link(steam_id) for steam_id in steam_ids]
    steam_ids_str = '\n'.join(links) + '\n'
    return steam_ids_str.encode('utf-8')


async def dump_accounts(steam_ids: list[int], chunk_size: int = 1000) -> BufferedInputFile:
    chunks = [steam_ids[i:i + chunk_size] for i in range(0, len(steam_ids), chunk_size)]

    tasks = [process_bytes(chunk) for chunk in chunks]

    results = await asyncio.gather(*tasks)

    steam_id_to_dump = b"".join(results)
    return BufferedInputFile(steam_id_to_dump, 'accounts_dump.txt')

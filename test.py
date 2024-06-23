import asyncio
import aiofiles
import aiohttp
import ua_generator


async def fetch_accounts(session, page):
    url = 'https://vaclist.net/api/banned'
    headers = ua_generator.generate().headers.get()
    params = {
        'count': '60',
        'page': page,
    }
    async with session.get(url, headers=headers, params=params) as response:
        response.raise_for_status()
        data = await response.json()
        return data


async def get_and_write_accounts(session, page):
    print('Fetching %d' % page)
    data = await fetch_accounts(session, page)
    profile_urls = [account['profile_url'] for account in data]
    return profile_urls


async def write_to_file(profile_urls, file):
    async with aiofiles.open(file, 'a', encoding='utf-8') as f:
        for url in profile_urls:
            await f.write(url + '\n')


async def get_accounts():
    async with aiohttp.ClientSession() as session:
        file = 'profile_urls.txt'
        page = 600
        while True:
            tasks = [get_and_write_accounts(session, page + i) for i in range(50)]
            results = await asyncio.gather(*tasks)
            flattened_urls = [url for sublist in results for url in sublist]
            await write_to_file(flattened_urls, file)
            if all(len(result) < 60 for result in results):
                break
            page += 50


if __name__ == '__main__':
    asyncio.run(get_accounts())

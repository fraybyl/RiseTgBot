from bot.utils.steam_utils.parser.market_parser import SteamMarketParser
from loader import configJson, logging

async def market_schedule() -> bool:
    logging.info('Обновление цен торговой площадки...')
    proxies = await configJson.get_config_value('proxies')
    market = SteamMarketParser(proxies)
    await market.fetch_all_pages()
    logging.info('Обновление цен торговой площадки завершена')
    
    
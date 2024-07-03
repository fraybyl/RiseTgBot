import time

from fluent.runtime import FluentLocalization

from bot.core.loader import redis_db
from bot.decorators.dec_cache import cached, build_key
from bot.types.AccountInfo import AccountInfo
from bot.types.Inventory import Inventory
from bot.types.Item import Item
from bot.types.Statistic import Statistic


async def fetch_price_results(provider: str, mode: str, currency: str) -> list[Item]:
    """
    Асинхронно извлекает результаты цен для предметов из Redis по провайдеру цен, преобразует в валюту и возвращает список объектов Item.

    Args:
        provider (str): Провайдер, данные которого требуется извлечь.
        mode (str, optional): Режим провайдера, если применим (по умолчанию None).
        currency (str): Валюта для конвертации цен.

    Returns:
        list[Item]: Список объектов Item, представляющих результаты цен.

    Raises:
        TypeError: Если cursor не является строкой.
    """
    cursor = '0'
    prices_results = []
    redis_key = f'prices:{provider}' + (f':{mode}' if mode else '')
    currency_ratio = float((await redis_db.hget('exchangeRates', currency)).decode('utf-8'))
    while cursor != 0:
        cursor, fields = await redis_db.hscan(name=redis_key, cursor=cursor, count=30000)
        if fields:
            pipeline = redis_db.pipeline()
            for field in fields:
                pipeline.hget(redis_key, field)

            pipeline_provider_results = await pipeline.execute()
            for field, value in zip(fields.keys(), pipeline_provider_results):
                item = Item.from_json(field, value, currency_ratio)
                prices_results.append(item)

    return prices_results


async def get_statistic(provider: str, mode: str = None, steam_ids: list[int] = None) -> Statistic:
    """
    Асинхронно считает статистику либо по всем аккаунтам либо по определенным.

    Args:
        provider (str): Провайдер, для которого требуется извлечь статистику.
        mode (str, optional): Режим провайдера, если применим (по умолчанию None).
        steam_ids (list[int], optional): Список steam_id для фильтрации статистики (по умолчанию None).

    Returns:
        Statistic: Объект Statistic, содержащий собранную статистику.

    Raises:
        TypeError: Если cursor не является строкой.
    """
    cursor = '0'
    steam_ids_set = set(steam_ids) if steam_ids else None
    statistics = Statistic()

    prices_results = await fetch_price_results(provider, mode, 'RUB')

    while cursor != 0:
        cursor, keys = await redis_db.scan(cursor=cursor, count=30000, match='data::*')
        if keys:
            pipeline = redis_db.pipeline()
            for key in keys:
                steam_id = int(key.decode('utf-8').split("::")[1])
                if not steam_ids_set or steam_id in steam_ids_set:
                    pipeline.hgetall(key)

            results = await pipeline.execute()
            for result in results:
                account_info_json = result.get(b'ban', {})
                inventory_json = result.get(b'inventory', {})

                if account_info_json or inventory_json:
                    statistics.total_accounts += 1

                if account_info_json:
                    account_info = AccountInfo.from_json(account_info_json)
                    statistics.add_account_info(account_info)

                if inventory_json:
                    inventory = Inventory.from_json_and_prices(inventory_json, prices_results)
                    statistics.add_inventory_info(inventory)
    return statistics


@cached(key_builder=lambda *args, **kwargs: "")
async def get_general_statistics(l10n: FluentLocalization, provider: str, mode: str = None) -> str:
    """
    Асинхронно получает общую статистику на основе локализации и провайдера для указанного режима.

    Args:
        l10n (FluentLocalization): Объект локализации для форматирования текста.
        provider (str): Провайдер, с которого смотреть цены.
        mode (str, optional): Режим провайдера, если применим (по умолчанию None).

    Returns:
        str: Текст общей статистики в формате, согласованном с локализацией.
    """
    statistics = await get_statistic(provider=provider, mode=mode)
    text = l10n.format_value('general-accounts-info', {
        'accounts': statistics.total_accounts,
        'total_bans': statistics.total_bans,
        'total_vac': statistics.total_vac,
        'total_community': statistics.total_community,
        'total_game_ban': statistics.total_game_ban,
        'bans_in_last_week': statistics.bans_in_last_week,
        'items': statistics.items,
        'cases': statistics.cases,
        'prices': statistics.prices
    })

    return text


@cached(key_builder=lambda user_id, *args, **kwargs: build_key(user_id))
async def get_personal_statistics(user_id: int, steam_ids: list[int], l10n: FluentLocalization, provider: str,
                                  mode: str = None) -> str:
    """
    Асинхронно получает персональную статистику для указанного пользователя на основе локализации, списка steam_ids и провайдера для указанного режима.

    Args:
        user_id (int): ID пользователя, под которым сохранить кеш.
        steam_ids (list[int]): Список steam_id по которым делать статистику.
        l10n (FluentLocalization): Объект локализации для форматирования текста.
        provider (str): Провайдер, с которого смотреть цены.
        mode (str, optional): Режим провайдера, если применим (по умолчанию None).

    Returns:
        str: Текст персональной статистики в формате, согласованном с локализацией.
    """
    statistics = await get_statistic(provider=provider, mode=mode, steam_ids=steam_ids)
    text = l10n.format_value('personal-accounts-info', {
        'accounts': statistics.total_accounts,
        'total_bans': statistics.total_bans,
        'total_vac': statistics.total_vac,
        'total_community': statistics.total_community,
        'total_game_ban': statistics.total_game_ban,
        'bans_in_last_week': statistics.bans_in_last_week,
        'items': statistics.items,
        'cases': statistics.cases,
        'prices': statistics.prices
    })

    return text

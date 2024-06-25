import asyncio

from aiogram.utils.callback_answer import CallbackAnswerMiddleware

import bot.utils.logging
from loguru import logger

from bot.core.loader import bot, dp, redis_db, redis_cache
from bot.database.database import start_db_postgres, close_db_postgres, engine
from bot.handlers import router as main_router
from bot.l10n.fluent_localization import get_fluent_localization
from bot.middlewares.l10n import L10nMiddleware
from bot.middlewares.valid_answer import ValidateQuantityMiddleware
from bot.schedulers.schedule import start_schedulers


async def on_startup() -> None:
    logger.info('Bot starting...')
    await start_db_postgres()
    locale = get_fluent_localization()

    dp.message.outer_middleware(L10nMiddleware(locale))
    dp.callback_query.outer_middleware(L10nMiddleware(locale))
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    dp.include_router(main_router)

    start_schedulers()


async def redis_shutdown() -> None:
    await redis_db.connection_pool.aclose()
    await redis_cache.connection_pool.aclose()
    await redis_db.aclose()
    await redis_cache.aclose()


async def on_shutdown() -> None:
    logger.info('Bot shutdown...')
    await dp.storage.close()
    await dp.fsm.storage.close()

    await redis_shutdown()
    await close_db_postgres(engine)


async def main() -> None:
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Exit bot')

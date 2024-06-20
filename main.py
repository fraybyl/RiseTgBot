import asyncio
from aiogram import Dispatcher
from loader import bot, dp, redis_db, redis_cache, pool_db, pool_cache , logging
from bot.middlewares.localization import L10nMiddleware
from bot.database.models import start_db_postegre
from bot.l10n.fluent_localization import get_fluent_localization
from bot.scheduled.ban_stat import ban_stat_schedule
from bot.scheduled.market_parse import market_schedule
from bot.handlers import router as main_router

async def on_startup():
    await start_db_postegre()
    await redis_db.ping()
    await redis_cache.ping()
    locale = get_fluent_localization()
    dp.message.outer_middleware(L10nMiddleware(locale)) 
    dp.callback_query.outer_middleware(L10nMiddleware(locale))
    dp.pre_checkout_query.outer_middleware(L10nMiddleware(locale))

    #asyncio.create_task(ban_stat_schedule())
    #asyncio.create_task(market_schedule())
    
async def on_shutdown():
    await redis_db.aclose()
    await redis_cache.aclose()
    await pool_db.disconnect()
    await pool_cache.disconnect()

async def main() -> None:
    dp.include_router(main_router)
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
   

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Exit bot')
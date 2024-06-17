import asyncio
from aiogram import Dispatcher
from loader import bot, dp, redis_db, redis_cache
from bot.middlewares.localization import L10nMiddleware
from bot.handlers import start_handlers, shop_handlers, personal_handlers, farmers_handlers, strategy_handlers, product_handlers, buy_handlers, inventory_handlers
from bot.database.models import start_db_postegre
from bot.l10n.fluent_localization import get_fluent_localization
from bot.scheduled.ban_stat import ban_stat

def register_routers(dp: Dispatcher):
    dp.include_router(start_handlers.router)
    dp.include_router(shop_handlers.router)
    dp.include_router(personal_handlers.router)
    dp.include_router(farmers_handlers.router)
    dp.include_router(strategy_handlers.router)
    dp.include_router(product_handlers.router)
    dp.include_router(buy_handlers.router)
    dp.include_router(inventory_handlers.router)

async def on_startup():
    await start_db_postegre()
    await redis_db.ping()
    await redis_cache.ping()
    locale = get_fluent_localization()
    dp.message.outer_middleware(L10nMiddleware(locale)) 
    dp.callback_query.outer_middleware(L10nMiddleware(locale))
    dp.pre_checkout_query.outer_middleware(L10nMiddleware(locale))
    
    register_routers(dp)

    #asyncio.create_task(ban_stat())
    
async def on_shutdown():
    await redis_db.aclose()


async def main() -> None:

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
   

if __name__ == "__main__":
    asyncio.run(main())
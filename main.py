import asyncio
from aiogram import Dispatcher
from loader import bot, dp
from bot.middlewares.localization import L10nMiddleware
from bot.handlers import start_handlers, shop_handlers, personal_handlers, farmers_handlers, strategy_handlers, product_handlers, buy_handlers, inventory_handlers
from bot.database.models import async_main
from bot.l10n.fluent_localization import get_fluent_localization

def register_routers(dp: Dispatcher):
    dp.include_router(start_handlers.router)
    dp.include_router(shop_handlers.router)
    dp.include_router(personal_handlers.router)
    dp.include_router(farmers_handlers.router)
    dp.include_router(strategy_handlers.router)
    dp.include_router(product_handlers.router)
    dp.include_router(buy_handlers.router)
    dp.include_router(inventory_handlers.router)

async def main() -> None:
    await async_main()
    locale = get_fluent_localization()
    dp.message.outer_middleware(L10nMiddleware(locale))
    dp.callback_query.outer_middleware(L10nMiddleware(locale))
    dp.pre_checkout_query.outer_middleware(L10nMiddleware(locale))
    
    register_routers(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
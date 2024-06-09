import asyncio
from aiogram import Dispatcher
from bot.handlers import start_handlers, shop_handlers, farmers_handlers, personal_handlers, strategy_handlers, steam_gift_code_handlers, steam_limit_accounts_handlers, buy_handlers
from loader import bot, dp
from bot.database.models import async_main


def register_routers(dp: Dispatcher):
    dp.include_router(start_handlers.router)
    dp.include_router(shop_handlers.router)
    dp.include_router(farmers_handlers.router)
    dp.include_router(personal_handlers.router)
    dp.include_router(strategy_handlers.router)
    dp.include_router(steam_gift_code_handlers.router)
    dp.include_router(steam_limit_accounts_handlers.router)
    dp.include_router(buy_handlers.router)
    
async def main() -> None:
    await async_main()
    register_routers(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
## ЕСЛИ БУДЕШЬ ПЕРЕДЕЛЫВАТЬ БД ТО ГЕНЕРИРУЙ РЕФЕРАЛКУ ПО TELEGRAM_ID ПЖ!! ПРОСТО ЗАКОДИРУЙ ЕЁ В BASE64 И ВСЁ!!!!!!!!!!!!!!!!!

if __name__ == "__main__":
    asyncio.run(main())
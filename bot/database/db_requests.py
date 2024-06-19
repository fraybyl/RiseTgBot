from sqlalchemy.future import select
from bot.database.models import async_session, User, Product, Category, SteamAccount
from loader import configJson, redis_cache
from decimal import Decimal

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def set_user(telegram_id: int, username: str = None, referral_code: str = None) -> User:
    """Sets or retrieves a user based on telegram_id, with optional referral code for bonuses."""
    async with async_session() as session:
        try:
            user = await session.scalar(select(User).where(User.telegram_id == telegram_id))

            if not user:
                referred_by = None
                if referral_code:
                    try:
                        referrer_id = int(referral_code)
                        referrer = await session.scalar(select(User).where(User.telegram_id == referrer_id))
                        if referrer:
                            referred_by = referrer.telegram_id
                        else:
                            logger.info(f"Referral code {referral_code} does not exist")
                    except ValueError:
                        logger.info(f"Invalid referral code: {referral_code}")

                user = User(telegram_id=telegram_id, username=username, referred_by=referred_by)
                session.add(user)
                if referred_by:
                    bonus_points = configJson.get_config_value('referral_bonus')
                    if bonus_points > 0:
                        referrer.bonus_points += Decimal(bonus_points)
                        session.add(referrer)

                await session.commit()
            return user
        except Exception as e:
            logger.error(f"Error in set_user: {e}")
            await session.rollback()
            raise

async def get_user_by_telegram_id(telegram_id: int) -> User:
    """Retrieves a user by their telegram_id."""
    async with async_session() as session:
        try:
            user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
            return user
        except Exception as e:
            logger.error(f"Error in get_user_by_telegram_id: {e}")
            raise

async def get_product_by_name(product_name: str) -> Product:
    """Retrieves a product by its name."""
    async with async_session() as session:
        try:
            product = await session.scalar(select(Product).where(Product.name == product_name))
            return product
        except Exception as e:
            logger.error(f"Error in get_product_by_name: {e}")
            raise

async def get_all_categories() -> list[Category]:
    """Retrieves all categories."""
    async with async_session() as session:
        try:
            result = await session.scalars(select(Category))
            categories = result.all()
            return categories
        except Exception as e:
            logger.error(f"Error in get_all_categories: {e}")
            raise

async def get_category_by_id(category_id: int) -> Category:
    """Retrieves a category by its ID."""
    async with async_session() as session:
        try:
            category = await session.scalar(select(Category).where(Category.id == category_id))
            return category
        except Exception as e:
            logger.error(f"Error in get_category_by_id: {e}")
            raise

async def get_products_by_category(category_id: int) -> list[Product]:
    """Retrieves products by category ID."""
    async with async_session() as session:
        try:
            products = await session.scalars(select(Product).where(Product.category_id == category_id))
            products_list = products.all()
            return products_list
        except Exception as e:
            logger.error(f"Error in get_products_by_category: {e}")
            raise

async def get_product_by_id(product_id: int) -> Product:
    """Retrieves a product by its ID."""
    async with async_session() as session:
        try:
            product = await session.scalar(select(Product).where(Product.id == product_id))
            return product
        except Exception as e:
            logger.error(f"Error in get_product_by_id: {e}")
            raise

async def get_steamid64_by_userid(user_id: int) -> list[int]:
    """Retrieves Steam URLs by user ID."""
    cached_result = await redis_cache.get(f"steamid64::{user_id}")
    if cached_result:
        return [int(id) for id in cached_result.decode().split(',')]
    
    async with async_session() as session:
        try:
            result = await session.execute(select(SteamAccount.steamid64).where(SteamAccount.user_id == user_id))
            steam_accounts = result.scalars().all()
            steamid64_list = [acc for acc in steam_accounts]
            
            # Store in Redis for future use with 1-hour expiry (adjust as needed)
            await redis_cache.set(f"steamid64::{user_id}", ','.join(map(str, steamid64_list)))
            
            return steamid64_list
        except Exception as e:
            logger.error(f"Error in get_steamid64_by_userid: {e}")
            raise
    
async def get_all_steamid64() -> list[int]:
    """Retrieves all Steam URLs."""
    async with async_session() as session:
        try:
            result = await session.execute(select(SteamAccount.steamid64).distinct())
            steam_accounts = result.scalars().all()
            return steam_accounts
        except Exception as e:
            logger.error(f"Error in get_all_steamid64: {e}")
            raise

async def set_steamid64_for_user(user_id: int, steamid64: list[int]) -> bool:
    """Sets Steam URLs for a user, avoiding duplicates."""
    async with async_session() as session:
        try:
            # Выполнение запроса на получение steamid64 для указанного user_id
            existing_accounts_result = await session.execute(
                select(SteamAccount.steamid64).where(SteamAccount.user_id == user_id)
            )
            
            # Преобразование результатов в набор steamid64
            existing_steam_urls = set(row[0] for row in existing_accounts_result.all())

            # Отфильтровать новые аккаунты, которые уже существуют в базе данных
            new_steam_accounts = [acc for acc in steamid64 if acc not in existing_steam_urls]

            # Если нет новых аккаунтов для добавления, возвращаем True
            if not new_steam_accounts:
                return True

            # Создание объектов SteamAccount для новых аккаунтов
            new_steam_account_objects = [
                SteamAccount(steamid64=steamid64, user_id=user_id) for steamid64 in new_steam_accounts
            ]
            session.add_all(new_steam_account_objects)

            # Коммит транзакции
            await session.commit()
            await redis_cache.delete(f"steamid64::{user_id}")
            return True
        except Exception as e:
            # Логирование ошибки и откат транзакции в случае исключения
            logger.error(f"Error in set_steamid64_for_user: {e}")
            await session.rollback()
            raise



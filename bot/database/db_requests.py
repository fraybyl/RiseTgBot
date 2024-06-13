from sqlalchemy import Integer, cast
from sqlalchemy.future import select
from bot.database.models import async_session, User, Product, Category, SteamAccount
from loader import configJson
from decimal import Decimal

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def set_user(telegram_id: int, username: str = None, referral_code: str = None) -> User:
    """Sets or retrieves a user based on telegram_id, with optional referral code for bonuses."""
    async with async_session() as session:
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
                bonus_points = await configJson.get_config_value('referral_bonus')
                if bonus_points > 0:
                    referrer.bonus_points += Decimal(bonus_points)
                    session.add(referrer)

            await session.commit()
        return user

async def get_user_by_telegram_id(telegram_id: int) -> User:
    """Retrieves a user by their telegram_id."""
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        return user

async def get_product_by_name(product_name: str) -> Product:
    """Retrieves a product by its name."""
    async with async_session() as session:
        product = await session.scalar(select(Product).where(Product.name == product_name))
        return product

async def get_all_categories() -> list[Category]:
    """Retrieves all categories."""
    async with async_session() as session:
        result = await session.scalars(select(Category))
        categories = result.all()
        return categories

async def get_category_by_id(category_id: int) -> Category:
    """Retrieves a category by its ID."""
    async with async_session() as session:
        category = await session.scalar(select(Category).where(Category.id == category_id))
        return category

async def get_products_by_category(category_id: int) -> list[Product]:
    """Retrieves products by category ID."""
    async with async_session() as session:
        products = await session.scalars(select(Product).where(Product.category_id == category_id))
        products_list = products.all()
        return products_list

async def get_product_by_id(product_id: int) -> Product:
    """Retrieves a product by its ID."""
    async with async_session() as session:
        product = await session.scalar(select(Product).where(Product.id == product_id))
        return product

async def get_steam_urls_by_userid(user_id: int) -> list[int]:
    """Retrieves Steam URLs"""
    async with async_session() as session:
        result = await session.execute(select(SteamAccount.steam_url).where(SteamAccount.user_id == user_id))
        steam_accounts = result.scalars().all()
        return steam_accounts
    
async def get_all_steam_urls() -> list[int]:
    """Retrieves Steam URLs associated with a user ID."""
    async with async_session() as session:
        result = await session.execute(select(SteamAccount.steam_url))
        steam_accounts = result.scalars().all()
        return steam_accounts

async def set_steam_urls_for_user(user_id: int, steam_accounts: list[int]) -> bool:
    """Sets Steam URLs for a user, avoiding duplicates."""
    async with async_session() as session:
        existing_accounts_result = await session.execute(
            select(SteamAccount.steam_url).where(SteamAccount.user_id == user_id)
        )
        existing_steam_urls = set(existing_accounts_result.scalars().all())

        new_steam_accounts = [acc for acc in steam_accounts if acc not in existing_steam_urls]

        if not new_steam_accounts:
            return True

        new_steam_account_objects = [
            SteamAccount(steam_url=steam_url, user_id=user_id) for steam_url in new_steam_accounts
        ]
        session.add_all(new_steam_account_objects)

        await session.commit()
        return True
                
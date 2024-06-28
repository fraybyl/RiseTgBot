from decimal import Decimal

from loguru import logger
from sqlalchemy import delete as sql_delete
from sqlalchemy.future import select

from bot.core.loader import config_json
from bot.database.database import async_session
from bot.database.models import User, Product, Category, SteamAccount
from bot.decorators.dec_cache import cached, build_key, clear_cache


async def set_user(telegram_id: int, username: str = None, referral_code: str = None) -> User:
    """Sets or retrieves a user based on telegram_id, with optional referral code for bonuses."""
    async with async_session() as session:
        try:
            user = await session.scalar(select(User).where(telegram_id == User.telegram_id))

            if not user:
                referred_by = None
                if referral_code:
                    try:
                        referrer_id = int(referral_code)
                        referrer = await session.scalar(select(User).where(referrer_id == User.telegram_id))
                        if referrer:
                            referred_by = referrer.telegram_id
                        else:
                            logger.info(f"Referral code {referral_code} does not exist")
                    except ValueError:
                        logger.info(f"Invalid referral code: {referral_code}")

                user = User(telegram_id=telegram_id, username=username, referred_by=referred_by)
                session.add(user)
                if referred_by:
                    bonus_points = await config_json.get_config_value('referral_bonus')
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
            user = await session.scalar(select(User).where(telegram_id == User.telegram_id))
            return user
        except Exception as e:
            logger.error(f"Error in get_user_by_telegram_id: {e}")
            raise


async def get_product_by_name(product_name: str) -> Product:
    """Retrieves a product by its name."""
    async with async_session() as session:
        try:
            product = await session.scalar(select(Product).where(product_name == Product.name))
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
            category = await session.scalar(select(Category).where(category_id == Category.id))
            return category
        except Exception as e:
            logger.error(f"Error in get_category_by_id: {e}")
            raise


async def get_products_by_category(category_id: int) -> list[Product]:
    """Retrieves products by category ID."""
    async with async_session() as session:
        try:
            products = await session.scalars(select(Product).where(category_id == Product.category_id))
            products_list = products.all()
            return products_list
        except Exception as e:
            logger.error(f"Error in get_products_by_category: {e}")
            raise


async def get_product_by_id(product_id: int) -> Product:
    """Retrieves a product by its ID."""
    async with async_session() as session:
        try:
            product = await session.scalar(select(Product).where(product_id == Product.id))
            return product
        except Exception as e:
            logger.error(f"Error in get_product_by_id: {e}")
            raise


@cached(ttl=None, key_builder=lambda user_id: build_key(user_id))
async def get_steamid64_by_userid(user_id: int) -> list[int]:
    """Возвращает Steam ID по user ID."""
    async with async_session() as session:
        try:
            result = await session.execute(select(SteamAccount.steamid64).where(user_id == SteamAccount.user_id))
            steam_accounts = result.scalars().all()
            steamid64_list = [acc for acc in steam_accounts]
            return steamid64_list
        except Exception as e:
            logger.error(f"Ошибка в get_steamid64_by_userid: {e}")
            raise


@cached(ttl=None)
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


async def get_steamids64_owners(steamid64_list: list[int]) -> dict[int, list[int]]:
    async with async_session() as session:
        try:
            result = await session.execute(
                select(SteamAccount.user_id, SteamAccount.steamid64)
                .where(SteamAccount.steamid64.in_(steamid64_list))
            )

            user_to_steamids = {}
            for user_id, steamid64 in result:
                if user_id not in user_to_steamids:
                    user_to_steamids[user_id] = []
                user_to_steamids[user_id].append(steamid64)

            return user_to_steamids
        except Exception as e:
            logger.error(f"Error in get_steamids64_owners: {e}")
            raise

@cached(ttl=None)
async def get_users_with_steam_accounts() -> list[int]:
    """Возвращает telegram_id всех пользователей с не пустым steam_account."""
    async with async_session() as session:
        try:
            result = await session.execute(
                select(User.telegram_id)
                .join(User.steam_accounts)
                .distinct()
            )
            user_telegram_ids = result.scalars().all()
            return user_telegram_ids
        except Exception as e:
            logger.error(f"Ошибка в get_users_with_steam_accounts: {e}")
            raise


async def set_steamid64_for_user(user_id: int, steamid64: list[int]) -> list[int]:
    """Sets Steam URLs for a user, avoiding duplicates."""
    async with async_session() as session:
        try:
            existing_accounts_result = await session.execute(
                select(SteamAccount.steamid64).where(user_id == SteamAccount.user_id)
            )

            existing_steam_urls = set(row[0] for row in existing_accounts_result.all())

            new_steam_accounts = [acc for acc in steamid64 if acc not in existing_steam_urls]

            if not new_steam_accounts:
                return []

            new_steam_account_objects = [
                SteamAccount(steamid64=steamid64, user_id=user_id) for steamid64 in new_steam_accounts
            ]
            session.add_all(new_steam_account_objects)

            await session.commit()
            await clear_cache(get_steamid64_by_userid, user_id)
            await clear_cache(get_all_steamid64)
            await clear_cache(get_users_with_steam_accounts)
            return new_steam_accounts
        except Exception as e:
            logger.error(f"Error in set_steamid64_for_user: {e}")
            await session.rollback()
            raise


async def remove_steamid64_for_user(user_id: int, steamid64: list[int]) -> list[int]:
    """Удаляет указанные Steam ID для пользователя."""
    async with async_session() as session:
        try:
            accounts_to_remove = []

            # Разбиваем steamid64 на группы по 32766 элементов postgres limit
            chunk_size = 32766
            steamid64_chunks = [steamid64[i:i + chunk_size] for i in range(0, len(steamid64), chunk_size)]

            for chunk in steamid64_chunks:
                accounts_to_remove_result = await session.execute(
                    select(SteamAccount.steamid64)
                    .where(
                        user_id == SteamAccount.user_id,
                        SteamAccount.steamid64.in_(chunk)
                    )
                )
                accounts_to_remove.extend(accounts_to_remove_result.scalars().all())

            if not accounts_to_remove:
                return []

            for chunk in steamid64_chunks:
                await session.execute(
                    sql_delete(SteamAccount)
                    .where(
                        user_id == SteamAccount.user_id,
                        SteamAccount.steamid64.in_(chunk)
                    )
                )

            await session.commit()
            await clear_cache(get_steamid64_by_userid, user_id)
            await clear_cache(get_all_steamid64)
            await clear_cache(get_users_with_steam_accounts)
            return accounts_to_remove
        except Exception as e:
            logger.error(f"Error in remove_steamid64_for_user: {e}")
            await session.rollback()
            raise

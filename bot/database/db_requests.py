from decimal import Decimal

from loguru import logger
from sqlalchemy import delete as sql_delete
from sqlalchemy.future import select

from bot.core.loader import config_json
from bot.database.database import async_session
from bot.database.models import User, Product, Category, SteamAccount
from bot.decorators.dec_cache import cached, build_key, clear_cache


async def set_user(telegram_id: int, username: str = None, referral_code: str = None) -> User:
    """Создает или извлекает пользователя на основе telegram_id, с дополнительным реферальным кодом для бонусов"""
    async with async_session() as session:
        try:
            user = await session.scalar(select(User).where(telegram_id == User.telegram_id))

            if not user:
                if username is None:
                    username = str(telegram_id)
                referred_by = None
                if referral_code:
                    try:
                        referrer_id = int(referral_code)
                        referrer = await session.scalar(select(User).where(referrer_id == User.telegram_id))
                        if referrer:
                            referred_by = referrer.telegram_id
                        else:
                            logger.info(f"Реферальный код {referral_code} не существует")
                    except ValueError:
                        logger.info(f"Неправильный реферальный код : {referral_code}")

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
            logger.error(f"ошибка в set_user: {e}")
            await session.rollback()
            raise


async def get_user_by_telegram_id(telegram_id: int) -> User:
    """Возвращает user по его telegramID"""
    async with async_session() as session:
        try:
            user = await session.scalar(select(User).where(telegram_id == User.telegram_id))
            return user
        except Exception as e:
            logger.error(f"Ошибка в get_user_by_telegram_id: {e}")
            raise


async def get_product_by_name(product_name: str) -> Product:
    """Возвращает product по product Name"""
    async with async_session() as session:
        try:
            product = await session.scalar(select(Product).where(product_name == Product.name))
            return product
        except Exception as e:
            logger.error(f"Ошибка в get_product_by_name: {e}")
            raise

async def set_categories(name: str, photo_filename: str) -> list[Category]:
    """добавляет новую категорию в базу данных
        Принимает:
        name: любое строковое значение (32) | Название категории
        photo_filename: любое строковое значение (32) | Название file_ids аватарки
    """
    async with async_session() as session:
        try:
            category = Category(name=name, photo_filename=photo_filename)
            session.add(category)
            await session.commit()
            return category
        except Exception as e:
            logger.error(f"Ошибка в create_category: {e}")
            await session.rollback()
            raise

async def delete_categories(name: str):
    """удаляет категорию из базы данных
    Принимает:
    name: любое строковое значение (32) | Название категории
    Возвращает:
    True - успех ( че тупой чтоли?)
    """
    async with async_session() as session:
        try:
            async with session.begin():
                category_result = await session.execute(select(Category).where(Category.name == name))
                category = category_result.scalar_one_or_none()
                
                if category:
                    await session.delete(category)
                    await session.commit()
                    logger.info(f"Категория '{name}' успешно удалена.")
                    return True
                else:
                    logger.error(f"Категория '{name}' не найдена.")
                    return False
        except Exception as e:
            logger.error(f"Ошибка при удалении категории '{name}': {e}")
            await session.rollback()
            raise

async def get_all_categories() -> list[Category]:
    """Возвращает все categories"""
    async with async_session() as session:
        try:
            result = await session.scalars(select(Category))
            categories = result.all()
            return categories
        except Exception as e:
            logger.error(f"ошибка в get_all_categories: {e}")
            raise



async def get_all_Products() -> list[Product]:
    """Возвращает все Products"""
    async with async_session() as session:
        try:
            result = await session.scalars(select(Product))
            product = result.all()
            return product
        except Exception as e:
            logger.error(f"ошибка в get_all_categories: {e}")
            raise

async def get_all_users() -> list[User]:
    """Возвращает все users"""
    async with async_session() as session:
        try:
            result = await session.scalars(select(User))
            users = result.all()
            return users
        except Exception as e:
            logger.error(f"ошибка в get_all_users: {e}")
            raise

async def get_category_by_id(category_id: int) -> Category:
    """Возвращает category по ID."""
    async with async_session() as session:
        try:
            category = await session.scalar(select(Category).where(category_id == Category.id))
            return category
        except Exception as e:
            logger.error(f"ошибка в get_category_by_id: {e}")
            raise

async def get_category_by_name(name: str) -> Category:
    """Возвращает category по Name."""
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Category).where(Category.name == name)
            )
            category = result.scalars().first()
            return category

async def get_products_by_category(category_id: int) -> list[Product]:
    """Возвращает список product по category ID."""
    async with async_session() as session:
        try:
            products = await session.scalars(select(Product).where(category_id == Product.category_id))
            products_list = products.all()
            return products_list
        except Exception as e:
            logger.error(f"ошибка в get_products_by_category: {e}")
            raise


async def get_product_by_id(product_id: int) -> Product:
    """Возвращает product по productID."""
    async with async_session() as session:
        try:
            product = await session.scalar(select(Product).where(product_id == Product.id))
            return product
        except Exception as e:
            logger.error(f"ошибка в get_product_by_id: {e}")
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
    """
    Извлекает все Steam URLs
    """
    async with async_session() as session:
        try:
            result = await session.execute(select(SteamAccount.steamid64).distinct())
            steam_accounts = result.scalars().all()
            return steam_accounts
        except Exception as e:
            logger.error(f"ошибка в get_all_steamid64: {e}")
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
            logger.error(f"ошибка в get_steamids64_owners: {e}")
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
    """
    Устанвливает Steam URLs для user
    Удаляет/Избегает дубликаты
    """
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
            logger.error(f"ошибка в set_steamid64_for_user: {e}")
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
            logger.error(f"ошибка в remove_steamid64_for_user: {e}")
            await session.rollback()
            raise


async def create_order(user_id: int, product_id: int, quantity: int) -> Order:
    async with async_session() as session:
        try:
            user = await get_user_by_telegram_id(user_id)
            product = await session.scalar(select(Product).where(Product.id == product_id))

            if not user or not product:
                raise ValueError("User or Product not found")

            total_price = product.price * quantity

            order = Order(user_id=user.telegram_id, total_price=total_price, status='pending')
            order_item = OrderItem(product_id=product.id, quantity=quantity, price=product.price)
            order.order_items.append(order_item)

            session.add(order)
            await session.commit()
            await session.refresh(order)

            return order
        except Exception as e:
            logger.error(f"Error in create_order: {e}")
            await session.rollback()
            raise


async def get_order_by_id(order_id: int) -> Order:
    async with async_session() as session:
        try:
            order = await session.scalar(select(Order).where(Order.id == order_id))
            return order
        except Exception as e:
            logger.error(f"Error in get_order_by_id: {e}")
            raise


async def update_order_status(order_id: int, new_status: str):
    async with async_session() as session:
        try:
            order = await session.scalar(select(Order).where(Order.id == order_id))
            if order:
                order.status = new_status
                await session.commit()
        except Exception as e:
            logger.error(f"Error in update_order_status: {e}")
            await session.rollback()
            raise
from sqlalchemy import Integer, cast
from sqlalchemy.future import select
from bot.database.models import async_session, User, Product, Category
from loader import configJson
from decimal import Decimal

async def set_user(telegram_id: int, username: str = None, referral_code: str = None) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        
        if not user:
            referred_by = None
            if referral_code:
                try:
                    referrer_id = int(referral_code)  # Преобразуем referral_code в int
                    referrer = await session.scalar(select(User).where(User.telegram_id == referrer_id))
                    if referrer:
                        referred_by = referrer.telegram_id
                    else:
                        print(f"Referral code {referral_code} does not exist")
                except ValueError:
                    print(f"Invalid referral code: {referral_code}")
            
            user = User(telegram_id=telegram_id, username=username, referred_by=referred_by)
            session.add(user)
            if referred_by:
                bonus_points = await configJson.get_config_value('referral_bonus')
                if(bonus_points > 0):
                    referrer.bonus_points += Decimal(bonus_points)
                    session.add(referrer)

            await session.commit()
        return user
    
async def get_user_by_telegram_id(telegram_id: int) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if(isinstance(user, User)):
            return user
        
async def get_product_by_name(product_name: str) -> Product:
    async with async_session() as session:
        product = await session.scalar(select(Product).where(Product.name == product_name))
        if(isinstance(product, Product)):
            return product
        
async def get_all_categories() -> Category:
    async with async_session() as session:
        result = await session.scalars(select(Category))
        categories = result.all()
        return categories
    
async def get_category_by_id(category_id: int) -> Category:
    async with async_session() as session:
        result = await session.scalar(select(Category).where(Category.id ==category_id ))
        if(isinstance(result, Category)):
            return result
    
async def get_products_by_category(category_id: int) -> Product:
    async with async_session() as session:
        products = await session.scalars(select(Product).where(Product.category_id == category_id))
        products = products.all()
        return products
        
async def get_product_by_id(product_id: int) -> Product:
    async with async_session() as session:
        product = await session.scalar(select(Product).where(Product.id == product_id))
        if(isinstance(product, Product)):
            return product
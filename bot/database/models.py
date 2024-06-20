from sqlalchemy import DECIMAL, Integer, String, DateTime, ForeignKey, BigInteger, func
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime
from bot.settings.settings import settings 

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

engine = create_async_engine(url=settings.SQLALCHEMY_URL)
async_session = async_sessionmaker(engine)

class User(Base):
    __tablename__ = 'user'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    discount_percentage: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0.00, nullable=False)
    bonus_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    referred_by: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.telegram_id'), nullable=True)
    
    referrer = relationship('User', remote_side=[telegram_id])
    steam_accounts = relationship('SteamAccount', back_populates='user')

class SteamAccount(Base):
    __tablename__ = 'steam_accounts'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    steamid64: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.telegram_id'), nullable=False, index=True)

    user = relationship('User', back_populates='steam_accounts')
    
class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    photo_filename: Mapped[str] = mapped_column(String(32), nullable=False)

    products = relationship('Product', back_populates='category')

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=True)
    photo_filename: Mapped[str] = mapped_column(String(32), nullable=False)

    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=False)
    
    category = relationship('Category', back_populates='products')

async def start_db_postegre():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def close_db_postegre(async_session):
    await async_session.close()
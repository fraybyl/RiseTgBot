from sqlalchemy import DECIMAL, Column, Integer, String, DateTime, ForeignKey, Float, BigInteger, func, VARCHAR
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
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    discount_percentage: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0.00, nullable=False)
    bonus_points: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.00, nullable=False)
    referred_by: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.telegram_id'), nullable=True)

    referrer = relationship('User', remote_side=[telegram_id])
    
class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    label: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(DECIMAL(10, 2))
    quantity: Mapped[int] = mapped_column(Integer)
    photo_url: Mapped[str] = mapped_column(String(255))


    
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
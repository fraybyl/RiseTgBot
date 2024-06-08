from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, BigInteger
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime
from bot.config.settings import settings 

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

engine = create_async_engine(url=settings.SQLALCHEMY_URL)
async_session = async_sessionmaker(engine)

class User(Base):
    __tablename__ = 'user'

    telegram_id = Column(BigInteger, primary_key=True, index=True, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    discount_percentage = Column(Float, default=0.0, nullable=False)
    bonus_points = Column(Integer, default=0, nullable=False)
    referred_by = Column(BigInteger, ForeignKey('user.telegram_id'), nullable=True)

    referrer = relationship('User', remote_side=[telegram_id])
    
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
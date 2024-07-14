from uuid import uuid4

from asyncpg import Connection
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession

from bot.core.config import settings
from bot.database.base_model import BaseModel


class CConnection(Connection):
    def _get_unique_id(self, prefix: str) -> str:
        return f"__asyncpg_{prefix}_{uuid4()}__"


def get_engine(url: URL | str = settings.database_url) -> AsyncEngine:
    return create_async_engine(
        url=url,
        echo=settings.DEBUG,
        pool_size=0,
        connect_args={
            "connection_class": CConnection,
        },
    )


def get_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


db_url = settings.database_url
engine = get_engine(url=db_url)
async_session = get_session_maker(engine)


async def start_db_postgres():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


async def close_db_postgres(engine: AsyncEngine):
    await engine.dispose()

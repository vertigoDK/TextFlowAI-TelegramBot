from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from typing import AsyncGenerator
from app.config.settings import settings

engine: AsyncEngine = create_async_engine(
    url=settings.DATABASE_URL.get_secret_value(),
    echo=True,
)

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
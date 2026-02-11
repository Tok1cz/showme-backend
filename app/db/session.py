from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore


async def get_session() -> AsyncSession:  # type: ignore
    async with AsyncSessionLocal() as session:  # type: ignore
        yield session  # type: ignore


sync_engine = create_engine(settings.DATABASE_URL_SYNCH, echo=False, future=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)

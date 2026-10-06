import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI.replace("psycopg://", "asyncpg://")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

async def init_db() -> None:
    async with engine.begin() as conn:
        # Import all models here so they are registered properly
        from app.models.user import User
        from app.models.training import *
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


# Helper: run blocking sync code in thread
def run_sync(func):
    import asyncio
    import concurrent.futures
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        return loop.run_in_executor(pool, func)

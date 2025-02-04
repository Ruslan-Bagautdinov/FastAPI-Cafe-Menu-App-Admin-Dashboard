from sqlalchemy.ext.asyncio import (AsyncSession,
                                    async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base

import logging
import asyncpg

from app.config import HOME_DB, WORK_DATABASE_URL, LOCAL_DATABASE_URL

if HOME_DB is True:
    DATABASE_URL = LOCAL_DATABASE_URL
else:
    DATABASE_URL = WORK_DATABASE_URL


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# engine = create_async_engine(DATABASE_URL, echo=False)

engine = create_async_engine(DATABASE_URL, pool_timeout=60, pool_size=250, max_overflow=50, echo=False)


async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def init_db():
    try:
        engine = create_async_engine(DATABASE_URL, pool_timeout=60, pool_size=250, max_overflow=50, echo=False)
        async with engine.begin() as conn:
            logger.debug("Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
            logger.debug("Tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

logger.info(DATABASE_URL)
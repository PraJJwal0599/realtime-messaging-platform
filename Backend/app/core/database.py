from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
AsyncSessionLocal = None

if DATABASE_URL:
    engine = create_async_engine (
        DATABASE_URL,
        echo = True,
        pool_pre_ping = True,
        connect_args = {"statement_cache_size" : 0, "timeout" : 30},    
    )
    AsyncSessionLocal = sessionmaker(
        engine, class_ = AsyncSession, expire_on_commit = False
    )
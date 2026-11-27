from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import settings

# -----------------------------------------------------------------------------
# Async Engine & Connection Pool Configuration
# -----------------------------------------------------------------------------
# pool_pre_ping=True: Checks connection liveness with a lightweight PING
# before handing it out, preventing "server closed connection unexpectedly" errors.
# pool_size=10: Number of persistent connections kept open in the pool.
# max_overflow=20: Max burst connections created above pool_size under high load.
# pool_recycle=1800: Recycles connections older than 30 mins to avoid firewall drops.
# -----------------------------------------------------------------------------
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
)

# Async session factory bound to the async engine
# expire_on_commit=False prevents SQLAlchemy from expiring attributes after commit,
# which would otherwise trigger lazy-load errors outside an active async context.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an isolated asynchronous database session.
    Automatically handles session lifecycle, rollback on unhandled exceptions,
    and returns connection to the pool upon completion.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

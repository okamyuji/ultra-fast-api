"""
tests/performance/conftest.py - パフォーマンステスト用の設定

パフォーマンステストは本番DBに対して実行されるため、
通常のテストDBではなく実際のDBを使用します。
"""

import asyncio
from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings


@pytest_asyncio.fixture(scope="session")
async def event_loop():
    """イベントループをセッションスコープで提供"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """本番DBエンジン（パフォーマンステスト用）"""
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_size=10,
        max_overflow=20,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession]:
    """本番DBセッション（パフォーマンステスト用）"""
    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()

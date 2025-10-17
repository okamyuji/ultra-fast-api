"""
テスト設定とフィクスチャ - TDD基盤
"""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.base import Base

# pytest-asyncio設定
pytest_plugins = ("pytest_asyncio",)


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """テスト用非同期エンジンを作成"""
    # SQLite in-memory データベース
    database_url = "sqlite+aiosqlite:///:memory:"

    # SQLite用のエンジン設定
    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # スキーマ作成
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # クリーンアップ
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession]:
    """テスト用非同期セッション"""
    async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture
def anyio_backend():
    """anyioのバックエンド指定"""
    return "asyncio"

"""
tests/performance/test_products_performance.py - 商品APIパフォーマンステスト

1000万件のデータに対して応答時間が1秒以内であることを確認します。
"""

import statistics
import time
from datetime import timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import create_jwt_token
from app.config import settings
from app.database.models.user import User
from app.main import app


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """パフォーマンステスト用ユーザーを取得または作成"""
    from sqlalchemy import select

    # 既存のユーザーを取得
    result = await db_session.execute(select(User).where(User.email == "perftest@example.com"))
    user = result.scalar_one_or_none()

    if user:
        return user

    # 存在しない場合は作成
    user = User(
        username="perftest_user",
        email="perftest@example.com",
        password_hash="hashed_password",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def access_token(test_user: User) -> str:
    """アクセストークンを生成"""
    return create_jwt_token(
        data={"sub": str(test_user.id), "token_type": "access"},
        expires_delta=timedelta(hours=settings.access_token_expire_hours),
    )


async def get_product_count(db_session: AsyncSession) -> int:
    """商品の総数を取得"""
    result = await db_session.execute(text("SELECT COUNT(*) FROM products"))
    return result.scalar() or 0


async def measure_request_time(client: AsyncClient, url: str, headers: dict | None = None) -> tuple[float, int]:
    """リクエストの応答時間を計測"""
    start_time = time.perf_counter()
    response = await client.get(url, headers=headers or {}, follow_redirects=True)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    return elapsed_time, response.status_code


@pytest.mark.performance
class TestProductsPerformance:
    """商品APIパフォーマンステストクラス"""

    @pytest.mark.asyncio
    async def test_products_list_initial_page_performance(self, db_session: AsyncSession, access_token: str):
        """商品一覧（初期ページ）のパフォーマンステスト

        要件: 応答時間 < 1秒
        """
        # データ件数確認
        product_count = await get_product_count(db_session)
        print(f"\n📊 総商品数: {product_count:,}件")

        if product_count < 100_000:
            pytest.skip(f"パフォーマンステストには最低10万件のデータが必要です（現在: {product_count:,}件）")

        # 複数回計測
        response_times = []
        iterations = 10

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            print(f"\n🔄 {iterations}回のリクエストを実行中...")

            for i in range(iterations):
                elapsed_time, status_code = await measure_request_time(client, "/products?limit=100")
                response_times.append(elapsed_time)
                print(f"  試行 {i + 1}: {elapsed_time * 1000:.2f}ms (status: {status_code})")

                assert status_code == 200, f"リクエストが失敗しました: {status_code}"

        # 統計計算
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        stdev = statistics.stdev(response_times) if len(response_times) > 1 else 0

        # 結果表示
        print("\n" + "=" * 80)
        print("📈 パフォーマンステスト結果 - 商品一覧（初期ページ）")
        print("=" * 80)
        print(f"データ件数: {product_count:,}件")
        print("ページサイズ: 100件")
        print(f"試行回数: {iterations}回")
        print(f"平均応答時間: {avg_time * 1000:.2f}ms")
        print(f"中央値: {median_time * 1000:.2f}ms")
        print(f"最小: {min_time * 1000:.2f}ms")
        print(f"最大: {max_time * 1000:.2f}ms")
        print(f"標準偏差: {stdev * 1000:.2f}ms")
        print("=" * 80)

        # アサーション
        assert avg_time < 1.0, f"平均応答時間が1秒を超えています: {avg_time * 1000:.2f}ms"
        assert max_time < 2.0, f"最大応答時間が2秒を超えています: {max_time * 1000:.2f}ms"

        print("✅ パフォーマンス要件を満たしています（< 1秒）")

    @pytest.mark.asyncio
    async def test_products_list_with_pagination_performance(self, db_session: AsyncSession, access_token: str):
        """カーソルベースページネーションのパフォーマンステスト

        要件: 応答時間 < 1秒（どのページでも）
        """
        product_count = await get_product_count(db_session)

        if product_count < 100_000:
            pytest.skip(f"パフォーマンステストには最低10万件のデータが必要です（現在: {product_count:,}件）")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 初期ページ取得
            response = await client.get("/products?limit=100", follow_redirects=True)
            assert response.status_code == 200
            data = response.json()
            cursor = data["pagination"].get("next_cursor")

            if not cursor:
                pytest.skip("次のページが存在しません")

            # カーソルベースの次ページを複数回計測
            response_times = []
            iterations = 5

            print(f"\n🔄 カーソルベースページネーション: {iterations}回のリクエスト...")

            for i in range(iterations):
                elapsed_time, status_code = await measure_request_time(client, f"/products?limit=100&cursor={cursor}")
                response_times.append(elapsed_time)
                print(f"  試行 {i + 1}: {elapsed_time * 1000:.2f}ms")

                assert status_code == 200

        avg_time = statistics.mean(response_times)
        max_time = max(response_times)

        print("\n" + "=" * 80)
        print("📈 カーソルベースページネーション パフォーマンス")
        print("=" * 80)
        print(f"平均応答時間: {avg_time * 1000:.2f}ms")
        print(f"最大応答時間: {max_time * 1000:.2f}ms")
        print("=" * 80)

        assert avg_time < 1.0, f"平均応答時間が1秒を超えています: {avg_time * 1000:.2f}ms"
        print("✅ カーソルベースページネーション: パフォーマンス要件を満たしています")

    @pytest.mark.asyncio
    async def test_products_list_with_filters_performance(self, db_session: AsyncSession, access_token: str):
        """フィルタリング付き商品一覧のパフォーマンステスト

        要件: 応答時間 < 1秒
        """
        product_count = await get_product_count(db_session)

        if product_count < 100_000:
            pytest.skip(f"パフォーマンステストには最低10万件のデータが必要です（現在: {product_count:,}件）")

        # 複数のフィルタパターンをテスト
        filter_patterns = [
            ("カテゴリフィルタ", "?category=electronics&limit=100"),
            ("ステータスフィルタ", "?status=active&limit=100"),
            (
                "複合フィルタ",
                "?category=electronics&status=active&limit=100",
            ),
            ("日付範囲フィルタ", "?date_from=2024-01-01&date_to=2025-12-31&limit=100"),
        ]

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            for filter_name, query_params in filter_patterns:
                response_times = []
                iterations = 5

                print(f"\n🔍 {filter_name} テスト中...")

                for i in range(iterations):
                    elapsed_time, status_code = await measure_request_time(client, f"/products{query_params}")
                    response_times.append(elapsed_time)
                    print(f"  試行 {i + 1}: {elapsed_time * 1000:.2f}ms")

                    assert status_code == 200

                avg_time = statistics.mean(response_times)
                max_time = max(response_times)

                print(f"  ├─ 平均: {avg_time * 1000:.2f}ms")
                print(f"  └─ 最大: {max_time * 1000:.2f}ms")

                assert avg_time < 1.0, f"{filter_name}の平均応答時間が1秒を超えています: {avg_time * 1000:.2f}ms"

        print("\n✅ 全てのフィルタパターンでパフォーマンス要件を満たしています")

    @pytest.mark.asyncio
    async def test_products_search_performance(self, db_session: AsyncSession, access_token: str):
        """検索機能のパフォーマンステスト

        要件: 応答時間 < 1秒
        """
        product_count = await get_product_count(db_session)

        if product_count < 100_000:
            pytest.skip(f"パフォーマンステストには最低10万件のデータが必要です（現在: {product_count:,}件）")

        # 検索パターン
        search_patterns = [
            ("ノートパソコン", "?search=ノートパソコン&limit=100"),
            ("スマートフォン", "?search=スマートフォン&limit=100"),
            ("高性能", "?search=高性能&limit=100"),
        ]

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            for search_term, query_params in search_patterns:
                response_times = []
                iterations = 5

                print(f"\n🔎 検索: '{search_term}' テスト中...")

                for i in range(iterations):
                    elapsed_time, status_code = await measure_request_time(client, f"/products{query_params}")
                    response_times.append(elapsed_time)
                    print(f"  試行 {i + 1}: {elapsed_time * 1000:.2f}ms")

                    assert status_code == 200

                avg_time = statistics.mean(response_times)
                max_time = max(response_times)

                print(f"  ├─ 平均: {avg_time * 1000:.2f}ms")
                print(f"  └─ 最大: {max_time * 1000:.2f}ms")

                assert avg_time < 1.0, f"検索'{search_term}'の平均応答時間が1秒を超えています: {avg_time * 1000:.2f}ms"

        print("\n✅ 全ての検索パターンでパフォーマンス要件を満たしています")

    @pytest.mark.asyncio
    async def test_product_detail_performance(self, db_session: AsyncSession, access_token: str):
        """商品詳細取得のパフォーマンステスト

        要件: 応答時間 < 1秒
        """
        # ランダムな商品IDを取得
        result = await db_session.execute(text("SELECT id FROM products ORDER BY RANDOM() LIMIT 1"))
        product_id = result.scalar()

        if not product_id:
            pytest.skip("商品が存在しません")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response_times = []
            iterations = 10

            print(f"\n📦 商品詳細取得テスト中... (ID: {product_id})")

            for i in range(iterations):
                elapsed_time, status_code = await measure_request_time(client, f"/products/{product_id}")
                response_times.append(elapsed_time)
                print(f"  試行 {i + 1}: {elapsed_time * 1000:.2f}ms")

                assert status_code == 200

            avg_time = statistics.mean(response_times)
            max_time = max(response_times)

            print("\n" + "=" * 80)
            print("📈 商品詳細取得 パフォーマンス")
            print("=" * 80)
            print(f"平均応答時間: {avg_time * 1000:.2f}ms")
            print(f"最大応答時間: {max_time * 1000:.2f}ms")
            print("=" * 80)

            assert avg_time < 0.5, f"平均応答時間が500msを超えています: {avg_time * 1000:.2f}ms"
            print("✅ 商品詳細取得: パフォーマンス要件を満たしています（< 500ms）")

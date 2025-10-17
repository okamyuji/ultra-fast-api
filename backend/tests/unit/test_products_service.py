"""
unit/test_products_service.py - 商品サービスのユニットテスト（TDD）
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.products.schemas import ProductCreate, ProductListParams, ProductUpdate
from app.products.service import ProductsService


class TestProductsService:
    """商品サービスのテストクラス"""

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession):
        """テストユーザーを作成"""
        from src.app.auth.utils import hash_password

        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("TestPassword123!"),
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def products_service(self, db_session: AsyncSession):
        """商品サービスのインスタンスを作成"""
        return ProductsService(db_session)

    @pytest.fixture
    def product_data(self):
        """テスト商品のデータ"""
        return {
            "name": "Test Product",
            "description": "Test Description",
            "category": "electronics",
            "status": "active",
            "price": 99.99,
            "stock": 10,
        }

    # ーーーーーー 商品作成テスト ーーーーーー

    @pytest.mark.asyncio
    async def test_create_product_success(self, products_service, test_user, product_data):
        """商品作成成功のテスト"""
        # Arrange
        create_schema = ProductCreate(**product_data)

        # Act
        product = await products_service.create_product(create_schema, test_user.id)

        # Assert
        assert product.id is not None
        assert product.name == product_data["name"]
        assert product.category == product_data["category"]
        assert product.price == product_data["price"]
        assert product.user_id == test_user.id

    @pytest.mark.asyncio
    async def test_create_product_invalid_status(self, products_service, test_user):
        """無効なステータスでの商品作成テスト"""
        # Arrange
        invalid_data = {
            "name": "Test Product",
            "description": "Test",
            "category": "electronics",
            "status": "invalid_status",
            "price": 99.99,
            "stock": 10,
        }

        # Act & Assert
        with pytest.raises(ValueError, match="Status must be one of"):
            ProductCreate(**invalid_data)

    # ーーーーーー 商品取得テスト ーーーーーー

    @pytest.mark.asyncio
    async def test_get_product_by_id(self, products_service, test_user, product_data):
        """IDで商品を取得するテスト"""
        # Arrange
        create_schema = ProductCreate(**product_data)
        created_product = await products_service.create_product(create_schema, test_user.id)

        # Act
        product = await products_service.get_product_by_id(created_product.id)

        # Assert
        assert product is not None
        assert product.id == created_product.id
        assert product.name == product_data["name"]

    @pytest.mark.asyncio
    async def test_get_product_by_id_not_found(self, products_service):
        """存在しない商品IDでの取得テスト"""
        # Arrange
        non_existent_id = uuid4()

        # Act
        product = await products_service.get_product_by_id(non_existent_id)

        # Assert
        assert product is None

    # ーーーーーー 商品更新テスト ーーーーーー

    @pytest.mark.asyncio
    async def test_update_product_success(self, products_service, test_user, product_data):
        """商品更新成功のテスト"""
        # Arrange
        create_schema = ProductCreate(**product_data)
        created_product = await products_service.create_product(create_schema, test_user.id)

        update_data = ProductUpdate(name="Updated Product", price=149.99)

        # Act
        updated_product = await products_service.update_product(created_product.id, update_data)

        # Assert
        assert updated_product.name == "Updated Product"
        assert updated_product.price == 149.99
        assert updated_product.category == product_data["category"]  # 変更されていない

    @pytest.mark.asyncio
    async def test_update_product_not_found(self, products_service):
        """存在しない商品の更新テスト"""
        # Arrange
        non_existent_id = uuid4()
        update_data = ProductUpdate(name="Updated")

        # Act & Assert
        with pytest.raises(ValueError, match="商品が見つかりません"):
            await products_service.update_product(non_existent_id, update_data)

    # ーーーーーー 商品削除テスト ーーーーーー

    @pytest.mark.asyncio
    async def test_delete_product_success(self, products_service, test_user, product_data):
        """商品削除成功のテスト"""
        # Arrange
        create_schema = ProductCreate(**product_data)
        created_product = await products_service.create_product(create_schema, test_user.id)

        # Act
        await products_service.delete_product(created_product.id)

        # Assert
        product = await products_service.get_product_by_id(created_product.id)
        assert product is None

    @pytest.mark.asyncio
    async def test_delete_product_not_found(self, products_service):
        """存在しない商品の削除テスト"""
        # Arrange
        non_existent_id = uuid4()

        # Act & Assert
        with pytest.raises(ValueError, match="商品が見つかりません"):
            await products_service.delete_product(non_existent_id)

    # ーーーーーー 商品リスト取得テスト ーーーーーー

    @pytest.mark.asyncio
    async def test_list_products_basic(self, products_service, test_user, product_data):
        """基本的な商品リスト取得のテスト"""
        # Arrange - 3つの商品を作成
        for i in range(3):
            data = product_data.copy()
            data["name"] = f"Product {i}"
            create_schema = ProductCreate(**data)
            await products_service.create_product(create_schema, test_user.id)

        params = ProductListParams(limit=10)

        # Act
        result = await products_service.list_products(params)

        # Assert
        assert len(result["items"]) == 3
        assert result["pagination"]["returned_count"] == 3
        assert result["pagination"]["has_more"] is False

    @pytest.mark.asyncio
    async def test_list_products_with_cursor_pagination(self, products_service, test_user, product_data):
        """カーソルベースページネーションのテスト"""
        # Arrange - 5つの商品を作成
        for i in range(5):
            data = product_data.copy()
            data["name"] = f"Product {i}"
            create_schema = ProductCreate(**data)
            await products_service.create_product(create_schema, test_user.id)

        # Act - 最初のページ (limit=2)
        params1 = ProductListParams(limit=2)
        result1 = await products_service.list_products(params1)

        # Assert - 最初のページ
        assert len(result1["items"]) == 2
        assert result1["pagination"]["has_more"] is True
        assert result1["pagination"]["next_cursor"] is not None

        # Act - 2ページ目
        params2 = ProductListParams(limit=2, cursor=result1["pagination"]["next_cursor"])
        result2 = await products_service.list_products(params2)

        # Assert - 2ページ目
        assert len(result2["items"]) == 2
        assert result2["pagination"]["has_more"] is True

    @pytest.mark.asyncio
    async def test_list_products_with_category_filter(self, products_service, test_user, product_data):
        """カテゴリフィルターのテスト"""
        # Arrange
        for i, category in enumerate(["electronics", "books", "electronics"]):
            data = product_data.copy()
            data["name"] = f"Product {i}"
            data["category"] = category
            create_schema = ProductCreate(**data)
            await products_service.create_product(create_schema, test_user.id)

        params = ProductListParams(category="electronics")

        # Act
        result = await products_service.list_products(params)

        # Assert
        assert len(result["items"]) == 2
        for item in result["items"]:
            assert item.category == "electronics"

    @pytest.mark.asyncio
    async def test_list_products_with_search(self, products_service, test_user, product_data):
        """検索機能のテスト"""
        # Arrange
        names = ["Laptop Computer", "Gaming Mouse", "Mechanical Keyboard"]
        for name in names:
            data = product_data.copy()
            data["name"] = name
            create_schema = ProductCreate(**data)
            await products_service.create_product(create_schema, test_user.id)

        params = ProductListParams(search="gaming")

        # Act
        result = await products_service.list_products(params)

        # Assert
        assert len(result["items"]) == 1
        assert "Gaming" in result["items"][0].name

    @pytest.mark.asyncio
    async def test_list_products_with_sort(self, products_service, test_user, product_data):
        """ソート機能のテスト"""
        # Arrange
        prices = [100.0, 50.0, 150.0]
        for i, price in enumerate(prices):
            data = product_data.copy()
            data["name"] = f"Product {i}"
            data["price"] = price
            create_schema = ProductCreate(**data)
            await products_service.create_product(create_schema, test_user.id)

        params = ProductListParams(sort_by="price", sort_order="asc")

        # Act
        result = await products_service.list_products(params)

        # Assert
        assert len(result["items"]) == 3
        assert result["items"][0].price == 50.0
        assert result["items"][1].price == 100.0
        assert result["items"][2].price == 150.0

    @pytest.mark.asyncio
    async def test_list_products_with_date_range_filter(self, products_service, test_user, product_data, db_session):
        """日付範囲フィルターのテスト"""
        # Arrange - 異なる日付の商品を作成
        now = datetime.now(UTC)
        dates = [
            now - timedelta(days=5),
            now - timedelta(days=2),
            now,
        ]

        for i, date in enumerate(dates):
            data = product_data.copy()
            data["name"] = f"Product {i}"
            create_schema = ProductCreate(**data)
            product = await products_service.create_product(create_schema, test_user.id)

            # 日付を手動で設定
            product.created_at = date
            db_session.add(product)

        await db_session.commit()

        # Act - 3日前から現在まで
        params = ProductListParams(
            date_from=now - timedelta(days=3),
            date_to=now + timedelta(days=1),
        )
        result = await products_service.list_products(params)

        # Assert
        assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_list_products_combined_filters(self, products_service, test_user, product_data):
        """複数フィルターの組み合わせテスト"""
        # Arrange
        products_to_create = [
            {"name": "Gaming Laptop", "category": "electronics", "status": "active", "price": 1200.0},
            {"name": "Office Laptop", "category": "electronics", "status": "active", "price": 800.0},
            {"name": "Gaming Mouse", "category": "electronics", "status": "inactive", "price": 50.0},
            {"name": "Office Chair", "category": "furniture", "status": "active", "price": 300.0},
        ]

        for prod in products_to_create:
            data = product_data.copy()
            data.update(prod)
            create_schema = ProductCreate(**data)
            await products_service.create_product(create_schema, test_user.id)

        params = ProductListParams(
            category="electronics", status="active", search="laptop", sort_by="price", sort_order="desc"
        )

        # Act
        result = await products_service.list_products(params)

        # Assert
        assert len(result["items"]) == 2
        assert result["items"][0].name == "Gaming Laptop"
        assert result["items"][1].name == "Office Laptop"
        for item in result["items"]:
            assert item.category == "electronics"
            assert item.status == "active"

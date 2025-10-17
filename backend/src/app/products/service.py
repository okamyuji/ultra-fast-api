"""
products/service.py - 商品ビジネスロジック（TDD実装）
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.product import Product
from app.products.schemas import ProductCreate, ProductListParams, ProductUpdate


class ProductsService:
    """商品サービス"""

    def __init__(self, db_session: AsyncSession):
        """初期化"""
        self.db = db_session

    # ーーーーーー 商品作成 ーーーーーー

    async def create_product(self, schema: ProductCreate, user_id: UUID) -> Product:
        """商品を作成"""
        product = Product(
            name=schema.name,
            description=schema.description,
            category=schema.category,
            status=schema.status,
            price=schema.price,
            stock=schema.stock,
            user_id=user_id,
        )

        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)

        return product

    # ーーーーーー 商品取得 ーーーーーー

    async def get_product_by_id(self, product_id: UUID) -> Product | None:
        """IDで商品を取得"""
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalars().first()

    # ーーーーーー 商品更新 ーーーーーー

    async def update_product(self, product_id: UUID, schema: ProductUpdate) -> Product:
        """商品を更新"""
        product = await self.get_product_by_id(product_id)
        if not product:
            raise ValueError("商品が見つかりません")

        # 更新されたフィールドのみ適用
        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        product.updated_at = datetime.now(UTC)

        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)

        return product

    # ーーーーーー 商品削除 ーーーーーー

    async def delete_product(self, product_id: UUID) -> None:
        """商品を削除"""
        product = await self.get_product_by_id(product_id)
        if not product:
            raise ValueError("商品が見つかりません")

        await self.db.delete(product)
        await self.db.commit()

    # ーーーーーー 商品リスト取得 ーーーーーー

    async def list_products(self, params: ProductListParams) -> dict:
        """商品リストを取得（フィルタリング・ページネーション対応）"""
        # ベースクエリ
        query = select(Product)

        # カテゴリフィルター
        if params.category:
            query = query.where(Product.category == params.category)

        # ステータスフィルター
        if params.status:
            query = query.where(Product.status == params.status)

        # 日付範囲フィルター
        if params.date_from:
            query = query.where(Product.created_at >= params.date_from)

        if params.date_to:
            query = query.where(Product.created_at <= params.date_to)

        # 検索フィルター (名前または説明)
        if params.search:
            search_pattern = f"%{params.search}%"
            query = query.where(or_(Product.name.ilike(search_pattern), Product.description.ilike(search_pattern)))

        # Seek Method カーソルベースページネーション
        # 参考: https://use-the-index-luke.com/ja/sql/partial-results/fetch-next-page
        # 複合条件を使用した正確なページネーション
        if params.cursor:
            try:
                cursor_id = UUID(params.cursor)
                cursor_product = await self.get_product_by_id(cursor_id)

                if cursor_product:
                    # Seek Method: 複合条件でソートキー + ID を使用
                    # これにより、ソートキーが同一の場合でも正確にページネーション可能
                    sort_column = getattr(Product, params.sort_by)
                    cursor_sort_value = getattr(cursor_product, params.sort_by)

                    if params.sort_order == "desc":
                        # DESC順: (sort_column < cursor_value) OR (sort_column = cursor_value AND id < cursor_id)
                        query = query.where(
                            or_(
                                sort_column < cursor_sort_value,
                                (sort_column == cursor_sort_value) & (Product.id < cursor_id),
                            )
                        )
                    else:
                        # ASC順: (sort_column > cursor_value) OR (sort_column = cursor_value AND id > cursor_id)
                        query = query.where(
                            or_(
                                sort_column > cursor_sort_value,
                                (sort_column == cursor_sort_value) & (Product.id > cursor_id),
                            )
                        )
            except ValueError:
                # 無効なカーソルの場合は無視
                pass

        # ソート
        sort_column = getattr(Product, params.sort_by)
        if params.sort_order == "desc":
            query = query.order_by(desc(sort_column), desc(Product.id))
        else:
            query = query.order_by(sort_column, Product.id)

        # limit + 1 で次ページの有無を判定
        query = query.limit(params.limit + 1)

        # 実行
        result = await self.db.execute(query)
        products = list(result.scalars().all())

        # has_more判定
        has_more = len(products) > params.limit
        if has_more:
            products = products[: params.limit]

        # next_cursor生成
        next_cursor = str(products[-1].id) if products and has_more else None

        return {
            "items": products,
            "pagination": {
                "next_cursor": next_cursor,
                "has_more": has_more,
                "returned_count": len(products),
                "total_count_estimate": None,  # 大規模データでは推定値のみ返す
            },
        }

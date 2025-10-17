"""
products/router.py - 商品APIエンドポイント
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.database.db import get_session
from app.database.models.user import User
from app.products.schemas import ProductCreate, ProductListParams, ProductResponse, ProductUpdate
from app.products.service import ProductsService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session),
) -> ProductResponse:
    """商品を作成（認証必須）

    認証されたユーザーのみが商品を作成できます。
    user_idは自動的に認証ユーザーのIDが使用されます。
    """
    service = ProductsService(db)
    product = await service.create_product(product_data, current_user.id)
    return ProductResponse.model_validate(product)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_session),
) -> ProductResponse:
    """商品を取得"""
    service = ProductsService(db)
    product = await service.get_product_by_id(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品が見つかりません",
        )

    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_session),
) -> ProductResponse:
    """商品を更新"""
    service = ProductsService(db)

    try:
        product = await service.update_product(product_id, product_data)
        return ProductResponse.model_validate(product)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_session),
) -> None:
    """商品を削除"""
    service = ProductsService(db)

    try:
        await service.delete_product(product_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get("/", response_model=dict)
async def list_products(
    category: str | None = Query(None, description="カテゴリでフィルタ"),
    status_filter: str | None = Query(None, alias="status", description="ステータスでフィルタ"),
    search: str | None = Query(None, description="名前または説明で検索"),
    sort_by: str = Query("created_at", description="ソートフィールド"),
    sort_order: str = Query("desc", description="ソート順序 (asc/desc)"),
    limit: int = Query(100, ge=1, le=1000, description="取得件数"),
    cursor: str | None = Query(None, description="ページネーションカーソル"),
    date_from: str | None = Query(None, description="開始日時 (ISO 8601)"),
    date_to: str | None = Query(None, description="終了日時 (ISO 8601)"),
    db: AsyncSession = Depends(get_session),
) -> dict:
    """商品リストを取得（カーソルベースページネーション）"""
    from datetime import datetime

    # 日付文字列をdatetimeに変換
    date_from_dt = datetime.fromisoformat(date_from) if date_from else None
    date_to_dt = datetime.fromisoformat(date_to) if date_to else None

    params = ProductListParams(
        category=category,
        status=status_filter,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        cursor=cursor,
        date_from=date_from_dt,
        date_to=date_to_dt,
    )

    service = ProductsService(db)
    result = await service.list_products(params)

    # ProductResponseに変換
    items = [ProductResponse.model_validate(item) for item in result["items"]]

    return {
        "items": items,
        "pagination": result["pagination"],
    }

"""
products/schemas.py - 商品関連のPydanticスキーマ
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBase(BaseModel):
    """商品基本スキーマ"""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category: str = Field(..., min_length=1, max_length=100)
    status: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)


class ProductCreate(ProductBase):
    """商品作成スキーマ"""

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """ステータスの検証"""
        allowed_statuses = ["active", "inactive", "draft", "archived"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return v


class ProductUpdate(BaseModel):
    """商品更新スキーマ"""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(None, min_length=1, max_length=100)
    status: str | None = Field(None, min_length=1, max_length=50)
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """ステータスの検証"""
        if v is not None:
            allowed_statuses = ["active", "inactive", "draft", "archived"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of {allowed_statuses}")
        return v


class ProductResponse(ProductBase):
    """商品レスポンススキーマ"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None
    created_at: datetime
    updated_at: datetime


class ProductListParams(BaseModel):
    """商品リストクエリパラメータ"""

    limit: int = Field(default=100, ge=1, le=100)
    cursor: str | None = None
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc")
    search: str | None = None
    category: str | None = None
    status: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        """ソートフィールドの検証"""
        allowed_fields = ["created_at", "name", "price", "updated_at"]
        if v not in allowed_fields:
            raise ValueError(f"sort_by must be one of {allowed_fields}")
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        """ソート順の検証"""
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v


class PaginationMeta(BaseModel):
    """ページネーションメタデータ"""

    next_cursor: str | None
    has_more: bool
    returned_count: int
    total_count_estimate: int | None = None


class ProductListResponse(BaseModel):
    """商品リストレスポンス"""

    items: list[ProductResponse]
    pagination: PaginationMeta

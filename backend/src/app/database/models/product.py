"""
database/models/product.py - 商品モデル（1000万件対応）
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


def utc_now():
    """UTC現在時刻を返す"""
    return datetime.now(UTC)


class Product(Base):
    """商品テーブル（1000万件対応）"""

    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        # 無限スクロール最適化
        Index("idx_products_created_at_desc", "created_at", postgresql_using="desc"),
        Index("idx_products_created_at_id", "created_at", "id"),
        # フィルタリング最適化
        Index("idx_products_category_status", "category", "status"),
        Index("idx_products_category", "category"),
        Index("idx_products_status", "status"),
        # ユーザー検索
        Index("idx_products_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name}, category={self.category})>"

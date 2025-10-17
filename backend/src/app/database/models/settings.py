"""
database/models/settings.py - ユーザー設定モデル
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


def utc_now():
    """UTC現在時刻を返す"""
    return datetime.now(UTC)


class UserSettings(Base):
    """ユーザー設定テーブル"""

    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    theme = Column(String(20), default="light", nullable=False)
    default_page_size = Column(Integer, default=100, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", name="unique_user_settings"),
        Index("idx_user_settings_user_id", "user_id"),
    )

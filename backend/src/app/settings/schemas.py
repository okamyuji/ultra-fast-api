"""
settings/schemas.py - ユーザー設定スキーマ
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ユーザー設定スキーマ
class UserSettingsBase(BaseModel):
    """ユーザー設定基本スキーマ"""

    theme: str = Field(default="light", description="テーマ (light/dark)")
    default_page_size: int = Field(default=100, ge=10, le=100, description="デフォルトページサイズ")


class UserSettingsCreate(UserSettingsBase):
    """ユーザー設定作成スキーマ"""

    pass


class UserSettingsUpdate(BaseModel):
    """ユーザー設定更新スキーマ"""

    theme: str | None = Field(None, description="テーマ (light/dark)")
    default_page_size: int | None = Field(None, ge=10, le=100, description="デフォルトページサイズ")


class UserSettingsResponse(UserSettingsBase):
    """ユーザー設定レスポンススキーマ"""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# プロフィール更新スキーマ
class ProfileUpdate(BaseModel):
    """プロフィール更新スキーマ"""

    username: str | None = Field(None, min_length=3, max_length=255, description="ユーザー名")
    email: str | None = Field(None, description="メールアドレス")


# デバイス情報スキーマ
class DeviceInfo(BaseModel):
    """デバイス情報スキーマ"""

    id: UUID
    device_id: str
    device_name: str | None
    device_type: str | None
    last_used_at: datetime
    created_at: datetime
    is_current: bool = False

    model_config = ConfigDict(from_attributes=True)


class DeviceListResponse(BaseModel):
    """デバイス一覧レスポンス"""

    devices: list[DeviceInfo]

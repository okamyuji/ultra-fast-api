"""
auth/schemas.py - 認証関連のPydanticスキーマ（TDD用）
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """ユーザー基本スキーマ"""

    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr


class UserRegisterSchema(UserBase):
    """ユーザー登録スキーマ"""

    password: str = Field(..., min_length=8, max_length=255)


class UserLoginSchema(BaseModel):
    """ログインスキーマ"""

    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., description="パスワード")


class UserResponse(UserBase):
    """ユーザーレスポンススキーマ"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AuthTokens(BaseModel):
    """認証トークンレスポンス"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenRefresh(BaseModel):
    """トークンリフレッシュスキーマ"""

    refresh_token: str


class PasswordResetRequest(BaseModel):
    """パスワードリセットリクエスト"""

    email: EmailStr


class PasswordReset(BaseModel):
    """パスワードリセット実行スキーマ"""

    token: str
    new_password: str = Field(..., min_length=8, max_length=255)


class PasswordChange(BaseModel):
    """パスワード変更スキーマ"""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=255)


class PasswordResetConfirm(BaseModel):
    """パスワードリセット確認スキーマ"""

    token: str
    new_password: str = Field(..., min_length=8, max_length=255)

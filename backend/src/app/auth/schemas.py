"""
auth/schemas.py - 認証関連のPydanticスキーマ（TDD用）
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field

from app.auth.security import BCRYPT_MAX_BYTES


def _fits_bcrypt(value: str) -> str:
    if len(value.encode()) > BCRYPT_MAX_BYTES:
        raise ValueError(f"パスワードは {BCRYPT_MAX_BYTES} バイト以内にしてください")
    return value


Password = Annotated[str, Field(min_length=8, max_length=255), AfterValidator(_fits_bcrypt)]


class UserBase(BaseModel):
    """ユーザー基本スキーマ"""

    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr


class UserRegisterSchema(UserBase):
    """ユーザー登録スキーマ"""

    password: Password


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
    new_password: Password


class PasswordChange(BaseModel):
    """パスワード変更スキーマ"""

    current_password: str
    new_password: Password


class PasswordResetConfirm(BaseModel):
    """パスワードリセット確認スキーマ"""

    token: str
    new_password: Password

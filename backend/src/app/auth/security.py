"""
auth/security.py - JWT・パスワードハッシング処理
"""

from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# パスワードハッシング設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """パスワードをbcryptでハッシング"""
    return cast(str, pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワード検証"""
    return cast(bool, pwd_context.verify(plain_password, hashed_password))


def create_jwt_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """JWT トークンを生成

    Args:
        data: トークンに含めるペイロード
        expires_delta: 有効期限

    Returns:
        JWT トークン文字列
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(hours=24)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return cast(str, encoded_jwt)


def decode_jwt_token(token: str) -> dict[str, Any]:
    """JWT トークンをデコード

    Args:
        token: JWT トークン文字列

    Returns:
        デコードされたペイロード

    Raises:
        ValueError: トークンが無効または期限切れの場合
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return cast(dict[str, Any], payload)
    except JWTError as e:
        raise ValueError(f"トークンが無効です: {str(e)}") from e


def create_access_token(
    user_id: UUID,
    username: str,
    expires_delta: timedelta | None = None,
) -> tuple[str, int]:
    """アクセストークンを生成

    Args:
        user_id: ユーザーID
        username: ユーザー名
        expires_delta: 有効期限

    Returns:
        (トークン, 有効期限秒数)のタプル
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.access_token_expire_hours)

    to_encode = {
        "sub": str(user_id),
        "username": username,
        "token_type": "access",
    }

    token = create_jwt_token(to_encode, expires_delta)
    expires_in_seconds = int(expires_delta.total_seconds())

    return token, expires_in_seconds


def create_refresh_token(
    user_id: UUID,
    device_id: str,
    expires_delta: timedelta | None = None,
) -> str:
    """リフレッシュトークンを生成

    Args:
        user_id: ユーザーID
        device_id: デバイスID
        expires_delta: 有効期限

    Returns:
        JWT リフレッシュトークン
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.refresh_token_expire_days)

    to_encode = {
        "sub": str(user_id),
        "device_id": device_id,
        "token_type": "refresh",
    }

    return create_jwt_token(to_encode, expires_delta)


def verify_access_token(token: str) -> dict[str, Any] | None:
    """アクセストークンを検証

    Args:
        token: JWT トークン

    Returns:
        検証成功時はペイロード、失敗時は None
    """
    try:
        payload = decode_jwt_token(token)
        token_type = payload.get("token_type")

        if token_type != "access":
            return None

        return payload
    except ValueError:
        return None


def verify_refresh_token(token: str) -> dict[str, Any] | None:
    """リフレッシュトークンを検証

    Args:
        token: JWT リフレッシュトークン

    Returns:
        検証成功時はペイロード、失敗時は None
    """
    try:
        payload = decode_jwt_token(token)
        token_type = payload.get("token_type")

        if token_type != "refresh":
            return None

        return payload
    except ValueError:
        return None

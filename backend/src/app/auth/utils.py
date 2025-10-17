"""
認証ユーティリティ関数
"""

from typing import cast

from passlib.context import CryptContext

# パスワードハッシング設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """パスワードをハッシュ化する"""
    return cast(str, pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワードを検証する"""
    return cast(bool, pwd_context.verify(plain_password, hashed_password))

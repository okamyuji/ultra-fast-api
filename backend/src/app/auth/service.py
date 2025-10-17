"""
auth/service.py - 認証ビジネスロジック（TDD実装）
"""

import re
from datetime import UTC, datetime, timedelta
from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import UserLoginSchema, UserRegisterSchema
from app.auth.security import create_jwt_token, hash_password, verify_access_token, verify_password
from app.config import settings
from app.database.models.token import PasswordResetToken, RefreshToken
from app.database.models.user import User


class AuthService:
    """認証サービス"""

    def __init__(self, db_session: AsyncSession):
        """初期化"""
        self.db = db_session

    # ーーーーーー パスワード検証 ーーーーーー

    @staticmethod
    def _validate_password(password: str) -> bool:
        """
        パスワード要件を検証
        - 最小8文字
        - 大文字を含む
        - 小文字を含む
        - 数字を含む
        - 特殊文字を含む
        """
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[!@#$%^&*()_\-+=\[\]{}|;:',.<>?/`~]", password):
            return False
        return True

    # ーーーーーー ユーザー登録 ーーーーーー

    async def register_user(self, schema: UserRegisterSchema) -> User:
        """ユーザーを登録"""
        # パスワード要件の検証
        if not self._validate_password(schema.password):
            raise ValueError("パスワードが要件を満たしていません")

        # ユーザー名の重複チェック
        existing_user = await self.get_user_by_username(schema.username)
        if existing_user:
            raise ValueError("ユーザー名は既に使用されています")

        # メールアドレスの重複チェック
        existing_email = await self.get_user_by_email(schema.email)
        if existing_email:
            raise ValueError("メールアドレスは既に使用されています")

        # ユーザー作成
        new_user = User(
            username=schema.username,
            email=schema.email,
            password_hash=hash_password(schema.password),
            is_active=True,
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user

    # ーーーーーー ユーザー取得 ーーーーーー

    async def get_user_by_username(self, username: str) -> User | None:
        """ユーザー名でユーザーを取得"""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """IDでユーザーを取得"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> User | None:
        """メールアドレスでユーザーを取得"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    # ーーーーーー ログイン ーーーーーー

    async def login_user(self, schema: UserLoginSchema) -> User:
        """ユーザーをログイン"""
        user = await self.get_user_by_email(schema.email)

        if not user:
            raise ValueError("メールアドレスまたはパスワードが不正です")

        if not verify_password(schema.password, user.password_hash):
            raise ValueError("メールアドレスまたはパスワードが不正です")

        if not user.is_active:
            raise ValueError("ユーザーが無効化されています")

        return user

    # ーーーーーー JWTトークン ーーーーーー

    def create_access_token(self, user_id: str, expires_delta: timedelta | None = None) -> str:
        """アクセストークンを作成"""
        if expires_delta is None:
            expires_delta = timedelta(hours=settings.access_token_expire_hours)

        return cast(
            str, create_jwt_token(data={"sub": str(user_id), "token_type": "access"}, expires_delta=expires_delta)
        )

    def create_refresh_token(self, user_id: str, device_id: str, expires_delta: timedelta | None = None) -> str:
        """リフレッシュトークンを作成"""
        if expires_delta is None:
            expires_delta = timedelta(days=settings.refresh_token_expire_days)

        return cast(
            str,
            create_jwt_token(
                data={"sub": str(user_id), "device_id": device_id, "token_type": "refresh"}, expires_delta=expires_delta
            ),
        )

    def verify_token(self, token: str) -> dict:
        """トークンを検証して ペイロードを取得"""
        from src.app.auth.security import decode_jwt_token

        return decode_jwt_token(token)

    # ーーーーーー パスワード変更 ーーーーーー

    async def change_password(self, user_id: UUID, current_password: str, new_password: str) -> User:
        """パスワードを変更"""
        # ユーザー取得
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("ユーザーが見つかりません")

        # 現在のパスワード検証
        if not verify_password(current_password, user.password_hash):
            raise ValueError("現在のパスワードが不正です")

        # 新しいパスワード要件の検証
        if not self._validate_password(new_password):
            raise ValueError("新しいパスワードが要件を満たしていません")

        # パスワード更新
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.now(UTC)

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    # ーーーーーー トークンリフレッシュ ーーーーーー

    async def refresh_access_token(self, refresh_token_str: str) -> tuple[str, str]:
        """
        リフレッシュトークンから新しいアクセストークンとリフレッシュトークンを生成

        Returns:
            tuple[str, str]: (新しいアクセストークン, 新しいリフレッシュトークン)
        """
        # リフレッシュトークンを検証
        try:
            payload = verify_access_token(refresh_token_str)
        except ValueError as e:
            raise ValueError(f"無効なリフレッシュトークンです: {e}") from e

        # トークンタイプを確認
        if payload.get("token_type") != "refresh":
            raise ValueError("リフレッシュトークンではありません")

        user_id = payload.get("sub")
        device_id = payload.get("device_id")

        if not user_id or not device_id:
            raise ValueError("トークンに必要な情報が含まれていません")

        # ユーザーが存在するか確認
        user = await self.get_user_by_id(UUID(user_id))
        if not user or not user.is_active:
            raise ValueError("ユーザーが見つからないか無効です")

        # DBのリフレッシュトークンを確認
        token_hash = hash_password(refresh_token_str)
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user.id)
            .where(RefreshToken.token_hash == token_hash)
            .where(RefreshToken.revoked_at.is_(None))
        )
        db_token = result.scalars().first()

        if not db_token:
            raise ValueError("リフレッシュトークンが見つからないか無効です")

        # トークンの有効期限確認
        if db_token.expires_at < datetime.now(UTC):
            raise ValueError("リフレッシュトークンの有効期限が切れています")

        # 古いトークンを無効化
        db_token.revoked_at = datetime.now(UTC)

        # 新しいトークンを生成
        new_access_token = self.create_access_token(str(user.id))
        new_refresh_token = self.create_refresh_token(str(user.id), device_id)

        # 新しいリフレッシュトークンをDBに保存
        new_db_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_password(new_refresh_token),
            device_id=device_id,
            device_name=db_token.device_name,
            device_type=db_token.device_type,
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
            last_used_at=datetime.now(UTC),
        )

        self.db.add(new_db_token)
        await self.db.commit()

        return new_access_token, new_refresh_token

    # ーーーーーー ログアウト ーーーーーー

    async def logout(self, user_id: UUID, device_id: str | None = None) -> bool:
        """
        ログアウト（リフレッシュトークンを無効化）

        Args:
            user_id: ユーザーID
            device_id: デバイスID（指定しない場合は全デバイス）

        Returns:
            bool: 成功した場合True
        """
        query = select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))

        if device_id:
            query = query.where(RefreshToken.device_id == device_id)

        result = await self.db.execute(query)
        tokens = result.scalars().all()

        if not tokens:
            return False

        # すべてのトークンを無効化
        for token in tokens:
            token.revoked_at = datetime.now(UTC)

        await self.db.commit()
        return True

    # ーーーーーー パスワードリセット ーーーーーー

    async def request_password_reset(self, email: str) -> str:
        """
        パスワードリセットトークンを生成

        Args:
            email: メールアドレス

        Returns:
            str: リセットトークン

        Note:
            実際のメール送信は実装されていません（本番環境では実装が必要）
        """
        user = await self.get_user_by_email(email)
        if not user:
            # セキュリティのため、ユーザーが存在しなくても同じレスポンスを返す
            # 実際の実装では何も行わない
            return "dummy_token"

        # 既存の未使用トークンを無効化
        result = await self.db.execute(
            select(PasswordResetToken)
            .where(PasswordResetToken.user_id == user.id)
            .where(PasswordResetToken.used_at.is_(None))
        )
        existing_tokens = result.scalars().all()
        for token in existing_tokens:
            token.used_at = datetime.now(UTC)

        # リセットトークンを生成（1時間有効）
        import secrets

        reset_token = secrets.token_urlsafe(32)
        token_hash = hash_password(reset_token)

        # DBに保存
        db_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )

        self.db.add(db_token)
        await self.db.commit()

        # 本番環境ではここでメール送信処理を行う
        # send_password_reset_email(user.email, reset_token)

        return reset_token

    async def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """
        パスワードリセットトークンを検証して新しいパスワードを設定

        Args:
            token: リセットトークン
            new_password: 新しいパスワード

        Returns:
            bool: 成功した場合True
        """
        # パスワード要件の検証
        if not self._validate_password(new_password):
            raise ValueError("新しいパスワードが要件を満たしていません")

        # トークンハッシュを生成
        token_hash = hash_password(token)

        # DBからトークンを検索
        result = await self.db.execute(
            select(PasswordResetToken)
            .where(PasswordResetToken.token_hash == token_hash)
            .where(PasswordResetToken.used_at.is_(None))
        )
        db_token = result.scalars().first()

        if not db_token:
            raise ValueError("無効または期限切れのリセットトークンです")

        # 有効期限確認
        if db_token.expires_at < datetime.now(UTC):
            raise ValueError("リセットトークンの有効期限が切れています")

        # ユーザーを取得
        user = await self.get_user_by_id(db_token.user_id)
        if not user:
            raise ValueError("ユーザーが見つかりません")

        # パスワードを更新
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.now(UTC)

        # トークンを使用済みにする
        db_token.used_at = datetime.now(UTC)

        await self.db.commit()
        return True

    # ーーーーーー ユーザー情報更新 ーーーーーー

    async def update_user_profile(self, user_id: UUID, username: str | None = None, email: str | None = None) -> User:
        """ユーザープロフィールを更新"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("ユーザーが見つかりません")

        # ユーザー名変更時
        if username and username != user.username:
            existing_user = await self.get_user_by_username(username)
            if existing_user:
                raise ValueError("ユーザー名は既に使用されています")
            user.username = username

        # メールアドレス変更時
        if email and email != user.email:
            existing_user = await self.get_user_by_email(email)
            if existing_user:
                raise ValueError("メールアドレスは既に使用されています")
            user.email = email

        user.updated_at = datetime.now(UTC)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

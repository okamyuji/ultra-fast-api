"""
settings/service.py - ユーザー設定サービス
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.settings import UserSettings
from app.database.models.token import RefreshToken
from app.database.models.user import User
from app.settings.schemas import ProfileUpdate, UserSettingsCreate, UserSettingsUpdate


class SettingsService:
    """ユーザー設定サービス"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ーーーーーー 設定管理 ーーーーーー

    async def get_user_settings(self, user_id: UUID) -> UserSettings | None:
        """ユーザー設定を取得"""
        result = await self.db.execute(select(UserSettings).where(UserSettings.user_id == user_id))
        return result.scalars().first()

    async def create_user_settings(self, user_id: UUID, schema: UserSettingsCreate) -> UserSettings:
        """ユーザー設定を作成"""
        settings = UserSettings(
            user_id=user_id,
            theme=schema.theme,
            default_page_size=schema.default_page_size,
        )

        self.db.add(settings)
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def get_or_create_user_settings(self, user_id: UUID) -> UserSettings:
        """ユーザー設定を取得、存在しない場合は作成"""
        settings = await self.get_user_settings(user_id)
        if not settings:
            settings = await self.create_user_settings(user_id, UserSettingsCreate())
        return settings

    async def update_user_settings(self, user_id: UUID, schema: UserSettingsUpdate) -> UserSettings:
        """ユーザー設定を更新"""
        settings = await self.get_or_create_user_settings(user_id)

        # 更新対象のフィールドのみ更新
        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)

        settings.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    # ーーーーーー プロフィール管理 ーーーーーー

    async def update_profile(self, user_id: UUID, schema: ProfileUpdate) -> User:
        """プロフィールを更新"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise ValueError("ユーザーが見つかりません")

        # 更新対象のフィールドのみ更新
        update_data = schema.model_dump(exclude_unset=True)

        # ユーザー名の重複チェック
        if "username" in update_data and update_data["username"] != user.username:
            existing_user = await self.db.execute(select(User).where(User.username == update_data["username"]))
            if existing_user.scalars().first():
                raise ValueError("このユーザー名は既に使用されています")

        # メールアドレスの重複チェック
        if "email" in update_data and update_data["email"] != user.email:
            existing_user = await self.db.execute(select(User).where(User.email == update_data["email"]))
            if existing_user.scalars().first():
                raise ValueError("このメールアドレスは既に使用されています")

        # 更新実行
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    # ーーーーーー デバイス管理 ーーーーーー

    async def get_user_devices(self, user_id: UUID) -> list[RefreshToken]:
        """ユーザーのデバイス一覧を取得"""
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.revoked_at.is_(None))
            .where(RefreshToken.expires_at > datetime.now(UTC))
            .order_by(RefreshToken.last_used_at.desc())
        )
        return list(result.scalars().all())

    async def revoke_device(self, user_id: UUID, device_id: str) -> bool:
        """デバイスを無効化（リフレッシュトークンを無効化）"""
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.device_id == device_id)
            .where(RefreshToken.revoked_at.is_(None))
        )
        tokens = result.scalars().all()

        if not tokens:
            raise ValueError("デバイスが見つかりません")

        # すべてのトークンを無効化
        for token in tokens:
            token.revoked_at = datetime.now(UTC)

        await self.db.commit()
        return True

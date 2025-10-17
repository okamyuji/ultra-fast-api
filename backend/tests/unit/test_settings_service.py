"""
tests/unit/test_settings_service.py - SettingsService ユニットテスト
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.settings import UserSettings
from app.database.models.token import RefreshToken
from app.database.models.user import User
from app.settings.schemas import ProfileUpdate, UserSettingsCreate, UserSettingsUpdate
from app.settings.service import SettingsService


class TestSettingsService:
    """SettingsService テストクラス"""

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> User:
        """テスト用ユーザーを作成"""
        user = User(
            username="settingsuser",
            email="settings@example.com",
            password_hash="hashed_password",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def test_settings(self, db_session: AsyncSession, test_user: User) -> UserSettings:
        """テスト用ユーザー設定を作成"""
        settings = UserSettings(
            user_id=test_user.id,
            theme="dark",
            default_page_size=50,
        )
        db_session.add(settings)
        await db_session.commit()
        await db_session.refresh(settings)
        return settings

    # ーーーーーー 設定管理テスト ーーーーーー

    async def test_get_user_settings(self, db_session: AsyncSession, test_user: User, test_settings: UserSettings):
        """ユーザー設定取得テスト"""
        service = SettingsService(db_session)
        settings = await service.get_user_settings(test_user.id)

        assert settings is not None
        assert settings.user_id == test_user.id
        assert settings.theme == "dark"
        assert settings.default_page_size == 50

    async def test_get_user_settings_not_found(self, db_session: AsyncSession):
        """存在しないユーザー設定取得テスト"""
        service = SettingsService(db_session)
        settings = await service.get_user_settings(uuid4())

        assert settings is None

    async def test_create_user_settings(self, db_session: AsyncSession, test_user: User):
        """ユーザー設定作成テスト"""
        service = SettingsService(db_session)
        schema = UserSettingsCreate(theme="light", default_page_size=100)

        # 既存設定を削除（test_settingsフィクスチャの影響を受けないため）
        await db_session.execute(select(UserSettings).where(UserSettings.user_id == test_user.id))
        existing = await db_session.execute(select(UserSettings).where(UserSettings.user_id == test_user.id))
        for s in existing.scalars():
            await db_session.delete(s)
        await db_session.commit()

        settings = await service.create_user_settings(test_user.id, schema)

        assert settings.user_id == test_user.id
        assert settings.theme == "light"
        assert settings.default_page_size == 100
        assert settings.created_at is not None
        assert settings.updated_at is not None

    async def test_get_or_create_user_settings_existing(
        self, db_session: AsyncSession, test_user: User, test_settings: UserSettings
    ):
        """ユーザー設定取得または作成テスト（既存）"""
        service = SettingsService(db_session)
        settings = await service.get_or_create_user_settings(test_user.id)

        assert settings.id == test_settings.id
        assert settings.theme == "dark"

    async def test_get_or_create_user_settings_new(self, db_session: AsyncSession):
        """ユーザー設定取得または作成テスト（新規）"""
        # 新しいユーザーを作成
        user = User(username="newuser", email="newuser@example.com", password_hash="hash")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        service = SettingsService(db_session)
        settings = await service.get_or_create_user_settings(user.id)

        assert settings.user_id == user.id
        assert settings.theme == "light"  # デフォルト値

    async def test_update_user_settings(self, db_session: AsyncSession, test_user: User, test_settings: UserSettings):
        """ユーザー設定更新テスト"""
        service = SettingsService(db_session)
        schema = UserSettingsUpdate(theme="light", default_page_size=75)

        settings = await service.update_user_settings(test_user.id, schema)

        assert settings.theme == "light"
        assert settings.default_page_size == 75

    async def test_update_user_settings_partial(
        self, db_session: AsyncSession, test_user: User, test_settings: UserSettings
    ):
        """ユーザー設定部分更新テスト"""
        service = SettingsService(db_session)
        schema = UserSettingsUpdate(theme="light")

        settings = await service.update_user_settings(test_user.id, schema)

        assert settings.theme == "light"
        # 他のフィールドは変更されていないはず
        assert settings.default_page_size == 50

    # ーーーーーー プロフィール管理テスト ーーーーーー

    async def test_update_profile_username(self, db_session: AsyncSession, test_user: User):
        """プロフィール更新（ユーザー名）テスト"""
        service = SettingsService(db_session)
        schema = ProfileUpdate(username="updateduser")

        user = await service.update_profile(test_user.id, schema)

        assert user.username == "updateduser"
        assert user.email == test_user.email  # メールは変更されていない

    async def test_update_profile_email(self, db_session: AsyncSession, test_user: User):
        """プロフィール更新（メールアドレス）テスト"""
        service = SettingsService(db_session)
        schema = ProfileUpdate(email="newemail@example.com")

        user = await service.update_profile(test_user.id, schema)

        assert user.email == "newemail@example.com"
        assert user.username == test_user.username  # ユーザー名は変更されていない

    async def test_update_profile_both(self, db_session: AsyncSession, test_user: User):
        """プロフィール更新（両方）テスト"""
        service = SettingsService(db_session)
        schema = ProfileUpdate(username="newusername", email="newmail@example.com")

        user = await service.update_profile(test_user.id, schema)

        assert user.username == "newusername"
        assert user.email == "newmail@example.com"

    async def test_update_profile_duplicate_username(self, db_session: AsyncSession, test_user: User):
        """プロフィール更新（重複ユーザー名）テスト"""
        # 別のユーザーを作成
        other_user = User(username="existinguser", email="existing@example.com", password_hash="hash")
        db_session.add(other_user)
        await db_session.commit()

        service = SettingsService(db_session)
        schema = ProfileUpdate(username="existinguser")

        with pytest.raises(ValueError, match="このユーザー名は既に使用されています"):
            await service.update_profile(test_user.id, schema)

    async def test_update_profile_duplicate_email(self, db_session: AsyncSession, test_user: User):
        """プロフィール更新（重複メールアドレス）テスト"""
        # 別のユーザーを作成
        other_user = User(username="otheruser", email="existing@example.com", password_hash="hash")
        db_session.add(other_user)
        await db_session.commit()

        service = SettingsService(db_session)
        schema = ProfileUpdate(email="existing@example.com")

        with pytest.raises(ValueError, match="このメールアドレスは既に使用されています"):
            await service.update_profile(test_user.id, schema)

    async def test_update_profile_user_not_found(self, db_session: AsyncSession):
        """プロフィール更新（ユーザー存在しない）テスト"""
        service = SettingsService(db_session)
        schema = ProfileUpdate(username="newname")

        with pytest.raises(ValueError, match="ユーザーが見つかりません"):
            await service.update_profile(uuid4(), schema)

    # ーーーーーー デバイス管理テスト ーーーーーー

    async def test_get_user_devices(self, db_session: AsyncSession, test_user: User):
        """ユーザーデバイス一覧取得テスト"""
        # テスト用デバイスを作成
        device1 = RefreshToken(
            user_id=test_user.id,
            token_hash="hash1",
            device_id="device-001",
            device_name="iPhone 14",
            device_type="ios",
            expires_at=datetime.now(UTC) + timedelta(days=30),
            last_used_at=datetime.now(UTC),
        )
        device2 = RefreshToken(
            user_id=test_user.id,
            token_hash="hash2",
            device_id="device-002",
            device_name="MacBook Pro",
            device_type="macos",
            expires_at=datetime.now(UTC) + timedelta(days=30),
            last_used_at=datetime.now(UTC) - timedelta(hours=1),
        )
        db_session.add_all([device1, device2])
        await db_session.commit()

        service = SettingsService(db_session)
        devices = await service.get_user_devices(test_user.id)

        assert len(devices) == 2
        # last_used_at の降順でソートされているはず
        assert devices[0].device_id == "device-001"
        assert devices[1].device_id == "device-002"

    async def test_get_user_devices_exclude_revoked(self, db_session: AsyncSession, test_user: User):
        """ユーザーデバイス一覧取得（無効化済み除外）テスト"""
        # 有効なデバイス
        device1 = RefreshToken(
            user_id=test_user.id,
            token_hash="hash1",
            device_id="device-001",
            expires_at=datetime.now(UTC) + timedelta(days=30),
            last_used_at=datetime.now(UTC),
        )
        # 無効化済みデバイス
        device2 = RefreshToken(
            user_id=test_user.id,
            token_hash="hash2",
            device_id="device-002",
            expires_at=datetime.now(UTC) + timedelta(days=30),
            last_used_at=datetime.now(UTC),
            revoked_at=datetime.now(UTC),
        )
        db_session.add_all([device1, device2])
        await db_session.commit()

        service = SettingsService(db_session)
        devices = await service.get_user_devices(test_user.id)

        assert len(devices) == 1
        assert devices[0].device_id == "device-001"

    async def test_get_user_devices_exclude_expired(self, db_session: AsyncSession, test_user: User):
        """ユーザーデバイス一覧取得（期限切れ除外）テスト"""
        # 有効なデバイス
        device1 = RefreshToken(
            user_id=test_user.id,
            token_hash="hash1",
            device_id="device-001",
            expires_at=datetime.now(UTC) + timedelta(days=30),
            last_used_at=datetime.now(UTC),
        )
        # 期限切れデバイス
        device2 = RefreshToken(
            user_id=test_user.id,
            token_hash="hash2",
            device_id="device-002",
            expires_at=datetime.now(UTC) - timedelta(days=1),
            last_used_at=datetime.now(UTC),
        )
        db_session.add_all([device1, device2])
        await db_session.commit()

        service = SettingsService(db_session)
        devices = await service.get_user_devices(test_user.id)

        assert len(devices) == 1
        assert devices[0].device_id == "device-001"

    async def test_revoke_device(self, db_session: AsyncSession, test_user: User):
        """デバイス無効化テスト"""
        # テスト用デバイスを作成
        device = RefreshToken(
            user_id=test_user.id,
            token_hash="hash1",
            device_id="device-001",
            expires_at=datetime.now(UTC) + timedelta(days=30),
            last_used_at=datetime.now(UTC),
        )
        db_session.add(device)
        await db_session.commit()

        service = SettingsService(db_session)
        result = await service.revoke_device(test_user.id, "device-001")

        assert result is True

        # デバイスが無効化されていることを確認
        await db_session.refresh(device)
        assert device.revoked_at is not None

    async def test_revoke_device_not_found(self, db_session: AsyncSession, test_user: User):
        """デバイス無効化（存在しない）テスト"""
        service = SettingsService(db_session)

        with pytest.raises(ValueError, match="デバイスが見つかりません"):
            await service.revoke_device(test_user.id, "nonexistent-device")

    async def test_revoke_device_multiple_tokens(self, db_session: AsyncSession, test_user: User):
        """デバイス無効化（複数トークン）テスト"""
        # 同じdevice_idで複数のトークンを作成
        device1 = RefreshToken(
            user_id=test_user.id,
            token_hash="hash1",
            device_id="device-001",
            expires_at=datetime.now(UTC) + timedelta(days=30),
            last_used_at=datetime.now(UTC),
        )
        device2 = RefreshToken(
            user_id=test_user.id,
            token_hash="hash2",
            device_id="device-001",
            expires_at=datetime.now(UTC) + timedelta(days=30),
            last_used_at=datetime.now(UTC),
        )
        db_session.add_all([device1, device2])
        await db_session.commit()

        service = SettingsService(db_session)
        result = await service.revoke_device(test_user.id, "device-001")

        assert result is True

        # 両方のトークンが無効化されていることを確認
        await db_session.refresh(device1)
        await db_session.refresh(device2)
        assert device1.revoked_at is not None
        assert device2.revoked_at is not None

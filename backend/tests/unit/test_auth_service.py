"""
unit/test_auth_service.py - 認証サービスのユニットテスト（TDD）
"""

from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import UserLoginSchema, UserRegisterSchema
from app.auth.service import AuthService
from app.auth.utils import verify_password
from app.database.models.user import User


class TestAuthService:
    """認証サービスのテストクラス"""

    @pytest.fixture
    async def auth_service(self, db_session: AsyncSession):
        """認証サービスのインスタンスを作成"""
        return AuthService(db_session)

    @pytest.fixture
    async def test_user_data(self):
        """テストユーザーのデータ"""
        return {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePassword123!",
        }

    # ーーーーーー ユーザー登録テスト ーーーーーー

    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, test_user_data, db_session):
        """ユーザー登録成功のテスト"""
        # Arrange
        register_schema = UserRegisterSchema(**test_user_data)

        # Act
        user = await auth_service.register_user(register_schema)

        # Assert
        assert user.id is not None
        assert user.username == test_user_data["username"]
        assert user.email == test_user_data["email"]
        assert user.is_active is True
        assert verify_password(test_user_data["password"], user.password_hash)

        # DB確認
        result = await db_session.execute(select(User).where(User.username == test_user_data["username"]))
        db_user = result.scalars().first()
        assert db_user is not None

    @pytest.mark.asyncio
    async def test_register_user_duplicate_username(self, auth_service, test_user_data):
        """ユーザー名重複時のテスト"""
        # Arrange
        register_schema = UserRegisterSchema(**test_user_data)
        await auth_service.register_user(register_schema)

        # Act & Assert
        with pytest.raises(ValueError, match="ユーザー名は既に使用されています"):
            await auth_service.register_user(register_schema)

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, auth_service, test_user_data):
        """メールアドレス重複時のテスト"""
        # Arrange
        register_schema = UserRegisterSchema(**test_user_data)
        await auth_service.register_user(register_schema)

        # Act & Assert
        duplicate_data = {
            "username": "newuser",
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }
        with pytest.raises(ValueError, match="メールアドレスは既に使用されています"):
            await auth_service.register_user(UserRegisterSchema(**duplicate_data))

    @pytest.mark.asyncio
    async def test_register_user_weak_password(self, auth_service):
        """弱いパスワードでの登録テスト"""
        # Arrange - 長さは8文字以上だが、その他の要件を満たさない
        weak_password_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "weakpass",  # 大文字・数字・特殊文字なし
        }
        register_schema = UserRegisterSchema(**weak_password_data)

        # Act & Assert
        with pytest.raises(ValueError, match="パスワードが要件を満たしていません"):
            await auth_service.register_user(register_schema)

    # ーーーーーー ユーザーログインテスト ーーーーーー

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service, test_user_data):
        """ログイン成功のテスト"""
        # Arrange
        register_schema = UserRegisterSchema(**test_user_data)
        await auth_service.register_user(register_schema)

        # Act
        login_schema = UserLoginSchema(
            email=test_user_data["email"],
            password=test_user_data["password"],
        )
        user = await auth_service.login_user(login_schema)

        # Assert
        assert user is not None
        assert user.username == test_user_data["username"]

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, auth_service):
        """存在しないメールアドレスでのログインテスト"""
        # Arrange
        login_schema = UserLoginSchema(
            email="nonexistent@example.com",
            password="Password123!",
        )

        # Act & Assert
        with pytest.raises(ValueError, match="メールアドレスまたはパスワードが不正です"):
            await auth_service.login_user(login_schema)

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, auth_service, test_user_data):
        """不正なパスワードでのログインテスト"""
        # Arrange
        register_schema = UserRegisterSchema(**test_user_data)
        await auth_service.register_user(register_schema)

        # Act & Assert
        login_schema = UserLoginSchema(
            email=test_user_data["email"],
            password="WrongPassword123!",
        )
        with pytest.raises(ValueError, match="メールアドレスまたはパスワードが不正です"):
            await auth_service.login_user(login_schema)

    # ーーーーーー JWTトークン生成テスト ーーーーーー

    @pytest.mark.asyncio
    async def test_create_access_token(self, auth_service):
        """アクセストークン生成のテスト"""
        # Arrange
        user_id = str(uuid4())

        # Act
        token = auth_service.create_access_token(user_id)

        # Assert
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.asyncio
    async def test_create_refresh_token(self, auth_service):
        """リフレッシュトークン生成のテスト"""
        # Arrange
        user_id = str(uuid4())
        device_id = "device-001"

        # Act
        token = auth_service.create_refresh_token(user_id, device_id)

        # Assert
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.asyncio
    async def test_verify_token_valid(self, auth_service):
        """有効なトークン検証のテスト"""
        # Arrange
        user_id = str(uuid4())
        token = auth_service.create_access_token(user_id)

        # Act
        payload = auth_service.verify_token(token)

        # Assert
        assert payload is not None
        assert payload["sub"] == user_id

    @pytest.mark.asyncio
    async def test_verify_token_invalid(self, auth_service):
        """無効なトークン検証のテスト"""
        # Arrange
        invalid_token = "invalid.token.here"

        # Act & Assert
        with pytest.raises(ValueError):
            auth_service.verify_token(invalid_token)

    @pytest.mark.asyncio
    async def test_verify_token_expired(self, auth_service, monkeypatch):
        """期限切れトークン検証のテスト"""
        # Arrange
        user_id = str(uuid4())
        # 期限切れのトークンを生成（モック）
        from src.app.auth import security

        expired_token = security.create_jwt_token(
            data={"sub": user_id, "token_type": "access"},
            expires_delta=timedelta(hours=-1),  # 1時間前に期限切れ
        )

        # Act & Assert
        with pytest.raises(ValueError):
            auth_service.verify_token(expired_token)

    # ーーーーーー パスワード関連テスト ーーーーーー

    @pytest.mark.asyncio
    async def test_change_password_success(self, auth_service, test_user_data):
        """パスワード変更成功のテスト"""
        # Arrange
        register_schema = UserRegisterSchema(**test_user_data)
        user = await auth_service.register_user(register_schema)
        new_password = "NewPassword456!"

        # Act
        updated_user = await auth_service.change_password(user.id, test_user_data["password"], new_password)

        # Assert
        assert verify_password(new_password, updated_user.password_hash)

    @pytest.mark.asyncio
    async def test_change_password_invalid_current(self, auth_service, test_user_data):
        """現在のパスワードが不正な場合のテスト"""
        # Arrange
        register_schema = UserRegisterSchema(**test_user_data)
        user = await auth_service.register_user(register_schema)

        # Act & Assert
        with pytest.raises(ValueError, match="現在のパスワードが不正です"):
            await auth_service.change_password(user.id, "WrongPassword123!", "NewPassword456!")

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, auth_service, test_user_data):
        """ユーザー名でユーザーを取得するテスト"""
        # Arrange
        register_schema = UserRegisterSchema(**test_user_data)
        registered_user = await auth_service.register_user(register_schema)

        # Act
        user = await auth_service.get_user_by_username(test_user_data["username"])

        # Assert
        assert user is not None
        assert user.id == registered_user.id
        assert user.username == test_user_data["username"]

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, auth_service):
        """存在しないユーザー名での取得テスト"""
        # Arrange
        username = "nonexistent"

        # Act
        user = await auth_service.get_user_by_username(username)

        # Assert
        assert user is None

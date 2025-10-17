"""
auth/router.py - 認証APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.auth.schemas import (
    AuthTokens,
    PasswordChange,
    PasswordResetConfirm,
    PasswordResetRequest,
    TokenRefresh,
    UserLoginSchema,
    UserRegisterSchema,
    UserResponse,
)
from app.auth.service import AuthService
from app.config import settings
from app.database.db import get_session
from app.database.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegisterSchema,
    db: AsyncSession = Depends(get_session),
) -> UserResponse:
    """新規ユーザー登録"""
    service = AuthService(db)

    try:
        user = await service.register_user(user_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/login", response_model=AuthTokens)
async def login(
    credentials: UserLoginSchema,
    db: AsyncSession = Depends(get_session),
) -> AuthTokens:
    """ユーザーログイン"""
    service = AuthService(db)

    try:
        user = await service.login_user(credentials)

        # JWTトークンを生成
        access_token = service.create_access_token(user.id)
        # TODO: 実際のデバイス情報を取得
        refresh_token = service.create_refresh_token(user.id, device_id="web-client")

        from app.config import settings

        return AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_hours * 3600,  # 秒単位
            user=UserResponse.model_validate(user),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session),
) -> None:
    """パスワード変更（認証必須）"""
    service = AuthService(db)

    try:
        await service.change_password(
            current_user.id,
            password_data.current_password,
            password_data.new_password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """現在のユーザー情報を取得（認証必須）"""
    return UserResponse.model_validate(current_user)


@router.post("/refresh", response_model=AuthTokens)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_session),
) -> AuthTokens:
    """トークンリフレッシュ"""
    service = AuthService(db)

    try:
        new_access_token, new_refresh_token = await service.refresh_access_token(token_data.refresh_token)

        # ユーザー情報を取得（トークンからuser_idを抽出）
        from app.auth.security import verify_access_token

        payload = verify_access_token(new_access_token)
        user_id = payload.get("sub")

        user = await service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ユーザーが見つかりません",
            )

        return AuthTokens(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_hours * 3600,
            user=UserResponse.model_validate(user),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """ログアウト（認証必須）

    現在のユーザーのすべてのリフレッシュトークンを無効化します。
    """
    service = AuthService(db)
    await service.logout(current_user.id)
    return {"message": "Logged out successfully"}


@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """パスワードリセットリクエスト

    Note: 本番環境ではメールが送信されますが、開発環境ではトークンを返します。
    """
    service = AuthService(db)
    reset_token = await service.request_password_reset(reset_request.email)

    # 開発環境用: トークンを返す（本番環境では削除）
    return {"message": "Password reset email sent", "token": reset_token}


@router.post("/confirm-password-reset", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """パスワードリセット確認"""
    service = AuthService(db)

    try:
        await service.confirm_password_reset(reset_data.token, reset_data.new_password)
        return {"message": "Password reset successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

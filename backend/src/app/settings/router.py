"""
settings/router.py - ユーザー設定APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.auth.schemas import UserResponse
from app.database.db import get_session
from app.database.models.user import User
from app.settings.schemas import DeviceInfo, DeviceListResponse, ProfileUpdate, UserSettingsResponse, UserSettingsUpdate
from app.settings.service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=UserSettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session),
) -> UserSettingsResponse:
    """ユーザー設定を取得（認証必須）"""
    service = SettingsService(db)
    settings = await service.get_or_create_user_settings(current_user.id)
    return UserSettingsResponse.model_validate(settings)


@router.put("", response_model=UserSettingsResponse)
async def update_settings(
    settings_data: UserSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session),
) -> UserSettingsResponse:
    """ユーザー設定を更新（認証必須）"""
    service = SettingsService(db)
    settings = await service.update_user_settings(current_user.id, settings_data)
    return UserSettingsResponse.model_validate(settings)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session),
) -> UserResponse:
    """プロフィールを更新（認証必須）"""
    service = SettingsService(db)

    try:
        user = await service.update_profile(current_user.id, profile_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/devices", response_model=DeviceListResponse)
async def get_devices(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session),
) -> DeviceListResponse:
    """デバイス一覧を取得（認証必須）"""
    service = SettingsService(db)
    devices = await service.get_user_devices(current_user.id)

    # RefreshToken から DeviceInfo に変換
    device_list = [
        DeviceInfo(
            id=device.id,
            device_id=device.device_id,
            device_name=device.device_name,
            device_type=device.device_type,
            last_used_at=device.last_used_at,
            created_at=device.created_at,
            is_current=False,  # TODO: 現在のデバイスかどうかを判定
        )
        for device in devices
    ]

    return DeviceListResponse(devices=device_list)


@router.delete("/devices/{device_id}", status_code=status.HTTP_200_OK)
async def delete_device(
    device_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """デバイスを削除（リフレッシュトークンを無効化）（認証必須）"""
    service = SettingsService(db)

    try:
        await service.revoke_device(current_user.id, device_id)
        return {"message": "Device removed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

"""
unit/test_auth_token_flows.py - パスワードのハッシュとトークンの流れのテスト
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import PasswordChange, PasswordReset, PasswordResetConfirm, UserLoginSchema, UserRegisterSchema
from app.auth.security import hash_password, hash_token, verify_password
from app.auth.service import AuthService
from app.database.db import get_session
from app.database.models.token import RefreshToken
from app.main import app

PASSWORD = "SecurePassword123!"
# 25 文字で 75 バイト。文字数の上限（255）には収まるが bcrypt の 72 バイトを超える
LONG_PASSWORD = "パ" * 24 + "A1!"


def test_password_hash_round_trip():
    hashed = hash_password(PASSWORD)

    assert hashed.startswith("$2b$")
    assert verify_password(PASSWORD, hashed)
    assert not verify_password("WrongPassword123!", hashed)


def test_verify_password_returns_false_for_password_longer_than_72_bytes():
    hashed = hash_password(PASSWORD)

    assert verify_password(LONG_PASSWORD, hashed) is False


def test_hash_token_is_deterministic_and_distinct():
    assert hash_token("token-a") == hash_token("token-a")
    assert hash_token("token-a") != hash_token("token-b")


@pytest.mark.parametrize(
    "build",
    [
        lambda pw: UserRegisterSchema(username="someone", email="someone@example.com", password=pw),
        lambda pw: PasswordReset(token="t", new_password=pw),
        lambda pw: PasswordChange(current_password=PASSWORD, new_password=pw),
        lambda pw: PasswordResetConfirm(token="t", new_password=pw),
    ],
)
def test_password_fields_reject_more_than_72_bytes(build):
    with pytest.raises(ValidationError):
        build(LONG_PASSWORD)


async def _register(service: AuthService) -> None:
    await service.register_user(UserRegisterSchema(username="flowuser", email="flow@example.com", password=PASSWORD))


@pytest.mark.asyncio
async def test_refresh_tokens_issued_back_to_back_differ(db_session: AsyncSession):
    service = AuthService(db_session)

    assert service.create_refresh_token("user-1", "device-1") != service.create_refresh_token("user-1", "device-1")


@pytest.mark.asyncio
async def test_refresh_rotates_a_stored_token(db_session: AsyncSession):
    service = AuthService(db_session)
    await _register(service)
    user = await service.login_user(UserLoginSchema(email="flow@example.com", password=PASSWORD))
    first = service.create_refresh_token(str(user.id), "web-client")
    await service.store_refresh_token(user.id, first, "web-client")

    _, second = await service.refresh_access_token(first)

    assert second != first
    rows = (await db_session.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))).scalars().all()
    assert len(rows) == 2
    with pytest.raises(ValueError):
        await service.refresh_access_token(first)


@pytest.mark.asyncio
async def test_confirm_password_reset_with_issued_token_changes_password(db_session: AsyncSession):
    service = AuthService(db_session)
    await _register(service)
    token = await service.request_password_reset("flow@example.com")
    new_password = "AnotherPassword456?"

    await service.confirm_password_reset(token, new_password)

    user = await service.login_user(UserLoginSchema(email="flow@example.com", password=new_password))
    assert user.email == "flow@example.com"


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    async def override() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_then_refresh_over_http(client: AsyncClient):
    await client.post(
        "/auth/register", json={"username": "httpuser", "email": "http@example.com", "password": PASSWORD}
    )
    login = await client.post("/auth/login", json={"email": "http@example.com", "password": PASSWORD})

    refreshed = await client.post("/auth/refresh", json={"refresh_token": login.json()["refresh_token"]})

    assert refreshed.status_code == 200
    assert refreshed.json()["refresh_token"] != login.json()["refresh_token"]


@pytest.mark.asyncio
@pytest.mark.parametrize("email", ["http@example.com", "nobody@example.com"])
async def test_request_password_reset_does_not_return_the_token(client: AsyncClient, email: str):
    await client.post(
        "/auth/register", json={"username": "httpuser", "email": "http@example.com", "password": PASSWORD}
    )

    response = await client.post("/auth/request-password-reset", json={"email": email})

    assert response.status_code == 200
    assert "token" not in response.json()

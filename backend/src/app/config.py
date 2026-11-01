"""
config.py - アプリケーション設定
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# README と .env.example に載っている例の値。公開されているので、これで署名すると誰でもトークンを作れる
_EXAMPLE_JWT_SECRETS = frozenset(
    {
        "your-secret-key-change-in-production",
        "your-secret-key-change-this-in-production-with-openssl-rand-hex-32",
    }
)
MIN_JWT_SECRET_LENGTH = 32


class Settings(BaseSettings):
    """アプリケーション設定"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # 検証エラーに鍵の値を出さない
        hide_input_in_errors=True,
    )

    # データベース
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/ultra_fast_db"

    # JWT設定
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_hours: int = 24
    refresh_token_expire_days: int = 30

    # アプリケーション設定
    debug: bool = False
    app_name: str = "UltraFastAPI"
    api_version: str = "v1"

    # CORS設定
    cors_origins: list = ["*"]

    # ログ設定
    log_level: str = "INFO"

    @field_validator("jwt_secret_key")
    @classmethod
    def _reject_weak_jwt_secret(cls, value: str) -> str:
        value = value.strip()
        if value in _EXAMPLE_JWT_SECRETS:
            raise ValueError("JWT_SECRET_KEY が例の値のままです。openssl rand -hex 32 で作った値を設定してください")
        if len(value) < MIN_JWT_SECRET_LENGTH:
            raise ValueError(f"JWT_SECRET_KEY は {MIN_JWT_SECRET_LENGTH} 文字以上にしてください")
        return value


settings = Settings()

"""
config.py - アプリケーション設定
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # データベース
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/ultra_fast_db"

    # JWT設定
    jwt_secret_key: str = "your-secret-key-change-in-production"
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


settings = Settings()

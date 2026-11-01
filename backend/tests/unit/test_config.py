"""
unit/test_config.py - JWT の鍵の設定の検証のテスト
"""

import secrets

import pytest
from pydantic import ValidationError

from app.config import Settings

README_EXAMPLE = "your-secret-key-change-in-production"
ENV_EXAMPLE = "your-secret-key-change-this-in-production-with-openssl-rand-hex-32"


def _settings(**kwargs) -> Settings:
    return Settings(_env_file=None, **kwargs)


@pytest.mark.parametrize("example", [README_EXAMPLE, ENV_EXAMPLE, f"  {ENV_EXAMPLE}  "])
def test_rejects_published_example_secret(example: str):
    with pytest.raises(ValidationError):
        _settings(jwt_secret_key=example)


def test_rejects_secret_shorter_than_32_characters():
    with pytest.raises(ValidationError):
        _settings(jwt_secret_key=secrets.token_hex(15))


def test_requires_secret(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    with pytest.raises(ValidationError):
        _settings()


def test_error_does_not_contain_the_secret():
    weak = secrets.token_hex(10)

    with pytest.raises(ValidationError) as excinfo:
        _settings(jwt_secret_key=weak)

    assert weak not in str(excinfo.value)


def test_accepts_random_secret():
    key = secrets.token_hex(32)

    assert _settings(jwt_secret_key=key).jwt_secret_key == key

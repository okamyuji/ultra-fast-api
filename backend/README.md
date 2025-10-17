# Ultra Fast API Backend

FastAPI + PostgreSQL + SQLAlchemyによる超高速APIバックエンド

## 概要

1000万件のデータに対して1秒以内に応答する超高速APIシステムのバックエンド実装です。

## 技術スタック

- Python 3.12
- FastAPI 0.115.0
- PostgreSQL 17
- SQLAlchemy 2.0.36
- uv (パッケージマネージャー)
- Ruff (Linter/Formatter)

## セットアップ

```bash
# 依存関係のインストール
uv sync

# Docker環境の起動
docker compose up -d

# マイグレーションの実行
uv run alembic upgrade head

# テストの実行
uv run pytest
```

## 開発

```bash
# コード品質チェック
uv run ruff check .
uv run ruff format .
uv run mypy src/

# テストの実行
uv run pytest --cov=src
```

詳細はプロジェクトルートのREADME.mdを参照してください。

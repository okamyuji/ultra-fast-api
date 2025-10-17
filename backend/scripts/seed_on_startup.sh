#!/bin/sh
# Docker起動時に実行されるデータシーディングスクリプト

echo "🔍 データベース接続を確認中..."

# データベースが準備完了するまで待機
until pg_isready -h db -U postgres; do
  echo "⏳ データベースの起動を待機中..."
  sleep 2
done

echo "✅ データベース接続確認完了"
echo ""

# Alembicマイグレーション実行
echo "🔄 データベースマイグレーション実行中..."
uv run alembic upgrade head

if [ $? -eq 0 ]; then
  echo "✅ マイグレーション完了"
else
  echo "❌ マイグレーション失敗"
  exit 1
fi

echo ""

# 環境変数でシーディングを制御（デフォルトはfalse）
SEED_DATA=${SEED_DATA:-false}

if [ "$SEED_DATA" = "true" ]; then
  echo "🌱 商品データシーディング開始..."
  echo "⚠️  注意: 1000万件のデータ生成には時間がかかります（約10-30分）"
  echo ""

  uv run python scripts/seed_products.py

  if [ $? -eq 0 ]; then
    echo "✅ データシーディング完了"
  else
    echo "❌ データシーディング失敗"
    exit 1
  fi
else
  echo "ℹ️  データシーディングはスキップされました"
  echo "   シーディングを実行する場合は SEED_DATA=true を設定してください"
  echo "   または手動で実行: docker compose exec api uv run python scripts/seed_products.py"
fi

echo ""
echo "🚀 アプリケーション起動準備完了"

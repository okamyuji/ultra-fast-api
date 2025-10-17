# UltraFastAPI

1000万件データに対して1秒以内に応答する超高速APIシステム

FastAPI + PostgreSQL + Flutter(Riverpod 3.x) によるTDD開発

---

## 目次

- [概要](#概要)
- [技術スタック](#技術スタック)
- [パフォーマンス実績](#パフォーマンス実績)
- [クイックスタート](#クイックスタート)
- [バックエンド](#バックエンド)
- [フロントエンド](#フロントエンド)
- [プロジェクト構造](#プロジェクト構造)
- [API仕様](#api仕様)
- [開発](#開発)
- [テスト](#テスト)
- [トラブルシューティング](#トラブルシューティング)

---

## 概要

10万〜1000万件のデータに対して1秒以内に応答する超高速APIシステム。TDD（Test-Driven Development）手法で開発しています

### 主要機能

#### バックエンド

- ✅ **認証システム**
  - ユーザー登録・ログイン（メールアドレスベース）
  - JWT + リフレッシュトークン
  - パスワード変更・リセット
  - トークンリフレッシュ・ログアウト

- ✅ **商品管理**
  - CRUD操作（作成・読取・更新・削除）
  - カーソルベースページネーション（1000万件対応）
  - 高度なフィルタリング（カテゴリ、ステータス、日付範囲）
  - 全文検索（ILIKE）

- ✅ **ユーザー設定**
  - テーマ設定（ライト/ダーク）
  - デフォルトページサイズ設定
  - プロフィール編集
  - デバイス管理・取り消し

- ✅ **データ生成**
  - 1000万件日本語データ自動生成
  - カテゴリー別データ生成（電化製品、衣類、食品）
  - バッチインサート最適化
  - 進捗表示・リアルタイム統計

- ✅ **パフォーマンステスト**
  - 自動化テストスイート
  - 統計分析（平均・中央値・標準偏差）
  - CI/CD統合対応

#### フロントエンド

- ✅ **認証機能（JWT）**
  - ログイン / 会員登録
  - トークン自動更新（401/403エラー時）
  - セキュアストレージでのトークン管理
  - パスワードバリデーション
  - エラーハンドリング（401, 409, 422, 500等）

- ✅ **商品機能**
  - 1000万件対応のカーソルベースページネーション
  - 無限スクロール
  - カテゴリ・ステータスフィルタリング
  - 全文検索
  - 商品詳細表示

- ✅ **設定機能**
  - アプリケーション設定の取得・更新
  - 動的テーマ切り替え（ライト/ダーク）
  - ボトムタブナビゲーション

- ✅ **UI/UX**
  - Material 3デザイン
  - ライト/ダークテーマ
  - ローディング・エラー表示
  - 日本語ローカライズ

---

## 技術スタック

### バックエンド

| 技術 | バージョン | 用途 |
|------|----------|------|
| Python | 3.12 | プログラミング言語 |
| FastAPI | 0.115.0 | Webフレームワーク |
| PostgreSQL | 17 | データベース |
| SQLAlchemy | 2.0.36 | 非同期ORM |
| asyncpg | 0.30.0 | PostgreSQLドライバ |
| uv | 最新 | パッケージマネージャー（Rust製） |
| Ruff | 0.6.9 | Linter/Formatter |
| Alembic | 1.14.0 | DBマイグレーション |
| pytest | 8.2.2 | テストフレームワーク |
| Docker Compose | - | コンテナオーケストレーション |

### フロントエンド

| 技術 | バージョン | 用途 |
|------|----------|------|
| Flutter | 3.35.6 | UIフレームワーク |
| Dart | 3.9.2 | プログラミング言語 |
| Riverpod | 3.0.2 | 状態管理（Notifierパターン） |
| Dio | 5.7.0 | HTTP通信 |
| go_router | 16.2.5 | ルーティング |
| flutter_secure_storage | 9.2.2 | セキュアストレージ |
| json_serializable | 6.9.2 | JSONシリアライゼーション |
| Maestro | 2.0.6 | E2Eテスト |

---

## パフォーマンス実績

### API応答時間（1000万件データ）

**測定日**: 2025-10-16
**データ件数**: 10,000,000件
**測定環境**: Docker (PostgreSQL 17 + FastAPI)

| エンドポイント | 平均応答時間 | 最大応答時間 | 目標 | 達成率 |
|--------------|------------|------------|------|-------|
| 商品一覧（初期ページ） | **4.73ms** | - | <1000ms | **211x** ⚡⚡⚡ |
| カーソルページネーション | **2.99ms** | 4.53ms | <1000ms | **334x** ⚡⚡⚡ |
| フィルタリング（カテゴリ） | **3.12ms** | - | <1000ms | **320x** ⚡⚡⚡ |
| フィルタリング（ステータス） | **2.58ms** | - | <1000ms | **387x** ⚡⚡⚡ |
| フィルタリング（複合条件） | **3.40ms** | - | <1000ms | **294x** ⚡⚡⚡ |
| フィルタリング（日付範囲） | **2.43ms** | - | <1000ms | **411x** ⚡⚡⚡ |
| 検索（商品名） | **21.54ms** | - | <1000ms | **46x** ⚡⚡ |
| 検索（部分一致） | **17.37ms** | - | <1000ms | **57x** ⚡⚡ |
| 検索（複雑な条件） | **2.98ms** | - | <1000ms | **335x** ⚡⚡⚡ |
| 商品詳細取得 | **1.06ms** | 1.67ms | <500ms | **471x** ⚡⚡⚡ |

**総合評価**: ✅ **全テスト合格** - 全エンドポイントが目標応答時間を大幅に上回る性能を達成

### データ生成速度

**実測データ** (2025-10-16測定):

| 件数 | 実測時間 | 生成速度 | バッチサイズ | コミット間隔 |
|------|---------|---------|------------|------------|
| 1,000万件 | **20分16秒** | **8,219件/秒** | 10,000件 | 100,000件 |

---

## クイックスタート

### 前提条件

- Python 3.12+
- Flutter SDK 3.35.0+
- Dart 3.9.2+
- Docker & Docker Compose
- uv (Rust製Pythonパッケージマネージャー)

### セットアップ

#### 1. uvのインストール

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
```

#### 2. リポジトリのクローン

```bash
git clone https://github.com/okamyuji/ultra-fast-api/
cd ultra-fast-api
```

#### 3. バックエンドの起動

```bash
cd backend

# 環境変数設定（任意）
cat > .env << 'EOF'
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=ultra_fast_db
JWT_SECRET_KEY=your-secret-key-change-in-production
SEED_DATA=false
EOF

# Docker起動
docker compose up -d

# ログ確認
docker compose logs -f api

# APIドキュメント
open http://localhost:8000/docs
```

#### 4. フロントエンドの起動

```bash
cd ../frontend/ultra_fast_api

# 依存関係のインストール
flutter pub get

# コード生成
dart run build_runner build --delete-conflicting-outputs

# アプリ起動（サーバーURLを192.168.0.15:8000に設定）
flutter run
```

#### 5. データ生成（初回のみ、任意）

```bash
cd backend

# 1000万件データ生成（約20分）
SEED_DATA=true docker compose up -d
```

---

## バックエンド

### ディレクトリ構造

```text
backend/
├── src/
│   └── app/
│       ├── auth/              # 認証モジュール
│       │   ├── router.py      # エンドポイント
│       │   ├── service.py     # ビジネスロジック
│       │   ├── schemas.py     # Pydanticスキーマ
│       │   ├── security.py    # JWT/暗号化
│       │   └── dependencies.py # 依存性注入
│       ├── products/          # 商品モジュール
│       ├── settings/          # 設定モジュール
│       ├── database/          # データベース
│       │   ├── base.py        # Base定義
│       │   ├── db.py          # セッション管理
│       │   └── models/        # SQLAlchemyモデル
│       ├── config.py          # 設定管理
│       └── main.py            # FastAPIアプリ
├── tests/
│   ├── unit/                  # 単体テスト
│   ├── performance/           # パフォーマンステスト
│   └── conftest.py            # pytestフィクスチャ
├── alembic/                   # DBマイグレーション
├── scripts/                   # ユーティリティ
│   ├── seed_products.py       # データ生成
│   └── run_performance_tests.py # パフォーマンステスト実行
├── compose.yml                # Docker Compose設定
├── Dockerfile                 # Dockerイメージ
├── pyproject.toml             # プロジェクト設定
└── README.md                  # ドキュメント
```

### データベース設計

#### テーブル一覧

- **users**: ユーザー情報
- **products**: 商品情報（1000万件対応）
- **user_settings**: ユーザー設定
- **refresh_tokens**: リフレッシュトークン
- **password_reset_tokens**: パスワードリセットトークン

#### インデックス戦略

```sql
-- 商品テーブル
CREATE INDEX idx_products_created_at_desc ON products (created_at DESC, id);
CREATE INDEX idx_products_category_status ON products (category, status);
CREATE INDEX idx_products_user_id ON products (user_id);
```

### データシーディング

#### 使用方法

```bash
# Docker起動時に自動生成
SEED_DATA=true docker compose up -d

# 手動実行
docker compose exec api uv run python scripts/seed_products.py
```

#### データ仕様

- **総件数**: 10,000,000件（1000万件）
- **言語**: 日本語（商品名・説明文）
- **カテゴリ**: 3種類
  - electronics（電化製品）
  - clothing（衣類）
  - food（食品）
- **ステータス**: 3種類（active, inactive, archived）
- **価格**: 100円 〜 500,000円
- **在庫**: 0 〜 1,000個

### パフォーマンステスト

```bash
# パフォーマンステスト実行
python scripts/run_performance_tests.py

# またはpytest直接実行
docker compose exec api uv run pytest tests/performance/ -v
```

### 開発コマンド

```bash
# テスト実行
docker compose exec api uv run pytest

# カバレッジ確認
docker compose exec api uv run pytest --cov=src --cov-report=html

# コード品質確認
docker compose exec api uv run ruff check .
docker compose exec api uv run ruff format .
docker compose exec api uv run mypy src/

# マイグレーション
docker compose exec api uv run alembic upgrade head
docker compose exec api uv run alembic revision --autogenerate -m "description"
```

---

## フロントエンド

### ディレクトリ構造

```text
lib/
├── core/                      # コア機能
│   ├── api/                   # API通信
│   │   └── api_client.dart   # Dioクライアント設定
│   ├── config/                # 設定管理
│   │   └── app_config.dart   # JSON設定ファイル読み込み
│   ├── providers/             # グローバルプロバイダー
│   ├── router/                # ルーティング設定
│   └── storage/               # ストレージ管理
│       └── token_manager.dart # JWTトークン管理
├── features/                  # 機能別モジュール
│   ├── auth/                  # 認証機能
│   │   ├── data/             # データレイヤー
│   │   ├── domain/           # ドメインモデル
│   │   └── presentation/     # UI + Notifier
│   ├── products/             # 商品機能
│   ├── settings/             # 設定機能
│   ├── home/                 # ホーム画面（タブナビゲーション）
│   └── splash/               # スプラッシュ画面
├── shared/                    # 共通コンポーネント
│   ├── theme/                # テーマ設定
│   ├── widgets/              # 再利用可能ウィジェット
│   └── utils/                # ユーティリティ
└── main.dart                  # エントリーポイント

config/                        # 環境別設定ファイル
├── app_config.json           # デフォルト設定（192.168.0.15）
├── app_config.dev.json       # 開発環境設定
└── app_config.prod.json      # 本番環境設定
```

### 環境設定

#### config/app_config.json

```json
{
  "apiBaseUrl": "http://192.168.0.15:8000",
  "defaultPageLimit": 20,
  "connectTimeout": 30,
  "receiveTimeout": 30,
  "tokenRefreshThreshold": 10
}
```

### 開発コマンド

```bash
# アプリ起動
flutter run

# 環境指定起動
flutter run --dart-define=ENV=dev
flutter run --dart-define=ENV=prod

# テスト実行
flutter test
flutter test --coverage

# 静的解析
flutter analyze

# コード生成
dart run build_runner build --delete-conflicting-outputs

# コード生成（監視モード）
dart run build_runner watch

# Maestro UIテスト
maestro test .maestro/login_flow.yaml
maestro test .maestro/
```

---

## プロジェクト構造

```text
/Users/systemi/devs/python/ultra-fast-api/
├── backend/                   # バックエンド
│   ├── src/app/              # アプリケーションコード
│   ├── tests/                # テスト
│   ├── alembic/              # マイグレーション
│   ├── scripts/              # ユーティリティスクリプト
│   ├── compose.yml           # Docker Compose設定
│   ├── Dockerfile            # Dockerイメージ
│   └── pyproject.toml        # プロジェクト設定
├── frontend/
│   └── ultra_fast_api/       # Flutterアプリ
│       ├── lib/              # アプリケーションコード
│       ├── test/             # テスト
│       ├── config/           # 環境設定
│       ├── .maestro/         # UIテストフロー
│       └── pubspec.yaml      # Flutter設定
└── README.md                  # このファイル
```

---

## API仕様

### ベースURL

```text
http://localhost:8000
```

### 認証エンドポイント

#### POST /auth/register

会員登録

```json
Request:
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}

Response (201):
{
  "id": "uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### POST /auth/login

ログイン（メールアドレスベース）

```json
Request:
{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}

Response (200):
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_jwt_token",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "uuid",
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

#### POST /auth/refresh

トークン更新

```json
Request:
{
  "refresh_token": "jwt_token"
}

Response (200):
{
  "access_token": "new_jwt_token",
  "refresh_token": "new_refresh_token",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### POST /auth/logout

ログアウト（認証必須）

```json
Response (200):
{
  "message": "Logged out successfully"
}
```

### 商品エンドポイント

#### GET /products

商品一覧（カーソルベースページネーション）

**クエリパラメータ**:

- `limit=20` (デフォルト20, 最大100)
- `cursor=null` (カーソルベースページング)
- `sort_by=created_at` (created_at | name | price)
- `sort_order=desc` (asc | desc)
- `search=laptop` (名前・説明検索)
- `category=electronics` (カテゴリフィルタ)
- `status=active` (ステータスフィルタ)
- `date_from=2025-01-01` (範囲フィルタ)
- `date_to=2025-12-31` (範囲フィルタ)

```json
Response (200):
{
  "items": [
    {
      "id": "uuid",
      "name": "高性能ノートパソコン 1234",
      "description": "高品質なノートパソコンです。",
      "category": "electronics",
      "status": "active",
      "price": 1299.99,
      "stock": 50,
      "user_id": "uuid",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "next_cursor": "uuid",
    "has_more": true,
    "returned_count": 20,
    "total_count_estimate": 10000000
  }
}
```

#### GET /products/{id}

商品詳細

```json
Response (200):
{
  "id": "uuid",
  "name": "高性能ノートパソコン 1234",
  "description": "高品質なノートパソコンです。",
  "category": "electronics",
  "status": "active",
  "price": 1299.99,
  "stock": 50,
  "user_id": "uuid",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### 設定エンドポイント

#### GET /settings

ユーザー設定取得（認証必須）

```json
Response (200):
{
  "id": "uuid",
  "user_id": "uuid",
  "theme": "dark",
  "default_page_size": 20,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

#### PUT /settings

ユーザー設定更新（認証必須）

```json
Request:
{
  "theme": "light",
  "default_page_size": 50
}

Response (200):
{
  "id": "uuid",
  "user_id": "uuid",
  "theme": "light",
  "default_page_size": 50,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T11:45:00Z"
}
```

---

## 開発

### テスト戦略（TDD）

```text
ユニットテスト (60%)
  ├─ Serviceビジネスロジック
  ├─ Validator
  └─ Utility関数

統合テスト (30%)
  ├─ Auth + DB 連携
  ├─ Products + Filter + Pagination
  └─ Settings 更新

パフォーマンステスト (10%)
  ├─ 1000万件データ応答時間
  ├─ ページネーション性能
  └─ フィルタリング性能
```

### コードカバレッジ目標

- バックエンド: ≥80%
- フロントエンド: ≥80%

---

## テスト

### バックエンド

```bash
cd backend

# 全テスト実行
docker compose exec api uv run pytest

# ユニットテストのみ
docker compose exec api uv run pytest tests/unit/

# パフォーマンステスト
python scripts/run_performance_tests.py

# カバレッジ確認
docker compose exec api uv run pytest --cov=src --cov-report=html
```

### フロントエンド

```bash
cd frontend/ultra_fast_api

# 全テスト実行
flutter test

# カバレッジ付き
flutter test --coverage

# Maestro UIテスト
maestro test .maestro/
```

---

## トラブルシューティング

### バックエンド

#### Docker起動失敗

```bash
# コンテナ停止・削除
docker compose down -v

# 再ビルド・起動
docker compose build --no-cache
docker compose up -d
```

#### データシーディングが途中で止まった

```bash
# 再実行すれば不足分のみ追加される
docker compose exec api uv run python scripts/seed_products.py
```

#### データをリセットして再生成

```bash
# 全商品データを削除
docker compose exec db psql -U postgres -d ultra_fast_db -c "TRUNCATE products CASCADE;"

# 再度シーディング実行
docker compose exec api uv run python scripts/seed_products.py
```

### フロントエンド

#### ビルドエラー

```bash
flutter clean
flutter pub get
dart run build_runner build --delete-conflicting-outputs
```

#### 実機でHTTP接続エラー

**iOS**: `ios/Runner/Info.plist`に以下を追加

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

**Android**: `android/app/src/main/AndroidManifest.xml`に追加

```xml
<application android:usesCleartextTraffic="true">
```

#### トークン期限切れで403エラー

アプリをログアウトして再ログインしてください。トークンリフレッシュは自動的に実行されますが、リフレッシュトークン自体が期限切れの場合は再ログインが必要です。

---

## 環境変数

### バックエンド (.env)

```env
# データベース設定
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=ultra_fast_db

# JWT設定
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
REFRESH_TOKEN_EXPIRE_DAYS=30

# データシーディング設定
SEED_DATA=false
```

---

## 注意事項

⚠️ **初回起動時のみ推奨**: 1000万件の生成には約20分かかるため、初回起動時のみ `SEED_DATA=true` を使用し、2回目以降は `false` に戻すことを推奨します。

⚠️ **ディスク容量**: 1000万件のデータは約5-10GBのディスク容量を使用します。

⚠️ **本番環境注意**: 本番環境では `SEED_DATA=false` に設定し、誤ってデータ生成しないように注意してください。

⚠️ **JWT_SECRET_KEY**: 本番環境では必ず強力なシークレットキーに変更してください（`openssl rand -hex 32`で生成可能）。

⚠️ **HTTP接続**: 開発環境では `http://192.168.0.15:8000` を使用していますが、本番環境では必ずHTTPSを使用してください。

---

## ライセンス

MIT

---

## 参考リンク

### バックエンド

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [PostgreSQL Performance Optimization](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [uv Documentation](https://docs.astral.sh/uv)
- [Ruff Documentation](https://docs.astral.sh/ruff)

### フロントエンド

- [Flutter公式](https://flutter.dev/)
- [Riverpod 3.x](https://riverpod.dev/)
- [Dio](https://pub.dev/packages/dio)
- [go_router](https://pub.dev/packages/go_router)
- [Maestro](https://maestro.mobile.dev/)

---

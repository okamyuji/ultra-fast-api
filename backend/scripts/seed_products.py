"""
商品データシーディングスクリプト

1000万件の日本語を含む商品データをランダムに生成してデータベースに挿入します。
"""

import asyncio
import os
import random
import sys
from datetime import UTC, datetime, timedelta
from uuid import uuid4

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/src")

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# データベース接続URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/ultra_fast_db")

# データ生成設定
TARGET_RECORDS = 10_000_000  # 1000万件
BATCH_SIZE = 10_000  # バッチサイズ
COMMIT_INTERVAL = 100_000  # コミット間隔

# 日本語商品名プレフィックス
PRODUCT_PREFIXES = [
    "高性能",
    "プレミアム",
    "スタンダード",
    "エコノミー",
    "デラックス",
    "プロフェッショナル",
    "ビジネス",
    "ホーム",
    "ポータブル",
    "コンパクト",
    "ワイド",
    "スリム",
    "ミニ",
    "メガ",
    "ウルトラ",
    "スーパー",
    "ハイパー",
    "スマート",
    "デジタル",
    "アナログ",
    "ワイヤレス",
    "有線",
    "ハイブリッド",
]

# 日本語商品タイプ（カテゴリー別）
PRODUCT_TYPES_BY_CATEGORY = {
    "electronics": [
        "ノートパソコン",
        "デスクトップPC",
        "タブレット",
        "スマートフォン",
        "キーボード",
        "マウス",
        "モニター",
        "プリンター",
        "ヘッドホン",
        "イヤホン",
        "スピーカー",
        "ウェブカメラ",
        "外付けHDD",
        "SSD",
        "充電器",
        "ケーブル",
        "ルーター",
        "電卓",
        "時計",
        "照明",
        "扇風機",
        "暖房器具",
        "加湿器",
        "除湿機",
        "掃除機",
        "空気清浄機",
        "冷蔵庫",
        "電子レンジ",
        "炊飯器",
        "トースター",
        "コーヒーメーカー",
        "電気ケトル",
        "ミキサー",
    ],
    "clothing": [
        "Tシャツ",
        "シャツ",
        "ポロシャツ",
        "セーター",
        "カーディガン",
        "パーカー",
        "ジャケット",
        "コート",
        "ジーンズ",
        "チノパン",
        "スラックス",
        "スカート",
        "ワンピース",
        "スーツ",
        "ネクタイ",
        "靴下",
        "下着",
        "パジャマ",
        "スニーカー",
        "革靴",
        "ブーツ",
        "サンダル",
        "帽子",
        "マフラー",
        "手袋",
        "ベルト",
        "バッグ",
        "財布",
        "時計",
        "アクセサリー",
    ],
    "food": [
        "米",
        "パン",
        "麺",
        "パスタ",
        "うどん",
        "そば",
        "ラーメン",
        "カレー",
        "レトルト食品",
        "缶詰",
        "冷凍食品",
        "お菓子",
        "チョコレート",
        "クッキー",
        "ポテトチップス",
        "ジュース",
        "コーヒー",
        "紅茶",
        "緑茶",
        "ウーロン茶",
        "水",
        "調味料",
        "醤油",
        "味噌",
        "砂糖",
        "塩",
        "酢",
        "油",
        "ドレッシング",
        "ソース",
    ],
}

# カテゴリ（フィルター機能で使用される3つのカテゴリ）
CATEGORIES = [
    "electronics",  # 電化製品
    "clothing",  # 衣類
    "food",  # 食品
]

# ステータス
STATUSES = ["active", "inactive", "archived"]

# 説明文テンプレート
DESCRIPTION_TEMPLATES = [
    "高品質な{product_type}です。日常使いに最適で、長期間ご使用いただけます。",
    "{prefix}{product_type}は、最新の技術を搭載した革新的な製品です。",
    "使いやすさと機能性を兼ね備えた{product_type}。ビジネスシーンでも活躍します。",
    "コンパクトで持ち運びに便利な{product_type}。外出先でも快適に使用できます。",
    "エネルギー効率の良い{product_type}で、環境にも優しい設計です。",
    "プロフェッショナル向けの高性能{product_type}。要求の厳しい作業もスムーズに。",
    "家族みんなで使える{product_type}。シンプルな操作で誰でも簡単に使えます。",
    "スタイリッシュなデザインの{product_type}。インテリアにも馴染みます。",
]


def generate_product_name(category: str) -> str:
    """カテゴリーに応じたランダムな商品名を生成"""
    prefix = random.choice(PRODUCT_PREFIXES)
    product_type = random.choice(PRODUCT_TYPES_BY_CATEGORY[category])
    model_number = random.randint(100, 9999)
    return f"{prefix}{product_type} {model_number}"


def generate_description(name: str) -> str:
    """商品説明を生成"""
    prefix = name.split()[0]
    product_type = " ".join(name.split()[:-1])
    template = random.choice(DESCRIPTION_TEMPLATES)
    return template.format(prefix=prefix, product_type=product_type)


def generate_random_date(start_days_ago: int = 365, end_days_ago: int = 0) -> datetime:
    """ランダムな日時を生成"""
    start_date = datetime.now(UTC) - timedelta(days=start_days_ago)
    end_date = datetime.now(UTC) - timedelta(days=end_days_ago)
    random_timestamp = start_date.timestamp() + random.random() * (end_date.timestamp() - start_date.timestamp())
    return datetime.fromtimestamp(random_timestamp, UTC)


async def get_user_ids(session: AsyncSession) -> list[str]:
    """既存のユーザーIDを取得"""
    result = await session.execute(text("SELECT id FROM users"))
    user_ids = [str(row[0]) for row in result.fetchall()]

    if not user_ids:
        print("⚠️  警告: ユーザーが存在しません。デフォルトユーザーを作成します...")
        # デフォルトユーザーを作成
        default_user_id = str(uuid4())
        await session.execute(
            text("""
                INSERT INTO users (id, username, email, password_hash, is_active, created_at, updated_at)
                VALUES (:id, :username, :email, :password_hash, :is_active, :created_at, :updated_at)
            """),
            {
                "id": default_user_id,
                "username": "seed_user",
                "email": "seed@example.com",
                "password_hash": "$2b$12$dummy_hash_for_seeding_only",
                "is_active": True,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            },
        )
        await session.commit()
        user_ids = [default_user_id]
        print(f"✅ デフォルトユーザーを作成しました: {default_user_id}")

    return user_ids


async def get_existing_count(session: AsyncSession) -> int:
    """既存の商品数を取得"""
    result = await session.execute(text("SELECT COUNT(*) FROM products"))
    return result.scalar() or 0


async def delete_all_products(session: AsyncSession) -> int:
    """既存の全商品を削除"""
    print("🗑️  既存の商品データを削除中...")
    result = await session.execute(text("DELETE FROM products"))
    deleted_count = result.rowcount
    await session.commit()
    print(f"✅ {deleted_count:,}件の商品を削除しました")
    return deleted_count


async def seed_products():
    """商品データをシーディング"""
    print("=" * 80)
    print("🌱 商品データシーディング開始")
    print("=" * 80)
    print(f"📊 目標件数: {TARGET_RECORDS:,}件")
    print(f"📦 バッチサイズ: {BATCH_SIZE:,}件")
    print(f"💾 コミット間隔: {COMMIT_INTERVAL:,}件")
    print()

    # データベース接続
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # ユーザーID取得
        print("👤 ユーザーIDを取得中...")
        user_ids = await get_user_ids(session)
        print(f"✅ {len(user_ids)}人のユーザーを取得しました")
        print()

        # 既存データ確認
        existing_count = await get_existing_count(session)
        print(f"📈 既存商品数: {existing_count:,}件")

        # 既存データを削除して再作成
        if existing_count > 0:
            print("⚠️  既存データが見つかりました。全て削除して再作成します。")
            await delete_all_products(session)
            existing_count = 0

        remaining = TARGET_RECORDS - existing_count
        print(f"🎯 生成件数: {remaining:,}件")
        print()

        # データ生成とインサート
        total_inserted = 0
        batch_data = []

        start_time = datetime.now(UTC)

        for _i in range(remaining):
            # 商品データ生成
            category = random.choice(CATEGORIES)
            product_name = generate_product_name(category)
            created_at = generate_random_date(365, 1)
            updated_at = created_at + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            product = {
                "id": str(uuid4()),
                "name": product_name,
                "description": generate_description(product_name),
                "category": category,
                "status": random.choice(STATUSES),
                "price": round(random.uniform(100, 500000), 2),
                "stock": random.randint(0, 1000),
                "user_id": random.choice(user_ids),
                "created_at": created_at,
                "updated_at": updated_at,
            }

            batch_data.append(product)

            # バッチインサート
            if len(batch_data) >= BATCH_SIZE:
                await session.execute(
                    text("""
                        INSERT INTO products
                        (id, name, description, category, status, price, stock, user_id, created_at, updated_at)
                        VALUES
                        (:id, :name, :description, :category, :status, :price, :stock, :user_id, :created_at, :updated_at)
                    """),
                    batch_data,
                )
                total_inserted += len(batch_data)
                batch_data = []

                # コミット
                if total_inserted % COMMIT_INTERVAL == 0:
                    await session.commit()

                    # 進捗表示
                    elapsed = (datetime.now(UTC) - start_time).total_seconds()
                    speed = total_inserted / elapsed if elapsed > 0 else 0
                    progress = (total_inserted / remaining) * 100
                    eta_seconds = (remaining - total_inserted) / speed if speed > 0 else 0

                    print(
                        f"⏳ 進捗: {total_inserted:,}/{remaining:,}件 ({progress:.1f}%) | "
                        f"速度: {speed:,.0f}件/秒 | "
                        f"残り時間: {int(eta_seconds // 60)}分{int(eta_seconds % 60)}秒"
                    )

        # 残りのデータをインサート
        if batch_data:
            await session.execute(
                text("""
                    INSERT INTO products
                    (id, name, description, category, status, price, stock, user_id, created_at, updated_at)
                    VALUES
                    (:id, :name, :description, :category, :status, :price, :stock, :user_id, :created_at, :updated_at)
                """),
                batch_data,
            )
            total_inserted += len(batch_data)
            await session.commit()

        # 完了
        elapsed = (datetime.now(UTC) - start_time).total_seconds()
        print()
        print("=" * 80)
        print("✅ データシーディング完了！")
        print("=" * 80)
        print(f"📊 挿入件数: {total_inserted:,}件")
        print(f"⏱️  所要時間: {int(elapsed // 60)}分{int(elapsed % 60)}秒")
        print(f"⚡ 平均速度: {total_inserted / elapsed:,.0f}件/秒")

        # 最終確認
        final_count = await get_existing_count(session)
        print(f"📈 総商品数: {final_count:,}件")
        print("=" * 80)

    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(seed_products())
    except KeyboardInterrupt:
        print("\n\n⚠️  処理が中断されました")
    except Exception as e:
        print(f"\n\n❌ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()

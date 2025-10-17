"""
パフォーマンステスト実行スクリプト

1000万件のデータに対してAPIのパフォーマンスを計測します。
"""

import subprocess
import sys
from datetime import UTC, datetime

# カラー出力用
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_header(message: str):
    """ヘッダーを出力"""
    print("\n" + "=" * 80)
    print(f"{BOLD}{BLUE}{message}{RESET}")
    print("=" * 80)


def print_success(message: str):
    """成功メッセージを出力"""
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message: str):
    """エラーメッセージを出力"""
    print(f"{RED}❌ {message}{RESET}")


def print_warning(message: str):
    """警告メッセージを出力"""
    print(f"{YELLOW}⚠️  {message}{RESET}")


def print_info(message: str):
    """情報メッセージを出力"""
    print(f"{BLUE}ℹ️  {message}{RESET}")


def check_data_count():
    """データ件数を確認"""
    try:
        result = subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "-T",
                "db",
                "psql",
                "-U",
                "postgres",
                "-d",
                "ultra_fast_db",
                "-t",
                "-c",
                "SELECT COUNT(*) FROM products;",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        count = int(result.stdout.strip())
        return count
    except Exception as e:
        print_error(f"データ件数の確認に失敗しました: {e}")
        return 0


def run_performance_tests():
    """パフォーマンステストを実行"""
    print_header("🚀 パフォーマンステスト実行")

    # Dockerが起動しているか確認
    print_info("Dockerコンテナの状態を確認中...")
    result = subprocess.run(
        ["docker", "compose", "ps", "-q", "api"],
        capture_output=True,
        text=True,
    )

    if not result.stdout.strip():
        print_error("APIコンテナが起動していません")
        print_info("以下のコマンドで起動してください:")
        print("  docker compose up -d")
        return False

    print_success("APIコンテナが起動しています")

    # データ件数確認
    print_info("商品データ件数を確認中...")
    count = check_data_count()

    print(f"\n📊 現在の商品データ件数: {count:,}件")

    if count < 100_000:
        print_warning(f"パフォーマンステストには最低10万件のデータが推奨されます（現在: {count:,}件）")
        print_info("データを生成するには以下のコマンドを実行してください:")
        print("  docker compose exec api uv run python scripts/seed_products.py")
        print()
        response = input("このまま続行しますか？ (y/N): ")
        if response.lower() != "y":
            print_info("テストを中止しました")
            return False

    # パフォーマンステスト実行
    print_header("📈 パフォーマンステスト開始")
    print(f"開始時刻: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()

    try:
        result = subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "-T",
                "api",
                "uv",
                "run",
                "pytest",
                "tests/performance/",
                "-v",
                "--tb=short",
                "--color=yes",
            ],
            check=False,
        )

        print()
        print_header("📊 テスト結果サマリー")

        if result.returncode == 0:
            print_success("全てのパフォーマンステストが成功しました！")
            print_info("全てのAPIエンドポイントが1秒以内に応答しています")
            return True
        else:
            print_error("一部のパフォーマンステストが失敗しました")
            print_info("詳細は上記のログを確認してください")
            return False

    except KeyboardInterrupt:
        print()
        print_warning("テストが中断されました")
        return False
    except Exception as e:
        print_error(f"テスト実行中にエラーが発生しました: {e}")
        return False


def main():
    """メイン関数"""
    print_header("⚡ UltraFastAPI パフォーマンステストスイート")
    print(f"実行日時: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")

    try:
        success = run_performance_tests()

        print()
        print_header("🏁 テスト完了")

        if success:
            print_success("パフォーマンステストが正常に完了しました")
            print()
            print("📝 テスト項目:")
            print("  ✅ 商品一覧（初期ページ）: < 1秒")
            print("  ✅ カーソルベースページネーション: < 1秒")
            print("  ✅ フィルタリング（4パターン）: < 1秒")
            print("  ✅ 検索機能（3パターン）: < 1秒")
            print("  ✅ 商品詳細取得: < 500ms")
            sys.exit(0)
        else:
            print_error("パフォーマンステストが失敗しました")
            print_info("詳細なログを確認してください")
            sys.exit(1)

    except Exception as e:
        print_error(f"予期しないエラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

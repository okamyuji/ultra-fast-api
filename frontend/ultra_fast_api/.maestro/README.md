# Maestro UIテスト

## 概要

このディレクトリには、Ultra Fast APIアプリケーションのMaestro UIテストが含まれています。

## テストフロー

### 1. login_flow.yaml

- ログイン画面の基本的なフロー
- メールアドレスとパスワードを入力してログイン
- ホーム画面が表示されることを確認

### 2. product_list_flow.yaml

- ログイン後に商品一覧画面へ遷移
- 商品一覧が表示されることを確認
- スクロールして追加の商品を確認

### 3. product_search_flow.yaml

- 商品検索機能のテスト
- 検索バーに「商品」と入力
- 検索結果が表示されることを確認

### 4. settings_flow.yaml

- 設定画面へのアクセステスト
- 設定アイコンをタップ
- 設定画面が表示されることを確認

## 実行方法

### 個別のフローを実行

```bash
cd /Users/systemi/devs/python/ultra-fast-api/frontend/ultra_fast_api
maestro test .maestro/login_flow.yaml
```

### すべてのフローを実行

```bash
cd /Users/systemi/devs/python/ultra-fast-api/frontend/ultra_fast_api
maestro test .maestro/
```

## 前提条件

1. バックエンドAPIが起動していること  <http://192.168.0.15:8000>
2. テストユーザー（`test@example.com` / Password123）が存在すること
3. iOSシミュレータまたはAndroidエミュレータが起動していること

## 注意事項

- Maestroは実機またはシミュレータ/エミュレータで実行されます
- テスト実行前にアプリをビルドしておく必要があります
- 環境変数ENV=defaultを設定して本番設定（192.168.0.15）を使用します

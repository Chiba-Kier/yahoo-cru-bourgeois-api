# Yahoo! Cru Bourgeois API

Yahoo!ショッピングAPIを利用し、特定のクリュ・ブルジョワ銘柄を検索・抽出するAPIサーバーです。

## 1. セットアップ

### 1.1. 依存ライブラリのインストール
Python 3.10以上を推奨します。

```bash
# 仮想環境の作成（任意）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# インストール
pip install -r requirements.txt
```

### 1.2. Yahoo! Application ID の設定
このAPIの実行には、Yahoo!ショッピングAPIの **Client ID (Application ID)** が必要です。

1. [Yahoo!デベロッパーネットワーク](https://developer.yahoo.co.jp/)でアプリケーションを登録し、IDを取得します。
2. プロジェクト直下の `.env` ファイルに、IDを以下の形式で保存してください。

```text
YAHOO_CLIENT_ID=あなたのアプリケーションID
```
※ `.env` ファイルは `.gitignore` に追加されており、Git管理対象外です。秘密情報の漏洩に注意してください。

## 2. 実行方法

APIサーバーを起動します。

```bash
python main.py
```

サーバーはデフォルトで `http://localhost:8000` で待機します。

## 3. APIの使い方

### 検索エンドポイント (`/search`)
マスタデータ (`data/master_data.csv`) に登録された銘柄を全件検索します。

- **URL**: `GET /search`
- **クエリパラメータ**:
    - `min_price`: 最低価格 (オプション)
    - `max_price`: 最高価格 (オプション)

#### 例: 2000円〜4000円の範囲で検索
```bash
curl "http://localhost:8000/search?min_price=2000&max_price=4000"
```

## 4. マスタデータの管理
検索対象の銘柄は `data/master_data.csv` で管理しています。

- `chateau_name`: 仏語名称（表示用）
- `appellation`: 格付け/産地
- `search_name_ascii`: アルファベットの検索用キーワード
- `search_name_kana`: カタカナの検索用キーワード（**最もヒット率が高いため重要**）

## 5. ライセンス
このプロジェクトは [MIT License](LICENSE) の下で公開されています。

---
**注意**: 本ツールは個人の利用を目的としており、Yahoo!ショッピングAPIの[利用規約](https://developer.yahoo.co.jp/appendix/usage/terms.html)を遵守して使用してください（1 QPS制限等）。

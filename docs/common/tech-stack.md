# 技術スタック

## 採用技術と役割

| 層 | 担当 |
| --- | --- |
| Next.js / TypeScript | App Routerによる画面、Markdown本文と数式の描画、知識カード、Googleログインの画面、FastAPIへの同一オリジン中継 |
| FastAPI / Python | 入出力検証、教材取得、前提探索、問題選択、学習履歴の保存、復習計算、OpenAPI |
| PostgreSQL & pgvector | 教材・関係・履歴・復習状態の正本。通常のテーブルとJSONBのみを使用 |
| SQLAlchemy / Alembic | APIのDBアクセスと、新規DB用のマイグレーション |
| CLI | 教材JSONの検証・登録と、AIによる事前生成 |

## 認証

- 初版からGoogleアカウントによるログインを必須とする。
- 認証ライブラリとセッションの管理方式は、実装前に決める。

## データ形式と描画

- 問題キャッシュ、知識要素の本文はそれぞれmd形式のテキストとしてdbで管理する。
- 時刻はUTCの`timestamptz`で保存し、画面ではAsia/Tokyoで表示する。
- 数式はTeX対応レンダラーで描画する。具体的なライブラリはspec.mdでは指定されていない。

## ローカル実行と検証

- `compose.yaml`でPostgreSQL・API・Webをローカル起動する。
- Python側の実行・検証には`uv`を使う。

## AI接続

- とりあえずOpen AI APIで実験する。

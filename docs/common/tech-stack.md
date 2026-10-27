# 技術スタック

## 採用技術と役割

| 層 | 担当 |
| --- | --- |
| Next.js / TypeScript | App Routerによる画面、Markdown本文と数式の描画、知識カード、ログインボタン・ログイン状態の表示、FastAPIへの同一オリジン中継 |
| FastAPI / Python | Googleログイン・ユーザー登録・セッション・本人確認・退会、入出力検証、教材取得、前提探索、問題選択、学習履歴の保存、復習計算、OpenAPI |
| PostgreSQL & pgvector | 教材・関係・履歴・復習状態の正本。通常のテーブルとJSONBのみを使用 |
| SQLAlchemy / Alembic | APIのDBアクセスと、新規DB用のマイグレーション |
| CLI | 教材JSONの検証・登録と、AIによる事前生成 |

## 認証

- 2026-10-13、認証をFastAPI側へ集約する方向へ変更（ユーザー確認済み）。
- Googleログイン・内部ユーザー登録・ログイン状態・本人確認・ログアウトと退会はAPI側が担当する。
- Next.jsはボタン・画面表示・同一オリジン中継を担当する。Next.js側で別の認証セッションやAPI用署名JWTを作らない。
- Google OAuth/OIDC処理はAuthlibのFastAPI/Starlette連携を候補とする。OAuth処理やトークン検証を独自実装しない。
- セッション方式は新構成に合わせて選定する。最後の利用から24時間という要件は維持するが、旧Auth.js JWT・API用60秒トークン・RS256鍵分担は旧案とする。
- 既存Auth.jsコードとDBの記録テーブルは、移行確認後にユーザーが整理する。今回削除しない。

根拠：[AuthlibのFastAPI連携](https://blog.authlib.org/2020/fastapi-google-login)、[Starlette連携](https://docs.authlib.org/en/v1.6.9/client/starlette.html)。詳細は [認証の現行方針](../ai/auth.md)。

## データ形式と描画

- 問題キャッシュ、知識要素の本文はそれぞれmd形式のテキストとしてdbで管理する。
- 時刻はUTCの`timestamptz`で保存し、画面ではAsia/Tokyoで表示する。
- 本文表示はMarkdown＋TeX数式と知識リンクの詳細パネルで確認済み。
- 描画ライブラリはreact-markdown・remark-gfm・remark-math・rehype-katex・KaTeX。設定案は [技術設定](runtime-settings.md) にまとめる（確認済み）。

## ローカル実行と検証

- 初版はPostgreSQL・API・Webを全てローカル起動する（確認済み）。`compose.yaml`でまとめて起動する。
- Python側の実行・検証には`uv`を使う。

## AI接続

- とりあえずOpen AI APIで実験する。

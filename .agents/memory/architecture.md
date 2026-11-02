# 構成と主要フロー

確認日: 2026-10-30

- `apps/web/` は Next.js App Router、`apps/api/` は FastAPI、DB はローカル PostgreSQL。Web の `/api/*` は Next.js の rewrite で API の 127.0.0.1:8000 に転送される（`apps/web/next.config.ts`、`apps/api/src/api/main.py`、`compose.yaml`）。
- Google OAuth のコールバックで内部ユーザーを登録し、署名付きセッションに ID を保存する。保護された API はユーザーの存在と Google 紐付けを確認する（`apps/api/src/api/auth.py`、`apps/api/src/api/main.py`）。
- 試験一覧・詳細から演習を予約し、画面表示時に開始時刻を記録、解答閲覧の POST で初回閲覧時刻を記録する。未閲覧時は解答・解説と知識名を返さない。現在の出題は対象試験の未廃止問題を ID 順で最初の1件選択する（`apps/api/src/api/exams.py`、`apps/api/src/api/attempts.py`、`apps/web/src/components/attempt-home.tsx`）。
- 演習更新は Origin を確認しユーザー行をロックする。予約はクライアント生成 ID を使い再送可能で、進行中の演習があればその ID を 409 で返す（`apps/api/src/api/attempts.py`、`apps/web/src/components/start-attempt.tsx`）。
- ORM とスキーマ変更は `apps/api/src/api/models.py` と `apps/api/migrations/`。評価下書き UI は `apps/web/src/components/attempt-feedback.tsx` にあるが、確認時点では演習画面に接続されておらず、確定 API も `attempts.py` にない。
- Markdown と数式は React Markdown、remark、KaTeX で描画し、HTML を除外する（`apps/web/src/components/attempt-home.tsx`、`apps/web/src/components/attempt-answer.tsx`）。

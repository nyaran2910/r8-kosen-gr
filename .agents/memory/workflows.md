# 開発・検証手順

確認日: 2026-10-30。以下は定義・文書を確認した手順であり、この調査では実行していない。

- ルートの `just up-db` で PostgreSQL を起動。`just api::alembic-head` でマイグレーション、`just seed-db` で確認用データを投入する。シードは固定 ID の既存データを上書きしない（`justfile`、`apps/api/justfile`、`assets/seeds/README.md`）。
- `just api::dev` と `just web::dev` で開発サーバーを起動する。API はルートの環境ファイルを uv に渡す設定（`apps/api/justfile`、`apps/web/justfile`）。設定名と条件は `docs/common/api.md`、`docs/common/runtime-settings.md` を参照し、秘密値をメモリに保存しない。
- Web は `apps/web` で `pnpm lint`、`pnpm build` が定義されている。API の manifest にテストコマンドの定義は見当たらない（`apps/web/package.json`、`apps/api/pyproject.toml`）。受け入れ確認の手順は `docs/common/acceptance-check.md`。
- Web の変更前には配下の `apps/web/AGENTS.md` に従い、インストール済み Next.js の該当ガイドを確認する。

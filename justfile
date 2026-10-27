mod web "apps/web"
mod api "apps/api"

default:
  just --list --list-submodules

up-db:
    docker compose up -d db

check-db database:
    docker compose exec db psql -U learning -d learning -c '\d {{database}}'

# 動作確認用教材を追加する。既存の同じIDは上書きしない。
seed-db:
    docker compose exec -T db psql -X -v ON_ERROR_STOP=1 -U learning -d learning < assets/seeds/demo.sql

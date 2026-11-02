# プロジェクト概要

確認日: 2026-10-30

- 高等教育の学習で資料選択や問題・解答間の移動などの負担を減らす研究用システム。知識要素と問題、解答、解説、学習履歴などを扱う構想がある（`README.md`）。
- 初版の計画はローカルの学習アプリで、対象は編入数学。計画には評価、復習、履歴なども含まれるが、計画と実装済み機能は区別する（`docs/common/first-release.md`、`apps/api/src/api/attempts.py`）。
- `assets/sources/` は資料、`assets/seeds/demo.sql` は独自の動作確認用教材。資料の利用・公表方針は `docs/common/legal.md` を確認する（`README.md`、`assets/seeds/README.md`）。
- 仕様と現在地は `docs/common/`、詳細な根拠・作業文脈は `docs/ai/`。決定変更時は対応する概要と詳細を同時更新する（`docs/README.md`、`docs/ai/README.md`）。

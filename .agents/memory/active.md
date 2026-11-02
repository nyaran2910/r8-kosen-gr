# 作業の継続点

確認日: 2026-10-30。最新のソースを再確認してから続ける。

- 演習予約・開始・解答表示と知識一覧取得までのAPIがある。問題選択は未廃止問題をID順に最初の1件選ぶ暫定実装で、復習優先ロジックではない（`apps/api/src/api/attempts.py`）。
- `apps/web/src/components/attempt-feedback.tsx` に評価の入力・sessionStorage下書き用コンポーネントが作られているが、現時点で `attempt-home.tsx` に接続されていない。`attempt-answer.tsx` は `onRevealed` を受け取るが成功後に呼んでおらず、解答閲覧直後の親画面の知識一覧更新に未対応。ユーザーが自分で仕上げるため、次の案内時に現状を再確認する。
- 評価確定API・画面からの送信、理解度と復習予定の保存、未確定終了、下書きのログアウト・確定・終了時の削除は未完成。スキーマの存在と機能実装を混同しない（`apps/api/src/api/models.py`、`apps/api/src/api/attempts.py`、`apps/web/src/components/account-controls.tsx`）。
- ユーザーは直近、TypeScriptの `typeof`、`keyof`、文字列リテラル型を学んでいた。複雑な型表現は必要性を説明し、分かりやすい選択肢を優先する。

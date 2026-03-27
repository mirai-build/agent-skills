# 整合性チェックリスト

画面構成ドキュメントを更新したら、少なくとも次の観点で整合性を確認する。

## 前提文書

- `domain_model/01_system_purpose` と `02_actors` が、UX 設計の前提として参照できる状態か。
- `domain_model/04_journeys` が存在し、対象ジャーニーの開始条件と完了条件を追えるか。
- `domain_model/03_usecases` を補助参照に使う場合、画面の主操作と矛盾していないか。
- `ux/01_experience_scope/00_overview.md` と `02_user_journeys/00_overview.md` が、正本へのリンクを正しく案内しているか。

## 用語

- 画面名、ジャーニー名、actor 名、状態名が `domain_model` と一致しているか。
- 同じ画面に複数の呼び名を使っていないか。
- 仮置きの画面名が残っている場合、その理由と正式名称の未確定が明記されているか。

## `00_overview.md`

- `ux/00_overview.md` が最新で、`01_experience_scope` `02_user_journeys` `03_basic_layouts` `04_screen_inventory` `05_navigation_map` `06_screen_details` の入口を正しく案内しているか。
- 各カテゴリの `00_overview.md` に載せた項目ごとに、対応する詳細ドキュメントが存在するか。
- 詳細を追加または削除したのに、一覧が更新漏れになっていないか。

## `basic_layouts`

- 基本構成ごとに、ナビゲーション方針、画面の大分類、レイアウトの基本型、共通 UI 領域を追えるか。
- 複数の基本構成パターンがある場合、使い分け条件を説明できるか。
- 基本構成がワイヤーや詳細 UI 仕様に踏み込みすぎていないか。
- 存在しない共通 UI 領域を惰性的に列挙していないか。
- 本来あるべきところを意図的に外している共通 UI 領域がある場合、その理由が残っているか。

## `screen_inventory`

- 画面一覧 overview に、画面名、簡単な説明、対応ジャーニー、基本構成の対応が載っているか。
- 一覧へ載せた画面が `navigation_map` と `screen_details` で同じ名前で参照されているか。
- 画面一覧が遷移責務や詳細責務を抱え込みすぎていないか。

## `navigation_map`

- 1 ジャーニー 1 ファイルの単位が守られているか。
- Mermaid の遷移図と、遷移条件の表が一致しているか。
- 正常遷移だけでなく、キャンセル、差し戻し、権限不足、離脱などの重要な例外遷移を追えるか。
- 各遷移先の画面が `screen_inventory` に存在し、名称が一致しているか。
- 遷移の起点と終点が `user_journeys` の流れと矛盾していないか。

## `screen_details`

- 1 画面 1 ファイルの単位が守られているか。
- 各画面で、参照する基本構成、目的、主 actor、対応ジャーニー、開始条件、完了条件、主要状態、関連 context を追えるか。
- 基本構成で定義した共通 UI 領域のうち、この画面で使うものと、必要なら意図的に外すものを説明できるか。
- `入口と出口` のような遷移定義を持ち込まず、遷移責務を `navigation_map` へ寄せられているか。
- 表示責務と操作責務が、画面一覧の簡単な説明と矛盾していないか。

## 更新時の確認

- 上流の `domain_model` が更新された場合、関連する `basic_layouts` `screen_inventory` `navigation_map` `screen_details` を見直したか。
- `basic_layouts` の更新が必要なときに、`screen_inventory` `screen_details` へ差分が漏れていないか。
- `screen_inventory` の更新が必要なときに、`navigation_map` や `screen_details` へ差分が漏れていないか。
- 仮置きだった前提が確定したとき、関連文書をまとめて更新したか。
- 未解決事項と次に確認したい質問を残せているか。

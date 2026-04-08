# Context 分割の判断基準

この文書は `src/features/<context>/<feature>` の形で context を切るか、`src/features/<feature>` の flat 構成で進めるかを判断するための基準をまとめる。
過剰な入れ子を避けつつ、将来の保守で破綻しない粒度を選ぶ。

## context を切るべき場面

- 同じ domain の中に、一覧、詳細、作成、編集、削除、検索のような複数 feature がある。
- 複数 feature で共有する type、helper、query key、validation schema が一定量ある。
- route 群が domain ごとにまとまっており、context 単位で画面群を説明できる。
- team や ownership が domain 単位で分かれている。
- 今回の変更だけでなく、近い将来に同 domain 配下へ feature が増える見込みが高い。

例:

- `products/product-list`
- `products/product-detail`
- `products/product-creation`

この場合は `products/shared/` を置けるため、一覧と詳細で使う `Product` type や helper を自然に集約できる。

## flat feature で十分な場面

- repo 全体がまだ小さく、feature 数が少ない。
- 1 つの feature が独立しており、共通 language や shared asset がほとんどない。
- context を切っても、その中に feature が 1 つしか存在しない状態が長く続きそうである。
- 今回の task が局所修正で、context 導入のために unrelated file を大きく移動する必要がある。

例:

- `src/features/login-form`
- `src/features/profile-menu`

この規模なら、まず flat に保ち、複数 feature が揃ってから context 化する方が保守しやすい。

## repo 既存構成があるときの優先順位

- 既存 repo がすでに flat feature で安定運用されているなら、今回の task だけで全体を context 構成へ移し替えない。
- 既存 repo が domain ごとの folder を持っているなら、その語彙を優先して context 名に使う。
- `docs/` や設計書に bounded context や domain 分割があるなら、その境界を first candidate にする。

## 判断が難しいときに見る観点

1. 今回の変更で触る route は 1 つか、同じ domain の複数 route か。
2. 共有したい type / helper / store は feature をまたいで実在するか。
3. context 名にしたい語が、repo 内で共通 language としてすでに使われているか。
4. context を導入すると、関係ない feature まで大きく移動するか。

## ユーザーへ確認すべき条件

- flat と context のどちらにも妥当性があり、今回の判断で top-level tree が大きく変わる。
- 複数の context 名候補があり、repo の document や code から優先順位を決め切れない。
- 既存 feature をまとめ直すリファクタが今回の task 範囲を超える。

上の条件に当てはまる場合は、独断で tree を広げず、候補と影響範囲を添えてユーザーへ確認する。

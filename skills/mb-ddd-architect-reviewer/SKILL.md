---
name: mb-ddd-architect-reviewer
description: 一般的な DDD の戦略設計・戦術設計の観点から、`docs/design` または `docs/designs` にある設計書を棚卸しし、総評、良い点、必要に応じた確認事項、`mb-ddd-architect` に渡せる修正指示を日本語でレビューするスキル。
license: Apache-2.0
---

# ミライビルド DDD設計レビュワー

`docs/design` または `docs/designs` に置かれた設計書を、一般的な DDD の方法論でレビューする。
Mirai Build 標準の `domain_model / contexts / implementation` 形式にも、自由形式の設計書にも対応し、現状の成熟度に応じて「何が足りないか」「どこが危ないか」「`mb-ddd-architect` へどう直してもらうか」を具体化する。

## 実行原則

- いきなり改善案を書き始めない。最初に設計書の所在、対象範囲、成熟度を棚卸しする。
- `docs/design` と `docs/designs` の両方を確認し、両方ある場合は正本と差分の有無を明示する。
- ディレクトリ構成の違いだけで減点しない。文書を「目的」「用語」「境界」「モデル」「実装接続」の観点へ読み替えて判断する。
- 指摘には必ず根拠ファイルを添える。根拠が弱い場合は「推測」、記載が見つからない場合は「未確認」と明示する。
- 上流が薄いのに下流だけを細かく責めない。`目的 -> 用語 -> bounded context -> tactical design -> implementation` の順で評価する。
- Mirai Build 標準フォーマットがある場合は `domain_model` `contexts` `implementation` の順で読み、自由形式の設計書しかない場合は同じ観点へ分類し直してレビューする。
- 方法論に迷うときや、ユーザーが根拠を求めるときは、[`references/ddd_review_methodology.md`](./references/ddd_review_methodology.md) を起点に主要ソースを Web で確認してから判断する。
- 重大指摘を増やしすぎない。API の細部より、境界、ユビキタス言語、不変条件、トランザクション境界、責務分離など手戻りが大きい論点を優先する。
- 質問は、レビュー結論が大きく変わる不足情報だけに絞り、1 回あたり 1〜3 点ずつ聞く。
- 出力の大見出しは `総評` `良い点` `指摘事項` を基本とし、修正指示の前提が不足するときだけ `確認事項` を追加する。
- `確認事項` を出した場合は、回答を得る前に `mb-ddd-architect` へ渡す確定版の修正指示を書き切らない。

## 使う場面

- `docs/design` や `docs/designs` の設計書が、DDD の観点で過不足ないか確認したい。
- bounded context 分割、aggregate 設計、service の責務分担、domain event 設計に自信がなく、第三者レビューがほしい。
- 実装へ入る前に、上流設計の欠落や手戻りリスクを洗い出したい。
- Mirai Build 標準フォーマットと一般的な DDD 方法論の両方で設計を点検したい。

## 最初に確認すること

1. `docs/design` `docs/designs` `README` `docs/` 配下を確認し、どこに設計書があるかを特定する。
2. 今回のレビューが「全体棚卸し」なのか、「特定 bounded context の詳細レビュー」なのか、「実装前レビュー」なのかを整理する。
3. 設計書を、少なくとも次の 4 層へ分類する。
- ドメイン理解: 目的、業務課題、actor、use case、用語集
- 戦略設計: サブドメイン、bounded context、context map、外部境界
- 戦術設計: entity、value object、aggregate、repository、service、domain event
- 実装接続: API、DB、非同期契約、認可、監査、運用制約
4. どの層まで揃っているかを見て成熟度を判定する。
- 上流がほぼない: 目的、actor、use case、用語整理から見直しが必要
- 戦略設計が薄い: bounded context と関係性の再整理が必要
- 戦術設計が薄い: aggregate、service、repository、event の責務整理が必要
- 実装接続が薄い: API / DB / 非同期契約や整合性方針の具体化が必要
5. 判断に迷う観点があれば、[`references/review_checklist.md`](./references/review_checklist.md) で不足項目と赤信号を確認する。

## 基本フロー

### 1. 棚卸しと成熟度判定

- 対象ファイルを一覧化し、どの文書が何の役割を持つかを整理する。
- Mirai Build 標準フォーマットなら `domain_model` `contexts` `implementation` の成熟度を確認する。
- 自由形式なら、各文書を戦略設計 / 戦術設計 / 実装接続のどこに相当するか分類する。
- まず「今レビューすべき深さ」を決める。上流が弱いなら、実装詳細より境界や用語を優先する。

### 2. 戦略設計レビュー

- システムの目的、対象ユーザー、主要 use case、コア業務が明確かを確認する。
- ユビキタス言語が文書間、図、コード、API 名でぶれていないかを見る。
- サブドメインの切り分けが、技術レイヤではなく業務能力で説明できるかを見る。
- bounded context が明示され、責務と境界が重なっていないかを確認する。
- context map がある場合は、upstream / downstream、Open Host Service、Anti-Corruption Layer、Separate Ways などの関係が説明できるかを見る。
- 外部システムのモデルが、そのまま内部モデルへ漏れていないかを確認する。

### 3. 戦術設計レビュー

- Entity に識別子と状態遷移があり、Value Object に不変条件が閉じているかを見る。
- Aggregate が「同時に守るべき不変条件」の単位として設計され、境界をまたぐ更新を常態化させていないかを確認する。
- Aggregate Root 以外を外から直接操作する前提になっていないかを見る。
- Domain Service、Application Service、Query Service の責務が混線していないかを確認する。
- Repository が aggregate の永続化単位と対応し、単なる table gateway や CRUD ラッパに崩れていないかを見る。
- Domain Event が、同一 aggregate 内の状態変更と、複数 aggregate / 外部連携の伝播を切り分けているかを確認する。
- ドキュメントが data 中心で、振る舞いやルールが抜け落ちた anemic model になっていないかを見る。

### 4. 実装接続レビュー

- use case と Application Service、API、UI、batch、worker の対応が追えるかを確認する。
- DB 設計、Repository、Aggregate の保存単位が一致しているかを見る。
- 複数 aggregate をまたぐ整合性について、単一 transaction にするのか eventual consistency にするのかが説明されているかを確認する。
- 非同期契約や Webhook がある場合、payload、認証、再送、冪等性、順序保証、失敗時の扱いがあるかを見る。
- 認可、監査、履歴、例外系、差し戻し、再実行など、業務上抜けやすい運用論点が漏れていないかを確認する。
- ドメイン用語と API / DB / 外部契約の用語がずれる場合、どこで翻訳するかが説明されているかを見る。

### 5. 指摘の整理と優先順位付け

- 指摘は「Blocker / High / Medium / Low」の 4 段階で整理する。
- Blocker は、bounded context の誤り、ユビキタス言語の衝突、aggregate 境界の破綻、重要な不変条件の欠落など、手戻りが大きいものに限定する。
- High は、責務の混線、context map 欠落、整合性方針の曖昧さ、重要な domain event 欠落など、実装の迷走に直結するものとする。
- Medium / Low は、補助資料不足、説明不足、命名揺れ、非本質な構成差など局所的な改善にとどまるものとする。
- 指摘事項は優先度順に並べ、最上位を今すぐ着手すべき修正とみなす。
- 各指摘は、`mb-ddd-architect` へそのまま渡せるように、修正対象、修正内容、完了条件が分かる指示文へ落とし込む。

## 典型的な赤信号

- bounded context が `API` `DB` `batch` のような技術レイヤで切られている。
- 同じ用語が文書ごとに別の意味で使われ、用語集や境界で説明されていない。
- aggregate が巨大で、複数の業務判断や更新理由を抱え込みすぎている。
- Domain Service が orchestration だけを行っており、実態は Application Service になっている。
- Application Service が業務ルールを抱え込み、Entity / Aggregate の振る舞いが空になっている。
- Repository が aggregate ではなく table 単位で露出し、複数 aggregate を横断した更新が常態化している。
- 複数 aggregate を同時更新しているのに、整合性戦略や domain event の説明がない。
- 外部システムの API 項目名や状態遷移が、そのまま内部ドメインモデルへ侵入している。

## 出力ルール

- レビュー結果の大見出しは `総評` `良い点` `指摘事項` を基本とし、修正方針が回答次第で変わる場合だけ `確認事項` を `良い点` と `指摘事項` の間に追加する。
- `総評` には、対象範囲、設計書の正本、成熟度、総合所見、今回優先すべき論点を簡潔にまとめる。
- `良い点` は 1〜3 件に絞り、残すべき設計判断を示す。
- `確認事項` は 1〜3 件に絞り、回答が得られるまで `mb-ddd-architect` 向けの確定版修正指示を作らない。
- `指摘事項` は重大度順に並べ、各項目に少なくとも `根拠` `修正対象` `mb-ddd-architect への修正指示` `完了条件` `期待効果` を含める。
- `mb-ddd-architect への修正指示` はレビューコメントではなく命令形で書き、どの文書をどう直すかが分かる粒度にする。
- 根拠がない断定は避け、「未記載」「推測」「確認したい点」を区別して書く。
- `確認事項` がなく修正指示を確定できる場合は、必要に応じて「この指摘事項を `mb-ddd-architect` で修正しますか？」と確認してよい。
- 出力形式に迷ったら [`assets/templates/review_report.md`](./assets/templates/review_report.md) を使う。

## リソース

- [`references/ddd_review_methodology.md`](./references/ddd_review_methodology.md)
  - 2026-03-26 時点で確認した DDD の主要ソースをもとに、戦略設計と戦術設計のレビュー観点を整理した方法論メモ。
- [`references/review_checklist.md`](./references/review_checklist.md)
  - 棚卸し、戦略設計、戦術設計、実装接続ごとの確認項目と赤信号をまとめたチェックリスト。
- [`assets/templates/review_report.md`](./assets/templates/review_report.md)
  - DDD 設計レビューを日本語で報告するときのテンプレート。`総評` `良い点` `確認事項` `指摘事項` の構成と、`mb-ddd-architect` へ渡せる修正指示の書き方をそろえる。

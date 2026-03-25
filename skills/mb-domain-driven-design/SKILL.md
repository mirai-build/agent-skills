---
name: mb-domain-driven-design
description: ドメイン駆動設計に沿って、ユーザーへ不足情報を質問しながら `docs/designs/domain_model` `docs/designs/strategy` `docs/designs/contexts` の設計書を Markdown で段階的に整備するスキル。システムの目的整理、コアドメインとサブドメインの特定、Mermaid のドメインモデル図、戦術的設計、bounded context ごとの設計書をテンプレートベースで一貫して作成・更新したいときに使う。
---

# MB ドメイン駆動設計

ユーザーと並走しながら、DDD に準じた設計書を Markdown で整備する。
推測だけで書き切らず、情報が不足している箇所は都度質問し、合意できた内容から `docs/designs/` 配下へ段階的に反映する。

## 実行原則

- いきなり本文を書き始めない。最初に既存資料と不足情報を確認する。
- 情報が不足しているときは、手戻りが少ない順に 1〜3 個ずつ質問する。質問には「なぜ必要か」を短く添える。
- 回答しづらそうな問いには、選択肢、具体例、たたき台を添えてユーザーの情報提供を促す。
- 確定事項、仮置き、未確定事項を区別して記載する。仮置きで進める場合は、どこが仮説かを明示する。
- 一覧の入口は各対象ディレクトリの `00_overview.md` とし、「一覧（概略）→ 詳細」の順で整理する。
- `contexts` では bounded context ごとにディレクトリを分け、その下を `01_value_objects` から `07_presentation` までのカテゴリ別ディレクトリに分ける。
- ドキュメントを追加または更新したら、対応する `00_overview.md` の一覧も同時に更新する。
- ドキュメントは `domain_model` → `strategy` → `contexts` の順で整備する。後続フェーズで前提が変わったら先行ドキュメントも見直す。
- 図は特別な指定がない限り Mermaid を使う。1 枚で複雑になりすぎるときは bounded context ごとに分割する。
- ユビキタス言語を守る。既存資料と別名が混在する場合は、どの用語を正とするか確認してから反映する。

## 使う場面

- 新規プロダクトや既存システムについて、DDD に沿った設計書を整備したい。
- 要件整理から戦術的設計、bounded context ごとの設計までを、ユーザーとの対話を通じて順番に深めたい。
- `docs/designs/domain_model` `docs/designs/strategy` `docs/designs/contexts` を共通フォーマットで継続運用したい。

## 最初に確認すること

1. 既存資料を確認する。少なくとも `docs/designs`、要件書、画面仕様、業務フロー、ユースケース、用語集、既存コードを調べる。
2. 今回の依頼が新規作成か更新かを整理し、対象システム、対象範囲、対象 bounded context を確認する。
3. ユーザーへ、次のような材料があれば共有してもらう。
- 企画書、要件定義、業務フロー、既存設計書
- 主要ユーザーと運用担当の情報
- 現場の困りごと、KPI、制約、非機能要件
- 既存の用語集、イベント一覧、画面、API、DB スキーマ
4. 情報が足りなければ、[`references/hearing_guide.md`](./references/hearing_guide.md) から該当フェーズの質問を選び、回答しやすい粒度にして尋ねる。

## 基本フロー

1. 現状把握
- 既存資料とディレクトリ構成を確認し、何が揃っていて何が不足しているかを要約する。
- 先に決めるべき論点と、仮置きで進められる論点を分ける。

2. ドメインモデリング
- まず `assets/templates/domain_model/00_overview.md` をもとに `docs/designs/domain_model/00_overview.md` を作成または更新し、少なくともコアドメイン（ドメイン境界）とサブドメインの一覧を整理する。
- `assets/templates/domain_model/01_system_purpose.md` をもとに、システムの目的整理を `docs/designs/domain_model/01_system_purpose.md` へ作成または更新する。
- `assets/templates/domain_model/02_subdomains.md` をもとに、コアドメイン、サブドメイン、bounded context 候補、ユビキタス言語を `docs/designs/domain_model/02_subdomains.md` へ整理する。
- イベントストーミングをそのまま実施できない場合でも、出来事、利用者の行動、ルール、例外、外部連携を時系列で引き出してからドメインを分類する。
- `assets/templates/domain_model/03_domain_model.md` をもとに、Mermaid の図と主要な概念整理を `docs/designs/domain_model/03_domain_model.md` へ反映する。
- 用語が増えてきたら `assets/templates/domain_model/99_glossary.md` をもとに `docs/designs/domain_model/99_glossary.md` を追加し、ユビキタス言語の正本を分けてもよい。
- 案件規模が大きい場合は、`actors` `usecases` `contexts` などの補助文書を `domain_model` 配下へ追加してよい。ただし、基幹 3 文書との対応関係を明記する。

3. 戦術的設計
- まず `assets/templates/strategy/00_overview.md` をもとに `docs/designs/strategy/00_overview.md` を作成または更新し、少なくとも ValueObject、Entity、Aggregate、DomainService、Repository、ApplicationService、Presentation の一覧を整理する。
- ドメインモデリングの結果を前提にして、`assets/templates/strategy/01_tactical_design.md` をもとに `docs/designs/strategy/01_tactical_design.md` を作成または更新する。
- Value Object、Entity、Aggregate、Domain Service、Repository、Application Service、Presentation を、責務、不変条件、境界、依存関係が分かる粒度で整理する。
- ここで情報が不足する場合は、識別子、状態遷移、一貫性境界、認可、検索要件、外部システム連携を優先して確認する。

4. コンテキスト設計
- `docs/designs/contexts/` では、bounded context ごとに `NN_<bounded-context>/` ディレクトリを作成する。
- 各 context ディレクトリでは、まず `assets/templates/contexts/context_template/00_overview.md` をもとに `docs/designs/contexts/NN_<bounded-context>/00_overview.md` を作成または更新し、その context の責務、主要ユースケース、関連文書を一覧で整理する。
- 続いて、同じ context ディレクトリ配下に `01_value_objects` `02_entities` `03_aggregates` `04_domain_services` `05_repositories` `06_application_services` `07_presentation` のカテゴリ別ディレクトリを作成する。
- 各カテゴリでは、まず `assets/templates/contexts/context_template/<category>/00_overview.md` をもとに `docs/designs/contexts/NN_<bounded-context>/<category>/00_overview.md` を作成または更新し、一覧を整理する。
- さらに必要に応じて `assets/templates/contexts/context_template/<category>/01_*.md` をもとに、カテゴリ配下へ設計対象ごとの短い詳細ドキュメントを追加する。ファイル名は `NN_<topic>.md` を基本とする。
- `contexts` では「1 bounded context の中で ValueObject から Presentation までを通して読めること」を優先しつつ、1 ドキュメントを短く保つためにカテゴリ別ディレクトリへ分ける。
- ドメインモデリングや戦術的設計から導けない事項は、質問して補完する。特に context の責務境界、入力契機、前提条件、例外系、永続化、権限、外部連携は曖昧なままにしない。
- コンテキスト設計の判断で上位設計を見直す必要が出たら、関連ドキュメントへ必ず差分を反映する。

5. 仕上げ
- 作成または更新したファイル、今回確定した内容、仮置きの前提、未解決の質問をまとめて共有する。
- 仕上げ前に [`references/consistency_checklist.md`](./references/consistency_checklist.md) を使って整合性を確認する。

## 質問の進め方

- 1 回の質問は 1〜3 テーマに絞り、回答しやすい順に並べる。
- 「業務フローを教えて下さい」だけでなく、「誰が何をきっかけに、どの情報を見て、何を完了とみなしますか」のように具体化する。
- 抽象的な問いには、例を添える。
  例: 「コアドメイン候補が複数あるなら、どこが競争優位の源泉か、どこなら他社と最も差がつくかを教えて下さい。」
- 答えが出ない場合は、仮説案を 1 つ提示し、「この理解で近いですか」と確認する。
- フェーズをまたぐ質問は避け、今のドキュメントに必要な問いを優先する。

## 出力ルール

- Markdown で作成する。
- 見出し構成はテンプレートを崩しすぎない。不要な節は理由が説明できるときだけ省略する。
- Mermaid 図はレビューしやすいように、要素名を日本語またはユビキタス言語で統一する。
- ファイルを更新したときは、関連する他ドキュメントも確認して不整合を残さない。
- 既存文書の用語と新規文書の用語が衝突する場合は、衝突点を明示してユーザーへ確認する。

## リソース

- [`references/hearing_guide.md`](./references/hearing_guide.md)
  - フェーズ別の質問例、イベントストーミングの促し方、情報提供をお願いするときの観点をまとめたガイド。
- [`references/consistency_checklist.md`](./references/consistency_checklist.md)
  - ドキュメント横断で整合性を点検するときの確認項目。
- `assets/templates/domain_model/`
  - `00_overview.md` を入口に、コアドメインとサブドメインの一覧から詳細へ進むためのテンプレート群。
- `assets/templates/strategy/`
  - `00_overview.md` を入口に、ValueObject から Presentation までの一覧と詳細へ進むためのテンプレート群。
- `assets/templates/contexts/context_template/`
  - 1 bounded context ディレクトリの中に `00_overview.md` とカテゴリ別ディレクトリを置き、その下で `一覧 → 短い詳細` を運用するためのテンプレート群。

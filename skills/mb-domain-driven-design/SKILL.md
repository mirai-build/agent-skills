---
name: mb-domain-driven-design
description: ドメイン駆動設計に沿って、リポジトリ内の `docs/designs` の成熟度を見極めながら、`docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation` を段階的に整備するスキル。設計がまだ薄いときは domain_model から始め、domain_model が揃ったら contexts を 1 件ずつ深め、domain_model と contexts が揃った bounded context に対して API や DB を含む実装向け設計へ進みたいときに使う。
license: Apache-2.0
---

# MB ドメイン駆動設計

ユーザーと並走しながら、DDD に準じた設計書を Markdown で整備する。
推測だけで書き切らず、情報が不足している箇所は都度質問し、合意できた内容から `docs/designs/` 配下へ段階的に反映する。

## 実行原則

- いきなり本文を書き始めない。最初に既存資料と不足情報を確認する。
- 最初に `docs/designs` 配下の成熟度を見て、今どのフェーズまで揃っているかを判定してから着手する。
- 情報が不足しているときは、手戻りが少ない順に 1〜3 個ずつ質問する。質問には「なぜ必要か」を短く添える。
- 回答しづらそうな問いには、選択肢、具体例、たたき台を添えてユーザーの情報提供を促す。
- 確定事項、仮置き、未確定事項を区別して記載する。仮置きで進める場合は、どこが仮説かを明示する。
- 一覧の入口は各対象ディレクトリの `00_overview.md` とし、「一覧（概略）→ 詳細」の順で整理する。
- `contexts` では bounded context ごとにディレクトリを分け、その下を `01_value_objects` `02_entities` `03_aggregates` `04_repositories` `05_services` `06_interfaces` のカテゴリ別ディレクトリに分ける。
- 実装向け設計が必要な場合は `implementation` でも bounded context ごとにディレクトリを分け、その下を少なくとも `01_api` `02_database` のカテゴリ別ディレクトリに分ける。
- `domain_model` 配下は `01_system_purpose` `02_actors` `03_usecases` `04_journeys` `05_bounded_contexts` の順で整理する。各段階はディレクトリを分け、原則「`00_overview.md` → 詳細文書」の形にそろえる。
- ユースケースは `03_usecases/00_overview.md` と `01_*.md` を正本とし、`contexts` や `implementation` の前提として扱う。
- アクター定義は `02_actors/00_overview.md` に集約し、個別詳細ファイルへ分割しない。
- ユーザージャーニーは `04_journeys/00_overview.md` と `01_*.md` を使い、関連ユースケースをつないだ簡易フローとして扱う。
- `domain_events` と `external_integrations` は、必要な context にだけ任意で追加する。必要がなければ作成しない。
- 実装向け設計は、ドメインや bounded context の責務を API や DB 都合で崩さずに具体化するための後段フェーズとして扱う。
- `contexts` の `domain_events` と `external_integrations` は概念設計として扱い、非同期イベントや Webhook がある場合の具体契約は `implementation` 側で別途定義する。
- ドキュメントを追加または更新したら、対応する `00_overview.md` の一覧も同時に更新する。
- `contexts` 配下では、`06_interfaces` を除き、標準カテゴリまたは任意カテゴリの一覧に載せた項目ごとに詳細ドキュメントを必ず 1 つ作成する。overview だけで止めない。
- `contexts` は一気に複数 context を広げず、原則 1 回の作業で 1 bounded context ずつ進める。
- `implementation` 配下でも、一覧に載せた API や DB 設計対象ごとに詳細ドキュメントを必ず 1 つ作成する。overview だけで止めない。
- ドキュメントは `domain_model` → `contexts` → `implementation` の順で整備する。後続フェーズで前提が変わったら先行ドキュメントも見直す。
- 先行フェーズが十分に揃っていないときは、後続フェーズへ進まない。特に `implementation` は、対象 bounded context の `domain_model` と `contexts` が揃ってから着手する。
- 上流フェーズが変わったときは、影響を受ける下流フェーズへ必ず差分を波及させる。`domain_model` を更新したら関連する `contexts` と `implementation` を、`contexts` を更新したら関連する `implementation` を必ず見直す。
- 図は特別な指定がない限り Mermaid を使う。1 枚で複雑になりすぎるときは bounded context ごとに分割する。
- ユビキタス言語を守る。既存資料と別名が混在する場合は、どの用語を正とするか確認してから反映する。
- 主要なユビキタス言語は、日本語名だけでなくシステム上で使う英語名も対で宣言する。英語名は原則 2 語以内の名詞句とし、API 名、DB 名、コード識別子へ流用しやすい形を優先する。

## 使う場面

- 新規プロダクトや既存システムについて、DDD に沿った設計書を整備したい。
- 要件整理から bounded context ごとの設計までを、ユーザーとの対話を通じて順番に深めたい。
- `docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation` を共通フォーマットで継続運用したい。
- 実装着手前に、bounded context ごとの API、永続化、DB 制約を設計書として固めたい。

## 最初に確認すること

1. 既存資料を確認する。少なくとも `docs/designs`、要件書、画面仕様、業務フロー、ユースケース、用語集、既存コードを調べる。
2. 今回の依頼が新規作成か更新かを整理し、対象システム、対象範囲、対象 bounded context を確認する。
3. `docs/designs` の成熟度を見て、次のどの段階にいるかを判定する。
- 設計が 0 に近い、または `domain_model` が未整備: `domain_model` の整備から始める。
- `domain_model` はあるが `contexts` が薄い: `contexts` を 1 bounded context ずつ整備する。
- 対象 bounded context の `domain_model` と `contexts` が揃っている: `implementation` で API / DB 設計へ進む。
4. ユーザーへ、次のような材料があれば共有してもらう。
- 企画書、要件定義、業務フロー、既存設計書
- 主要ユーザーと運用担当の情報
- 現場の困りごと、KPI、制約、非機能要件
- 既存の用語集、イベント一覧、画面、API、DB スキーマ
5. 情報が足りなければ、[`references/hearing_guide.md`](./references/hearing_guide.md) や [`references/implementation_design_guide.md`](./references/implementation_design_guide.md) から該当フェーズの質問を選び、回答しやすい粒度にして尋ねる。

## 成熟度に応じた進め方

### 1. 設計が 0 に近いとき

- `docs/designs/domain_model` を優先し、次の順で固める。
  1. `01_system_purpose`: システムの目的
  2. `02_actors`: アクター定義
  3. `03_usecases`: ユースケース整理
  4. `04_journeys`: ユースケースをつないだ流れの整理
  5. `05_bounded_contexts`: bounded context 分割
- この段階では `contexts` や `implementation` を無理に作り切らない。
- 後から `domain_model` を更新した場合は、その時点で既に存在する `contexts` と `implementation` へ必ず影響を反映する。

### 2. `domain_model` ができているとき

- `docs/designs/contexts` を整備する。
- 対象は 1 回の作業で 1 bounded context に絞る。
- 複数 context が候補にある場合は、価値が高いもの、手戻りが少ないもの、依存の少ないものから順に進める。
- `contexts` の責務、用語、ユースケースが変わった場合は、その context にぶら下がる `implementation` を必ず見直す。

### 3. `domain_model` と `contexts` が揃っているとき

- 対象 bounded context に対して `docs/designs/implementation` を整備する。
- API と DB は、対応する ApplicationService、QueryService、Repository、Aggregate が contexts 側で追えることを前提にする。
- `implementation` も必要な bounded context から順に進め、一度に全 context を広げない。

## 基本フロー

1. 現状把握
- 既存資料とディレクトリ構成を確認し、何が揃っていて何が不足しているかを要約する。
- 先に決めるべき論点と、仮置きで進められる論点を分ける。
- 成熟度判定に基づき、このターンで進める対象を `domain_model`、`contexts` の 1 context、`implementation` の 1 context のどれかに絞る。
- すでに下流ドキュメントが存在する場合は、今回の変更がどこまで波及するかを最初に洗い出す。

2. ドメインモデリング
- まず `assets/templates/domain_model/00_overview.md` をもとに `docs/designs/domain_model/00_overview.md` を作成または更新し、`01_system_purpose` `02_actors` `03_usecases` `04_journeys` `05_bounded_contexts` の整備順と入口を整理する。
- `assets/templates/domain_model/01_system_purpose/00_overview.md` と `01_system_purpose.md` をもとに、システムの目的整理を `docs/designs/domain_model/01_system_purpose/` へ作成または更新する。
- `assets/templates/domain_model/02_actors/00_overview.md` をもとに、主要 actor の定義を `docs/designs/domain_model/02_actors/00_overview.md` へ集約して作成または更新する。
- `assets/templates/domain_model/03_usecases/00_overview.md` と `01_usecase.md` をもとに、主要な操作単位を `docs/designs/domain_model/03_usecases/` へ整理する。ユースケースは `00_overview.md` を入口にし、各 usecase を `01_*.md` で管理する。
- `assets/templates/domain_model/04_journeys/00_overview.md` と `01_journey.md` をもとに、ユースケースを組み合わせた時系列の流れを `docs/designs/domain_model/04_journeys/` へ整理する。ジャーニーは `00_overview.md` を入口にし、各 journey を `01_*.md` で管理する。
- `assets/templates/domain_model/05_bounded_contexts/00_overview.md` `01_context_split.md` `02_context_map.md` をもとに、bounded context 分割を `docs/designs/domain_model/05_bounded_contexts/` へ整理する。
- イベントストーミングをそのまま実施できない場合でも、出来事、利用者の行動、ルール、例外、外部連携を時系列で引き出してからドメインを分類する。
- 特にコア業務は、責務や用語が分かれるなら bounded context 候補まで具体化する。支援業務も独立した責務や用語がある場合は context 候補を切る。
- 用語が増えてきたら `assets/templates/domain_model/99_glossary.md` をもとに `docs/designs/domain_model/99_glossary.md` を追加し、日本語名とシステム英語名を対で管理するユビキタス言語の正本を分けてもよい。
- 案件規模が大きい場合でも、基本は `01_system_purpose` `02_actors` `03_usecases` `04_journeys` `05_bounded_contexts` の 5 段階に沿って整理し、補助文書を足す場合はどの段階を支えるものか明記する。

3. コンテキスト設計
- このフェーズへ進むのは、少なくとも `domain_model` でコア業務 / 支援業務、bounded context 候補、主要用語が整理できている場合に限る。
- `docs/designs/contexts/` では、bounded context ごとに `NN_<bounded-context>/` ディレクトリを作成する。
- 1 回の作業対象は原則 1 bounded context に限定し、他 context へは同時に広げない。
- ドメインモデリングの結果を前提にして、各 context の中で ValueObject、Entity、Aggregate、Repository を整理したうえで、`services` 配下に DomainService、ApplicationService、QueryService をまとめて整理し、必要なインターフェースは `interfaces` 一覧で管理する。
- ドメインイベントが重要な context では `domain_events` を追加し、外部 API や外部システム連携が重要な context では `external_integrations` を追加する。
- 各 context ディレクトリでは、まず `assets/templates/contexts/context_template/00_overview.md` をもとに `docs/designs/contexts/NN_<bounded-context>/00_overview.md` を作成または更新し、その context の責務、主要ユースケース、関連文書を一覧で整理する。
- 続いて、同じ context ディレクトリ配下に `01_value_objects` `02_entities` `03_aggregates` `04_repositories` `05_services` `06_interfaces` のカテゴリ別ディレクトリを作成する。
- ドメインイベントや外部連携が重要な場合だけ、同じ context ディレクトリ配下へ `07_domain_events` `08_external_integrations` を追加する。
- 各カテゴリでは、まず `assets/templates/contexts/context_template/<category>/00_overview.md` をもとに `docs/designs/contexts/NN_<bounded-context>/<category>/00_overview.md` を作成または更新し、一覧を整理する。
- `06_interfaces` を除く各カテゴリで 1 件以上の項目がある場合は、`assets/templates/contexts/context_template/<category>/01_*.md` をもとに、一覧へ載せた設計対象ごとの短い詳細ドキュメントを必ず追加する。`05_services` では Service 種別に応じたテンプレートを選ぶ。`07_domain_events` `08_external_integrations` は必要な context にだけ追加する。ファイル名は `NN_<topic>.md` を基本とする。
- `contexts` では「1 bounded context の中で ValueObject から Service までの設計と、必要な Interface 一覧を通して読めること」を優先しつつ、1 ドキュメントを短く保つためにカテゴリ別ディレクトリへ分ける。
- `domain_events` は、非同期処理、通知、監査、状態遷移の追跡が重要な context で優先的に追加する。
- `external_integrations` は、外部 API、SaaS、他システム連携、非同期基盤との接続が重要な context で優先的に追加する。
- ドメインモデリングから導けない事項は、質問して補完する。特に識別子、状態遷移、一貫性境界、認可、検索要件、外部連携と、context の責務境界、入力契機、前提条件、例外系、永続化は曖昧なままにしない。
- コンテキスト設計の判断で上位設計を見直す必要が出たら、関連する `domain_model` と、存在する場合は対象 `implementation` へ必ず差分を反映する。

4. 実装向け設計
- このフェーズへ進むのは、対象 bounded context の `domain_model` と `contexts` が揃い、ApplicationService、QueryService、Repository、Aggregate の責務が追える場合に限る。
- 実装まで見据えた設計が必要な場合は、`docs/designs/implementation/00_overview.md` を作成または更新し、どの bounded context で API / DB 設計まで作るかを一覧化する。
- `docs/designs/implementation/` では、bounded context ごとに `NN_<bounded-context>/` ディレクトリを作成する。
- 1 回の作業対象は原則 1 bounded context に限定し、必要な API / DB 設計から順に追加する。
- 各 implementation context ディレクトリでは、まず `assets/templates/implementation/context_template/00_overview.md` をもとに `docs/designs/implementation/NN_<bounded-context>/00_overview.md` を作成または更新し、その context の実装対象、入口、保存対象、関連文書を一覧で整理する。
- 続いて、同じ implementation context ディレクトリ配下に少なくとも `01_api` `02_database` を作成する。非同期イベントや Webhook がある場合は `03_async_contracts` も追加する。batch、worker、read model、運用設計など追加の実装観点が必要なら `04_<topic>` 以降の任意カテゴリを追加してよい。
- `01_api` では `assets/templates/implementation/context_template/01_api/00_overview.md` と `openapi.yml` を使い、API 設計の正本を `docs/designs/implementation/NN_<bounded-context>/01_api/openapi.yml` として出力する。`openapi.yml` には少なくとも path、operation、request / response schema、error response、security、主要な example を含める。
- `02_database` では `assets/templates/implementation/context_template/02_database/00_overview.md` と `01_table.md` を使い、`00_overview.md` に Mermaid の ER 図を載せ、各 table の詳細を `01_<table-name>.md` で分割管理する。各 table 詳細では、`| 物理名 | 説明 | データ型 | 備考 |` の表形式でカラム一覧を必ず出力する。
- 非同期イベントや Webhook がある場合は `03_async_contracts` に `assets/templates/implementation/context_template/03_async_contracts/00_overview.md` と `01_contract.md` を使い、送信 / 受信契約ごとに topic / endpoint、payload、署名や認証、再送、冪等性、順序保証、失敗時の扱いを整理する。
- 実装向け設計で出てきた API 名、DB 名、外部契約名がユビキタス言語と異なる場合は、その対応関係を明示する。
- 実装向け設計の判断で `domain_model` や `contexts` の前提が変わる場合は、上位ドキュメントへ必ず差分を反映し、その後に影響を受ける他の `implementation` 文書も見直す。

5. 仕上げ
- 作成または更新したファイル、今回確定した内容、仮置きの前提、未解決の質問をまとめて共有する。
- 仕上げ前に [`references/consistency_checklist.md`](./references/consistency_checklist.md) を使って整合性を確認する。

## 質問の進め方

- 1 回の質問は 1〜3 テーマに絞り、回答しやすい順に並べる。
- 「業務フローを教えて下さい」だけでなく、「誰が何をきっかけに、どの情報を見て、何を完了とみなしますか」のように具体化する。
- 抽象的な問いには、例を添える。
  例: 「コア業務候補が複数あるなら、どこが競争優位の源泉か、どこなら他社と最も差がつくかを教えて下さい。」
- 答えが出ない場合は、仮説案を 1 つ提示し、「この理解で近いですか」と確認する。
- フェーズをまたぐ質問は避け、今のドキュメントに必要な問いを優先する。

## 出力ルール

- Markdown で作成する。
- 見出し構成はテンプレートを崩しすぎない。不要な節は理由が説明できるときだけ省略する。
- 詳細ドキュメントのタイトルはカテゴリ名ではなく、設計対象の実名にする。例: ValueObject の詳細なら `# MedicalHistoryAnswers` のように書く。
- テンプレート由来の使い方注記や説明文は、最終ドキュメントに残さない。
- Service の入力・出力で ValueObject を参照する場合は、対応する ValueObject ドキュメントへの Markdown リンクを貼る。
- ユースケースを作る場合は `domain_model/03_usecases/00_overview.md` を入口にし、各詳細は `01_*.md` で分割する。
- ユーザージャーニーを作る場合は `domain_model/04_journeys/00_overview.md` を入口にし、各詳細は `01_*.md` で分割する。
- ユーザージャーニーは感情や印象評価ではなく、関連ユースケースをつないだ簡易フローとして記述する。
- `contexts` や `implementation` ではユースケースやユーザージャーニー全文を重複させず、必要な文書への Markdown リンクで参照する。
- 実装向け設計の API / DB 文書では、関連する ApplicationService、QueryService、Repository、Aggregate の設計書への Markdown リンクを貼る。
- ユビキタス言語を定義する文書では、日本語名とシステム英語名を対で記載する。英語名は原則 2 語以内とし、例外が必要な場合は理由を残す。
- API 設計の正本は `openapi.yml` とし、Markdown だけで API 詳細を済ませない。
- DB 設計では `00_overview.md` に Mermaid の ER 図を載せ、各 table 詳細では `| 物理名 | 説明 | データ型 | 備考 |` の表形式でカラム一覧を出す。
- 非同期イベントや Webhook があるシステムでは `03_async_contracts` を追加し、契約ごとに payload、認証 / 署名、再送、冪等性、失敗時の扱いを明記する。
- API の項目名や DB カラム名がドメイン内部の用語、または宣言済みのシステム英語名と異なるときは、その対応関係を文書中で説明する。
- Mermaid 図はレビューしやすいように、要素名を日本語またはユビキタス言語で統一する。
- ファイルを更新したときは、関連する他ドキュメントも確認して不整合を残さない。
- 上流ドキュメントを更新したときは、影響を受ける下流ドキュメントを同じターンで確認し、必要な差分を必ず反映する。
- 既存文書の用語と新規文書の用語が衝突する場合は、衝突点を明示してユーザーへ確認する。

## リソース

- [`references/hearing_guide.md`](./references/hearing_guide.md)
  - フェーズ別の質問例、イベントストーミングの促し方、情報提供をお願いするときの観点をまとめたガイド。
- [`references/implementation_design_guide.md`](./references/implementation_design_guide.md)
  - OpenAPI、ER 図、カラム定義表、認可、エラー、冪等性、永続化制約など、実装向け設計を深掘りするときの質問観点をまとめたガイド。
- [`references/consistency_checklist.md`](./references/consistency_checklist.md)
  - ドキュメント横断で整合性を点検するときの確認項目。
- `assets/templates/domain_model/`
  - `00_overview.md` を入口に、`01_system_purpose` `02_actors` `03_usecases` `04_journeys` `05_bounded_contexts` の順で domain_model を分割管理するテンプレート群。
  - `02_actors` は `00_overview.md` の 1 文書に集約し、詳細ファイルへ分割しない。
- `assets/templates/contexts/context_template/`
  - 1 bounded context ディレクトリの中に `00_overview.md` とカテゴリ別ディレクトリを置き、その下で ValueObject から Service までを「一覧 → 短い詳細」、Interface を「一覧」、必要なら Domain Event と External Integration も追加できるテンプレート群。
- `assets/templates/implementation/`
  - `implementation/00_overview.md` を入口に、bounded context ごとの API / DB に加えて、必要なら非同期イベント / Webhook 契約も含む実装向け設計を「一覧 → 詳細」で整理するためのテンプレート群。

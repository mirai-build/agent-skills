---
name: mb-ddd-backend-engineer
description: DDD 設計書を読み取り、現在のリポジトリへ bounded context 単位でバックエンド実装を追加・更新するスキル。最初に `docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation` と既存コードを確認し、設計書の整合と不足情報を整理したうえで、`packages/core` `packages/db` `apps/api` へ責務分離して実装し、検証まで進めたいときに使う。
license: Apache-2.0
---

# ミライビルド DDD バックエンドエンジニア

`skills/mb-ddd-architect` で整備した `domain_model` `contexts` `implementation` を出発点に、現在のリポジトリへバックエンド実装を追加または更新する。
設計書をそのまま写経せず、`domain_model` で用語と bounded context 境界を確認し、`contexts` で domain の責務を確定し、`implementation` で API / DB / 非同期契約の具体形を確認したうえで、repo 既存ルールへ合わせて `core -> db -> api` の順で実装する。

## 実行原則

- いきなり実装を始めない。最初に `docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation`、既存コード、ディレクトリ構成、package manager、scripts を確認する。
- まず対象 bounded context と今回の実装範囲を絞る。複数 context をまたぐときは依存順に小さく分ける。
- 対象 bounded context の `implementation` が未整備なら、API / DB / 非同期契約を推測で埋め切らない。既存コード規約だけでは決め切れない点を質問するか、必要に応じて `skills/mb-ddd-architect` で設計更新を提案する。
- 実装 profile を決めてから動く。現在サポートしているのは TypeScript モノレポ構成だけで、`references/profiles/typescript-monorepo.md` を正本として扱う。
- `packages/core` は framework 非依存で Repository interface を持つ layer、`packages/db` はその interface を実装する Prisma / RDB の具体実装、`apps/api` は NestJS の runtime 入口として分離する。
- 依存方向は必ず `packages/core -> packages/db -> apps/api` を守り、逆向きの import や責務逆流を許さない。特に Repository は先に core 側へ抽象 interface を定義し、その後で db 側に `implements` する具体実装を置く。
- controller と `packages/db` の Prisma repository 実装に業務判断を持ち込まない。業務ルールはまず `packages/core` に置く。
- ディレクトリは `src/` 配下で責務ごとに分け、layer 直下へファイルを平置きせずコンポーネント単位でディレクトリを切る。core 側は `packages/core/src/<bounded-context>/services/SomeApplicationService/SomeApplicationService.ts` を起点に `helpers/` `errors/` `types/` のような用途別サブディレクトリへ分け、db 側は `packages/db/src/repositories/SomePrismaRepository/SomePrismaRepository.ts` を起点に `helpers/` `mappers/` `errors/` のような用途別サブディレクトリへ分ける構成を基本にする。
- 大きなファイルを避け、原則 1 ファイル 1 関数、1 ファイル 1 型、1 ファイル 1 責務で分離する。1 つのファイルへ多数の関数、型、補助処理を詰め込んで可読性と保守性を落とさない。
- Repository や Service の class を巨大化させない。class の各関数は原則として helper の呼び出しと依存先のオーケストレーションに寄せ、複雑な分岐、検証、整形、クエリ組み立て、永続化変換は `helpers/` や `mappers/` へ逃がす。
- 複数コンポーネントで共有するものは、その共有範囲に対応する `shared/` へ分ける。たとえば core 側で service 間で共有するものは `packages/core/src/<bounded-context>/services/shared/`、core 側で layer をまたぐものは `packages/core/src/<bounded-context>/shared/`、repository 間で共有するものは `packages/db/src/repositories/shared/` に置く。
- そのコンポーネントに閉じない汎用的な関数は、コンポーネント本体へ直書きせず対応する `shared/` へ逃がす。単純な日付変換や共通整形のような処理を、個別 Service や Repository に抱え込まない。
- `implementation/openapi.yml` `implementation/NN_<bounded-context>/02_database` `implementation/NN_<bounded-context>/03_async_contracts` がある場合は、それぞれ API、永続化、非同期契約の一次情報として扱う。ただし API は対象 bounded context の tag を起点に読み、`domain_model` や `contexts` の責務と矛盾していれば、そのまま実装せず先に不整合を解消する。
- 設計書で曖昧な点がある場合は、識別子、一貫性境界、状態遷移、永続化形、API 入出力、外部連携を優先して 1〜3 個ずつ質問する。質問観点は `references/implementation_questions.md` を使う。
- 実装順は原則 `core -> db -> api` とし、export と test まで同じターンで揃える。
- 実装中に `domain_model` `contexts` `implementation` の前提ずれが見つかったら、コードだけで吸収せず、どの文書へ差分を返すべきかを整理して報告する。
- 新規追加した関数、クラス、複雑な処理には、保守時に意図が追える短い日本語コメントを付ける。

## 使う場面

- `docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation` をもとに、実際の backend コードを新規実装したい。
- 既存の bounded context に ApplicationService、QueryService、Repository、API 入口を足したい。
- 設計済みの OpenAPI、DB 設計、非同期契約を既存の TypeScript モノレポへ安全に反映したい。
- DDD 設計書と現在の repo 構成を照らし、`packages/core` `packages/db` `apps/api` の責務で迷わず実装したい。
- 将来は複数言語や複数 framework に広げたいが、まずは TypeScript モノレポ構成で運用を始めたい。

## 最初に確認すること

1. `docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation` を読み、対象 bounded context、主要 use case、aggregate、repository、service、interface、API、table、非同期契約を抜き出す。
2. `domain_model` `contexts` `implementation` の間で、用語、責務、入出力、永続化、外部連携に不整合がないかを確認する。
3. 今回が新規実装か既存更新かを整理し、対象ディレクトリ、既存 module、package manager、検証コマンドを確認する。
4. 設計書から読み切れない項目がある場合は、`references/implementation_questions.md` から近い問いを選び、実装に必要な粒度で確認する。
5. 対象 repo が TypeScript モノレポか確認し、該当する場合だけ `references/profiles/typescript-monorepo.md` のルールを適用する。違う構成なら未対応として扱い、追加 profile が必要と伝える。

## 基本フロー

1. 現状把握
- 設計書、既存コード、ディレクトリ構成を確認し、どの bounded context をどこまで実装するかを要約する。
- `domain_model` は用語と境界、`contexts` は domain 責務、`implementation` は API / DB / 非同期契約の一次情報として読み分ける。
- `core` `db` `api` のどこに変更が必要かを実装項目ごとに切り分ける。
- 設計書の不整合や欠落がある場合は、どの論点を質問で埋めるか、どこまでを仮置きで進めるかを先に決める。

2. core 実装
- `packages/core/src/<bounded-context>/` 配下を `services` `queries` `domain` `repositories` `gateways` `shared` に整理し、さらに各 layer の中を責務ごとのディレクトリに分ける。
- `contexts` を正本に、ValueObject、Entity、Aggregate、DomainService、Repository interface、ApplicationService、QueryService をコードへ落とす。
- db や api の実装に着手する前に、core 側で domain model、Service、Repository interface までを先に確定し、後続 layer が参照する抽象の入口をそろえる。
- ApplicationService は `packages/core/src/<bounded-context>/services/SomeApplicationService/SomeApplicationService.ts`、QueryService は `packages/core/src/<bounded-context>/queries/SomeQueryService/SomeQueryService.ts` のようにコンポーネント名とディレクトリ名を揃える。
- Repository interface は `packages/core/src/<bounded-context>/repositories/UserRepository/UserRepository.ts` のように責務ごとのディレクトリへ置き、interface 名は `UserRepository` のように domain の責務が分かる名前にする。
- Service、Repository interface、型、補助関数を 1 ファイルへまとめ書きせず、原則 1 ファイル 1 責務で分離する。関連型や helper も独立した責務を持つなら別ファイルへ切り出し、`packages/core/src/<bounded-context>/services/SomeApplicationService/helpers/validateInput.ts` や `errors/` `types/` のような用途別サブディレクトリへ整理する。
- Service class の各関数は薄いオーケストレーションにとどめ、分岐、入力検証、整形、計算、DTO 組み立てのような処理は helper へ切り出す。class 内に private method を増やしてロジックを抱え込むより、`helpers/` 配下の独立した関数へ逃がすことを優先する。
- 複数 Service や Repository で共有する contract / helper は、共有範囲に応じて `packages/core/src/<bounded-context>/services/shared/` や `packages/core/src/<bounded-context>/repositories/shared/`、layer 横断なら `packages/core/src/<bounded-context>/shared/` へ分ける。
- 個別 Service に閉じない汎用関数は `services/shared/` や `shared/` へ寄せ、単純な日付変換や共通整形を特定コンポーネントへ閉じ込めない。
- `implementation` にある API DTO や DB 名をそのまま domain へ持ち込まず、ユビキタス言語との差分は境界で吸収する。
- `07_domain_events` `08_external_integrations` や `03_async_contracts` がある場合は、core 側では発火点、event contract、gateway interface のどれを持つべきかを切り分ける。
- `index.ts` を更新し、利用側の公開面を揃える。
- unit test は対象 module 近傍の `__tests__` へ colocate する。

3. db 実装
- `implementation/NN_<bounded-context>/02_database` を正本として `packages/db/prisma/schema.prisma` に永続化モデルを反映し、必要なら migration / generate の更新方針を確認する。
- `00_overview.md` の ER 図、各 table 詳細、`contexts` の Aggregate / Repository 設計を突き合わせ、保存単位と transaction 境界が崩れないようにする。
- `packages/db/src/client` に PrismaClient provider があるか確認し、必要に応じて transaction 共有や env 解決を揃える。
- `packages/db/src/repositories/SomePrismaRepository/` のように Repository 実装ごとにディレクトリを分け、必ず `packages/core` で先に定義した Repository interface を `implements` する Prisma 実装を置く。db 側で interface や domain ルールを再定義しない。
- Prisma 実装の class 名は `SomePrismaRepository` のようにライブラリ依存であることが伝わる名前にし、`mappers/` `helpers/` `errors/` `__tests__/` `index.ts` も同じ Repository ディレクトリ配下へ閉じ込める。たとえば helper は `packages/db/src/repositories/SomePrismaRepository/helpers/buildUserWhereInput.ts` のように用途別ディレクトリで分ける。
- Repository 配下でも 1 ファイルに複数の業務関数や型を抱え込まず、mapper、型、変換、保存処理を責務単位で分離する。helper、mapper、error などの補助要素を Repository 直下へ平置きせず、用途ごとのサブディレクトリへ整理する。`SomePrismaRepository.ts` を巨大な万能ファイルにしない。
- Repository class の各関数も helper や mapper を呼ぶ薄い入口にとどめ、where 句の組み立て、record 変換、永続化前後の整形、エラー解釈は helper / mapper へ逃がす。Repository class 自体へ複雑な分岐や長い手続きを抱え込まない。
- 複数 Prisma Repository で共有する変換や補助処理は `packages/db/src/repositories/shared/` に置き、個別 Repository ディレクトリへ重複配置しない。
- Repository は単純なデータ IO と永続化差分の吸収に責務を限定し、業務処理や業務判断は書かない。業務ロジックの責務は Service 側で担保する。
- DB 名やカラム名が domain 用語と異なる場合は、変換責務を repository に閉じ込める。
- repository test は永続化実装の近くに置き、`packages/db/src/repositories/index.ts` と package の公開面を更新する。

4. api 実装
- `apps/api/src/modules/<module-name>/` 配下に NestJS module と `presentation/http` `presentation/webhook` `presentation/batch` `presentation/worker` を必要な分だけ追加する。
- `implementation/openapi.yml` がある場合は、対象 bounded context の tag を起点に API 契約を読み、route、request / response DTO、error response、security を合わせる。
- controller は request / response 境界と service 呼び出しに集中し、業務判断や Prisma 操作を直接書かない。
- module で concrete repository と app/query service を配線し、`apps/api/src/app.module.ts` を更新する。

5. 非同期入口と外部連携の実装
- `implementation/NN_<bounded-context>/03_async_contracts` がある場合は、webhook / worker / batch の入口、署名検証、冪等性、retry 方針、delivery ID 管理などを設計書に合わせて実装する。
- `contexts/07_domain_events` `08_external_integrations` だけがあり concrete 契約が未整備なら、外部 I/O 形状を推測で固定せず質問してから進める。
- outbox や event 保存が必要なら、`core` `db` `api` のどこに責務を置くかを明示して実装する。

6. 検証と仕上げ
- 変更した package / app を中心に build、lint、型検査、test を実行する。repo 既定のコマンドがあればそれを優先する。
- 変更ファイル、実装した use case、仮置き前提、未実装 TODO、実施した検証をまとめて報告する。
- 実装過程で見つけた設計書との差分は、`domain_model` `contexts` `implementation` のどこへ返すべきかまで添えて報告する。

## 設計書から実装へ落とす観点

- `domain_model` では用語、bounded context、上下流関係、共通概念を確定する。
- `contexts` では ValueObject、Entity、Aggregate、Repository、Service、Interface をそのまま `core` の構成へ写像する。
- `implementation/00_overview.md` では、その bounded context で今回どの入口と保存対象を実装するかを確定する。
- `implementation/openapi.yml` は controller / DTO / 認可 / エラー応答の正本として読み、対象 bounded context の operation は tag で絞り込む。
- `implementation/NN_<bounded-context>/02_database` は Prisma schema、relation、unique 制約、監査項目の正本として読む。
- `implementation/NN_<bounded-context>/03_async_contracts` は webhook / event / worker の契約、冪等性、再送、署名検証の正本として読む。
- `06_interfaces` にあるものは、API DTO、外部 gateway、repository contract、認可契約など、どの layer に置くべき interface かを見極める。
- `07_domain_events` `08_external_integrations` がある context では、イベント発火点、非同期処理、外部 API adapter の切り分けを先に決める。
- `implementation` の具体名が `domain_model` や `contexts` の用語とずれる場合は、どこで翻訳するかを明確にし、domain 内部の用語を崩さない。

## 出力ルール

- 実装は既存 repo の命名、package manager、script、lint rule を優先する。
- TypeScript profile ではディレクトリ名と主役の class / interface 名を揃える PascalCase を基本にし、`packages/core/src/<bounded-context>/services/SomeApplicationService/SomeApplicationService.ts` `packages/core/src/<bounded-context>/queries/SomeQueryService/SomeQueryService.ts` `packages/core/src/<bounded-context>/repositories/UserRepository/UserRepository.ts` `packages/db/src/repositories/SomePrismaRepository/SomePrismaRepository.ts` のように配置する。
- 原則 1 ファイル 1 関数、1 ファイル 1 型、1 ファイル 1 責務で分離し、1 つのファイルへ多数の関数、型、補助処理を詰め込まない。
- 依存方向は `packages/core -> packages/db -> apps/api` に固定し、Repository は `packages/core` で定義した抽象 interface を `packages/db` が `implements` する形から外れない。
- `packages/core/src/<bounded-context>/<layer>/<Component>/` 配下でも helper、error、type などの補助要素を `helpers/` `errors/` `types/` のような用途別サブディレクトリへ分け、`packages/core/src/<bounded-context>/services/SomeApplicationService/helpers/validateInput.ts` のように整理する。
- `packages/db/src/repositories/<Repository>/` 配下では helper、mapper、error などの補助要素を `helpers/` `mappers/` `errors/` のような用途別サブディレクトリへ分け、`packages/db/src/repositories/<Repository>/helpers/someHelperFunction.ts` のように整理する。
- Service / Repository の class 関数は原則 helper や mapper の呼び出しへ寄せ、class 自体へ複雑な分岐、検証、整形、クエリ組み立て、永続化変換を抱え込まない。
- layer 内で共有するものは必ずその layer の `shared/` に寄せ、複数コンポーネントから参照される helper や mapper を個別ディレクトリへ重複配置しない。
- そのコンポーネントに閉じない汎用関数はコンポーネント本体ではなく `shared/` へ置き、単純な日付変換や共通整形を各コンポーネントへ重複させない。
- Repository には業務処理を書かず、単純なデータ IO と永続化変換だけを持たせる。業務ロジックは Service 側で担保する。
- 新規ファイルには、存在理由や複雑な判断が分かる短い日本語コメントを必要箇所に入れる。
- 未確定事項を仮置きで進めたときは、コードコメントか最終報告で仮説を明示する。
- `implementation` がないまま API / DB / 非同期入口を大きく追加するときは、どこを既存コード規約から補い、どこが未確定かを明示する。
- 設計書と実装がずれた場合は、ずれた箇所と理由を報告し、必要なら `skills/mb-ddd-architect` で設計書更新を提案する。

## リソース

- `references/profiles/typescript-monorepo.md`
  - 現在サポートしている TypeScript モノレポ構成の実装ルール、ディレクトリ対応、命名、検証方針。
- `references/implementation_questions.md`
  - 設計書から実装へ落とす際に不足しやすい確認事項をまとめた質問ガイド。

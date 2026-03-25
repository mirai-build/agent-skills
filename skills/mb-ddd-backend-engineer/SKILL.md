---
name: mb-ddd-backend-engineer
description: DDD 設計書を読み取り、現在のリポジトリへ bounded context 単位でバックエンド実装を追加・更新するスキル。最初に `docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation` と既存コードを確認し、設計書の整合と不足情報を整理したうえで、`packages/core` `packages/db` `apps/api` へ責務分離して実装し、検証まで進めたいときに使う。
license: Apache-2.0
---

# ミライビルド DDD バックエンドエンジニア

`skills/mb-domain-driven-design` で整備した `domain_model` `contexts` `implementation` を出発点に、現在のリポジトリへバックエンド実装を追加または更新する。
設計書をそのまま写経せず、`domain_model` で用語と bounded context 境界を確認し、`contexts` で domain の責務を確定し、`implementation` で API / DB / 非同期契約の具体形を確認したうえで、repo 既存ルールへ合わせて `core -> db -> api` の順で実装する。

## 実行原則

- いきなり実装を始めない。最初に `docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation`、既存コード、ディレクトリ構成、package manager、scripts を確認する。
- まず対象 bounded context と今回の実装範囲を絞る。複数 context をまたぐときは依存順に小さく分ける。
- 対象 bounded context の `implementation` が未整備なら、API / DB / 非同期契約を推測で埋め切らない。既存コード規約だけでは決め切れない点を質問するか、必要に応じて `skills/mb-domain-driven-design` で設計更新を提案する。
- 実装 profile を決めてから動く。現在サポートしているのは TypeScript モノレポ構成だけで、`references/profiles/typescript-monorepo.md` を正本として扱う。
- `packages/core` は framework 非依存、`packages/db` は Prisma / RDB の具体実装、`apps/api` は NestJS の runtime 入口として分離する。
- controller と Prisma repository に業務判断を持ち込まない。業務ルールはまず `packages/core` に置く。
- `implementation/01_api/openapi.yml` `implementation/02_database` `implementation/03_async_contracts` がある場合は、それぞれ API、永続化、非同期契約の一次情報として扱う。ただし `domain_model` や `contexts` の責務と矛盾していれば、そのまま実装せず先に不整合を解消する。
- 設計書で曖昧な点がある場合は、識別子、一貫性境界、状態遷移、永続化形、API 入出力、外部連携を優先して 1〜3 個ずつ質問する。質問観点は `references/implementation_questions.md` を使う。
- 実装順は原則 `core -> db -> api` とし、export と test まで同じターンで揃える。
- 実装中に `domain_model` `contexts` `implementation` の前提ずれが見つかったら、コードだけで吸収せず、どの文書へ差分を返すべきかを整理して報告する。
- 新規追加した関数、クラス、複雑な処理には、保守時に意図が追える短いコメントを付ける。

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
- `packages/core/src/<bounded-context>/` 配下に `application` `query` `domain` `repositories` `gateways` を必要なものだけ追加する。
- `contexts` を正本に、ValueObject、Entity、Aggregate、DomainService、Repository interface、ApplicationService、QueryService をコードへ落とす。
- `implementation` にある API DTO や DB 名をそのまま domain へ持ち込まず、ユビキタス言語との差分は境界で吸収する。
- `07_domain_events` `08_external_integrations` や `03_async_contracts` がある場合は、core 側では発火点、event contract、gateway interface のどれを持つべきかを切り分ける。
- `index.ts` を更新し、利用側の公開面を揃える。
- unit test は対象 module 近傍の `__tests__` へ colocate する。

3. db 実装
- `implementation/02_database` を正本として `packages/db/prisma/schema.prisma` に永続化モデルを反映し、必要なら migration / generate の更新方針を確認する。
- `00_overview.md` の ER 図、各 table 詳細、`contexts` の Aggregate / Repository 設計を突き合わせ、保存単位と transaction 境界が崩れないようにする。
- `packages/db/src/client` に PrismaClient provider があるか確認し、必要に応じて transaction 共有や env 解決を揃える。
- `packages/db/src/persistence/<context-or-aggregate>/` に Prisma repository を実装し、`packages/core` の Repository interface を満たす。
- DB 名やカラム名が domain 用語と異なる場合は、変換責務を repository に閉じ込める。
- repository test は永続化実装の近くに置き、`src/index.ts` `src/persistence/index.ts` の公開面も更新する。

4. api 実装
- `apps/api/src/modules/<module-name>/` 配下に NestJS module と `presentation/http` `presentation/webhook` `presentation/batch` `presentation/worker` を必要な分だけ追加する。
- `implementation/01_api/openapi.yml` がある場合は、それを API 契約の正本として route、request / response DTO、error response、security を合わせる。
- controller は request / response 境界と service 呼び出しに集中し、業務判断や Prisma 操作を直接書かない。
- module で concrete repository と app/query service を配線し、`apps/api/src/app.module.ts` を更新する。

5. 非同期入口と外部連携の実装
- `implementation/03_async_contracts` がある場合は、webhook / worker / batch の入口、署名検証、冪等性、retry 方針、delivery ID 管理などを設計書に合わせて実装する。
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
- `implementation/01_api/openapi.yml` は controller / DTO / 認可 / エラー応答の正本として読む。
- `implementation/02_database` は Prisma schema、relation、unique 制約、監査項目の正本として読む。
- `implementation/03_async_contracts` は webhook / event / worker の契約、冪等性、再送、署名検証の正本として読む。
- `06_interfaces` にあるものは、API DTO、外部 gateway、repository contract、認可契約など、どの layer に置くべき interface かを見極める。
- `07_domain_events` `08_external_integrations` がある context では、イベント発火点、非同期処理、外部 API adapter の切り分けを先に決める。
- `implementation` の具体名が `domain_model` や `contexts` の用語とずれる場合は、どこで翻訳するかを明確にし、domain 内部の用語を崩さない。

## 出力ルール

- 実装は既存 repo の命名、package manager、script、lint rule を優先する。
- TypeScript profile では `*.app-service.ts` `*.query-service.ts` `*.repository.ts` `*.gateway.ts` `*.aggregate.ts` `*.entity.ts` `*.vo.ts` `*.service.ts` を基本 naming とする。
- 新規ファイルには、存在理由や複雑な判断が分かる短いコメントを必要箇所に入れる。
- 未確定事項を仮置きで進めたときは、コードコメントか最終報告で仮説を明示する。
- `implementation` がないまま API / DB / 非同期入口を大きく追加するときは、どこを既存コード規約から補い、どこが未確定かを明示する。
- 設計書と実装がずれた場合は、ずれた箇所と理由を報告し、必要なら `skills/mb-domain-driven-design` で設計書更新を提案する。

## リソース

- `references/profiles/typescript-monorepo.md`
  - 現在サポートしている TypeScript モノレポ構成の実装ルール、ディレクトリ対応、命名、検証方針。
- `references/implementation_questions.md`
  - 設計書から実装へ落とす際に不足しやすい確認事項をまとめた質問ガイド。

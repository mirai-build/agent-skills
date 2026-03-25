---
name: mb-ddd-backend-engineer
description: DDD 設計書を読み取り、現在のリポジトリへ bounded context 単位でバックエンド実装を追加・更新するスキル。最初に `docs/designs/domain_model` `docs/designs/contexts` と既存コードを確認し、不足情報を質問したうえで、`packages/core` `packages/db` `apps/api` へ責務分離して実装し、検証まで進めたいときに使う。
license: Apache-2.0
---

# ミライビルド DDD バックエンドエンジニア

`skills/mb-domain-driven-design` で整備した設計書を出発点に、現在のリポジトリへバックエンド実装を追加または更新する。
設計書をそのまま写経せず、bounded context、aggregate、repository、service、API 入口の責務へ分解し、repo 既存ルールへ合わせて `core -> db -> api` の順で実装する。

## 実行原則

- いきなり実装を始めない。最初に `docs/designs/domain_model` `docs/designs/contexts`、既存コード、ディレクトリ構成、package manager、scripts を確認する。
- まず対象 bounded context と今回の実装範囲を絞る。複数 context をまたぐときは依存順に小さく分ける。
- 実装 profile を決めてから動く。現在サポートしているのは TypeScript モノレポ構成だけで、`references/profiles/typescript-monorepo.md` を正本として扱う。
- `packages/core` は framework 非依存、`packages/db` は Prisma / RDB の具体実装、`apps/api` は NestJS の runtime 入口として分離する。
- controller と Prisma repository に業務判断を持ち込まない。業務ルールはまず `packages/core` に置く。
- 設計書で曖昧な点がある場合は、識別子、一貫性境界、状態遷移、永続化形、API 入出力、外部連携を優先して 1〜3 個ずつ質問する。質問観点は `references/implementation_questions.md` を使う。
- 実装順は原則 `core -> db -> api` とし、export と test まで同じターンで揃える。
- 新規追加した関数、クラス、複雑な処理には、保守時に意図が追える短いコメントを付ける。

## 使う場面

- `docs/designs/domain_model` `docs/designs/contexts` をもとに、実際の backend コードを新規実装したい。
- 既存の bounded context に ApplicationService、QueryService、Repository、API 入口を足したい。
- DDD 設計書と現在の repo 構成を照らし、`packages/core` `packages/db` `apps/api` の責務で迷わず実装したい。
- 将来は複数言語や複数 framework に広げたいが、まずは TypeScript モノレポ構成で運用を始めたい。

## 最初に確認すること

1. `docs/designs/domain_model` と `docs/designs/contexts` を読み、対象 bounded context、主要 use case、aggregate、repository、service、interface を抜き出す。
2. 今回が新規実装か既存更新かを整理し、対象ディレクトリ、既存 module、package manager、検証コマンドを確認する。
3. 設計書から読み切れない項目がある場合は、`references/implementation_questions.md` から近い問いを選び、実装に必要な粒度で確認する。
4. 対象 repo が TypeScript モノレポか確認し、該当する場合だけ `references/profiles/typescript-monorepo.md` のルールを適用する。違う構成なら未対応として扱い、追加 profile が必要と伝える。

## 基本フロー

1. 現状把握
- 設計書、既存コード、ディレクトリ構成を確認し、どの bounded context をどこまで実装するかを要約する。
- `core` `db` `api` のどこに変更が必要かを実装項目ごとに切り分ける。

2. core 実装
- `packages/core/src/<bounded-context>/` 配下に `application` `query` `domain` `repositories` `gateways` を必要なものだけ追加する。
- 設計書の ValueObject、Entity、Aggregate、DomainService、Repository interface、ApplicationService、QueryService をコードへ落とす。
- `index.ts` を更新し、利用側の公開面を揃える。
- unit test は対象 module 近傍の `__tests__` へ colocate する。

3. db 実装
- `packages/db/prisma/schema.prisma` に永続化モデルを反映し、必要なら migration / generate の更新方針を確認する。
- `packages/db/src/client` に PrismaClient provider があるか確認し、必要に応じて transaction 共有や env 解決を揃える。
- `packages/db/src/persistence/<context-or-aggregate>/` に Prisma repository を実装し、`packages/core` の Repository interface を満たす。
- repository test は永続化実装の近くに置き、`src/index.ts` `src/persistence/index.ts` の公開面も更新する。

4. api 実装
- `apps/api/src/modules/<module-name>/` 配下に NestJS module と `presentation/http` `presentation/webhook` `presentation/batch` `presentation/worker` を必要な分だけ追加する。
- controller は request / response 境界と service 呼び出しに集中し、業務判断や Prisma 操作を直接書かない。
- module で concrete repository と app/query service を配線し、`apps/api/src/app.module.ts` を更新する。

5. 検証と仕上げ
- 変更した package / app を中心に build、lint、型検査、test を実行する。repo 既定のコマンドがあればそれを優先する。
- 変更ファイル、実装した use case、仮置き前提、未実装 TODO、実施した検証をまとめて報告する。

## 設計書から実装へ落とす観点

- `domain_model` では用語、bounded context、上下流関係、共通概念を確定する。
- `contexts` では ValueObject、Entity、Aggregate、Repository、Service、Interface をそのまま `core` の構成へ写像する。
- `06_interfaces` にあるものは、API DTO、外部 gateway、repository contract、認可契約など、どの layer に置くべき interface かを見極める。
- `07_domain_events` `08_external_integrations` がある context では、イベント発火点、非同期処理、外部 API adapter の切り分けを先に決める。

## 出力ルール

- 実装は既存 repo の命名、package manager、script、lint rule を優先する。
- TypeScript profile では `*.app-service.ts` `*.query-service.ts` `*.repository.ts` `*.gateway.ts` `*.aggregate.ts` `*.entity.ts` `*.vo.ts` `*.service.ts` を基本 naming とする。
- 新規ファイルには、存在理由や複雑な判断が分かる短いコメントを必要箇所に入れる。
- 未確定事項を仮置きで進めたときは、コードコメントか最終報告で仮説を明示する。
- 設計書と実装がずれた場合は、ずれた箇所と理由を報告し、必要なら `skills/mb-domain-driven-design` で設計書更新を提案する。

## リソース

- `references/profiles/typescript-monorepo.md`
  - 現在サポートしている TypeScript モノレポ構成の実装ルール、ディレクトリ対応、命名、検証方針。
- `references/implementation_questions.md`
  - 設計書から実装へ落とす際に不足しやすい確認事項をまとめた質問ガイド。

---
name: mb-ddd-backend-engineer
description: DDD 設計書を読み取り、現在のリポジトリへ bounded context 単位でバックエンド実装を追加・更新するスキル。最初に `docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation` と既存コードを確認し、設計書の整合と不足情報を整理したうえで、`packages/core` `packages/db` `apps/api` へ責務分離して実装し、検証まで進めたいときに使う。
license: Apache-2.0
---

# ミライビルド DDD バックエンドエンジニア

`skills/mb-ddd-architect` で整備した `domain_model` `contexts` `implementation` を出発点に、現在のリポジトリへバックエンド実装を追加または更新する。
このファイルは、発火条件、実行原則、読む順、判断の入口だけを扱う。layer ごとの詳細規約や設計書からコードへの詳細な写像は `references/` の正本を読む。

## 概要

設計書をそのまま写経せず、`domain_model` で用語と bounded context 境界を確認し、`contexts` で domain の責務を確定し、`implementation` で API / DB / 非同期契約の具体形を確認したうえで、既存 repo の規約へ合わせて実装する。

`SKILL.md` には詳細な layer 別規約を再掲しない。実装標準、layer 別の詳細手順、設計書からコードへの写像は、それぞれ `references/` に分離して管理する。

## 実行原則

- いきなり実装を始めない。最初に `docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation`、既存コード、ディレクトリ構成、package manager、scripts を確認する。
- まず対象 bounded context と今回の実装範囲を絞る。複数 context をまたぐときは依存順に小さく分ける。
- 対象 bounded context の `implementation` が未整備なら、API / DB / 非同期契約を推測で埋め切らない。既存コード規約だけでは決め切れない点を質問するか、必要に応じて `skills/mb-ddd-architect` で設計更新を提案する。
- 実装 profile を決めてから動く。現在サポートしているのは TypeScript モノレポ構成だけで、フレームワーク非依存の標準は [`references/profiles/typescript/monorepo.md`](./references/profiles/typescript/monorepo.md)、NestJS 固有の標準は [`references/profiles/typescript/nest.md`](./references/profiles/typescript/nest.md) を正本として扱う。
- TypeScript で実装するときは、まず既存の domain 型、Repository interface、shared contract、generated type、DTO を棚卸しし、型定義は必要最小限にとどめる。同じ意味の型を layer ごとに作り直さず、新しい型は境界を守るために別表現が必要なときか、複数箇所で同じ意味を共有するときだけ追加する。
- TypeScript のファイル名では snake-case を使わず、CamelCase 系で統一する。クラスや model、DTO など主語を表すファイルは `HogeHoge.ts` `HogeHoge.test.ts` `FugaFuga.models.ts` のように PascalCase、関数中心のファイルは `someFunction.ts` のように lowerCamelCase を使う。
- 実装順序とコード依存を混同しない。実装順序は `packages/core -> packages/db -> apps/api` とし、コード依存は `packages/db -> packages/core` と `apps/api -> packages/core` を基本に守る。`apps/api` から `packages/db` への参照は composition root や module 配線に限定する。
- controller と repository 実装に業務判断を持ち込まない。業務ルールはまず `packages/core` に置く。
- API を含む use case を実装するときは、対象の backend component 一式を実装し切ってから、DB まで接続する API 結合テストまで扱う。NestJS の API テストは Playwright などのブラウザ E2E ではなく、`@nestjs/testing` と `supertest` を使う結合テストとして扱い、詳細は [`references/api_integration_testing.md`](./references/api_integration_testing.md) を正本にする。
- 設計書で曖昧な点がある場合は、識別子、一貫性境界、状態遷移、永続化形、API 入出力、外部連携を優先して 1〜3 個ずつ確認する。質問観点は [`references/implementation_questions.md`](./references/implementation_questions.md) を使う。
- 実装中に `domain_model` `contexts` `implementation` の前提ずれが見つかったら、コードだけで吸収せず、どの文書へ差分を返すべきかを整理して報告する。
- 新規追加した関数、クラス、複雑な処理には、保守時に意図が追える短い日本語コメントを付ける。
- `SomeApplicationService` `SomeQueryService` `UserRepository` `SomePrismaRepository` のような代表コンポーネントの主役ファイルには、実装時に参照した設計書パスを短い日本語コメントで残す。
- `normalizeRequiredSlug` のような再利用候補の validation / normalize helper を `SomeApplicationService.ts` や aggregate 実装へベタ書きしない。bounded context 全体で使う helper は `packages/core/src/<bounded-context>/shared`、domain や layer の文脈を持たない純粋 utility は `packages/utils` へ寄せる。

## 使う場面

- `docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation` をもとに、実際の backend コードを新規実装したい。
- 既存の bounded context に ApplicationService、QueryService、Repository、API 入口を足したい。
- 設計済みの OpenAPI、DB 設計、非同期契約を既存の TypeScript モノレポへ安全に反映したい。
- API route まで実装したあと、DB 接続付きの API 結合テストも同じ流れでそろえたい。
- DDD 設計書と現在の repo 構成を照らし、`packages/core` `packages/db` `apps/api` の責務で迷わず実装したい。
- 将来は複数言語や複数 framework に広げたいが、まずは TypeScript モノレポ構成で運用を始めたい。

## 最初の進め方

1. `docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation` と既存コードを確認し、対象 bounded context、主要 use case、実装対象の入口を整理する。
2. [`references/design_to_code_mapping.md`](./references/design_to_code_mapping.md) を読み、設計書のどこを正本にするか、どの情報をどの layer へ写像するかを決める。
3. [`references/implementation_flow.md`](./references/implementation_flow.md) を読み、初動棚卸しから `core -> db -> api -> async -> verify` の進め方と完了条件をそろえる。
4. 対象 repo が TypeScript モノレポなら [`references/profiles/typescript/monorepo.md`](./references/profiles/typescript/monorepo.md) を読み、`apps/api` が NestJS なら [`references/profiles/typescript/nest.md`](./references/profiles/typescript/nest.md) も読む。API を実装対象に含むなら [`references/api_integration_testing.md`](./references/api_integration_testing.md) も読み、結合テストの着手条件と置き場を先にそろえる。該当しない構成なら未対応として扱い、追加 profile が必要と伝える。
5. 設計書から読み切れない項目が残る場合は [`references/implementation_questions.md`](./references/implementation_questions.md) を使って確認事項を整理してから実装する。

## 参照ルール

- 設計書からコードへの写像、用語の翻訳境界、`06_interfaces` `07_domain_events` `08_external_integrations` の扱いは [`references/design_to_code_mapping.md`](./references/design_to_code_mapping.md) を正本にする。
- 初動棚卸し、実装範囲の絞り方、profile 適用判定、`core -> db -> api -> async -> verify` の進行順、完了条件は [`references/implementation_flow.md`](./references/implementation_flow.md) を正本にする。
- TypeScript モノレポの責務分離、命名、ディレクトリ対応、検証方針は [`references/profiles/typescript/monorepo.md`](./references/profiles/typescript/monorepo.md) を正本にする。
- NestJS 固有の tree、Controller / DTO / Validation、Mapper / Presenter / Builder、アンチパターンは [`references/profiles/typescript/nest.md`](./references/profiles/typescript/nest.md) を正本にする。
- API の結合テストの着手条件、置き場、実装観点、完了条件は [`references/api_integration_testing.md`](./references/api_integration_testing.md) を正本にする。
- 実装前の質問観点は [`references/implementation_questions.md`](./references/implementation_questions.md) を使う。
- 迷ったときは `design_to_code_mapping -> implementation_flow -> profile -> implementation_questions` の順で読む。
- `SKILL.md` へ profile 詳細や layer 別実装規約を再掲しない。重複が出そうなら `references/` 側を更新して一か所へ寄せる。

## リソース

- [`references/design_to_code_mapping.md`](./references/design_to_code_mapping.md)
  - `domain_model` `contexts` `implementation` の読み分け、用語の翻訳境界、layer ごとの置き場判定をまとめた写像ガイド。
- [`references/implementation_flow.md`](./references/implementation_flow.md)
  - 初動棚卸しから実装完了までの進め方と、同じターンでそろえるべき export / test / 最終報告の基準をまとめたフローガイド。
- [`references/profiles/typescript/monorepo.md`](./references/profiles/typescript/monorepo.md)
  - フレームワーク非依存の TypeScript モノレポ実装ルール、ディレクトリ対応、命名、検証方針。
- [`references/profiles/typescript/nest.md`](./references/profiles/typescript/nest.md)
  - NestJS 固有の tree、Controller / DTO / Validation、Mapper / Presenter / Builder、アンチパターン。
- [`references/api_integration_testing.md`](./references/api_integration_testing.md)
  - API の DB 接続付き結合テストを、どの条件で着手し、どこへ置き、何を確認するかをまとめたガイド。
- [`references/implementation_questions.md`](./references/implementation_questions.md)
  - 設計書から実装へ落とす際に不足しやすい確認事項をまとめた質問ガイド。

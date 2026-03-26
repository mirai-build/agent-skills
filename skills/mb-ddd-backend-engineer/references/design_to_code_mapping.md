# 設計書からコードへの写像ガイド

`docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation` を、どの順で読み、どの layer へ写像するかをそろえるためのガイド。
この文書は「どの情報をどこへ置くか」の判断を扱い、具体的なディレクトリ構成や命名規約は profile 文書へ委ねる。

## 読む順

1. `domain_model`
- 用語、bounded context、上下流関係、共通概念の正本として読む。
- まず「どの bounded context が今回の主語か」をここで確定する。

2. `contexts`
- ValueObject、Entity、Aggregate、Repository、Service、Interface の責務を読む。
- `packages/core` に置く抽象の正本として扱う。

3. `implementation`
- API、永続化、非同期契約など concrete な実装前提を読む。
- `contexts` と矛盾する場合は、どちらかを黙って採用せず不整合として扱う。

## 読み分けの原則

- `domain_model` は内部のユビキタス言語を決める文書として扱い、API 名や DB 名で上書きしない。
- `contexts` は業務責務の正本として扱い、Service、Repository、Aggregate の責務がここで追えないまま実装を始めない。
- `implementation` は concrete な契約の正本として扱うが、責務や境界を決める文書ではない。
- 設計書同士で用語、責務、入出力、永続化、一貫性境界に矛盾がある場合は、先に差分を整理してから実装する。

## layer への写像

### `domain_model`

- bounded context、共通概念、上下流関係は、実装対象と依存順を決める材料として使う。
- API / DB の具体名が別にあっても、`packages/core` では `domain_model` と `contexts` の用語を優先する。

### `contexts`

- ValueObject、Entity、Aggregate、DomainService、ApplicationService、QueryService、Repository interface、Gateway interface は `packages/core` の正本にする。
- HTTP request / response DTO、ORM の型、Webhook payload など transport や persistence に寄った表現は `packages/core` へ持ち込まない。
- `contexts` の用語と `implementation` の具体名がずれる場合は、境界で翻訳する。

### `implementation/openapi.yml`

- route、request / response schema、error response、security、tag は `apps/api` の正本として扱う。
- HTTP request / response DTO、controller、validation、Presenter / Builder など transport 境界の表現は `apps/api` に置く。
- `openapi.yml` の項目名をそのまま domain 用語へ流し込まず、必要な翻訳は API 境界で閉じ込める。

### `implementation/NN_<bounded-context>/02_database`

- Prisma schema、relation、unique 制約、監査項目、永続化都合の naming は `packages/db` の正本として扱う。
- Repository 実装、record 変換、transaction 境界、永続化前後の整形は `packages/db` に閉じ込める。
- DB 名やカラム名が domain 用語と異なる場合は、Repository と mapper で吸収する。

### `implementation/NN_<bounded-context>/03_async_contracts`

- Webhook / batch / worker の入口、payload、署名検証、冪等性、retry、delivery ID 管理は concrete 契約の正本として扱う。
- 入口の実装は `apps/api` 側の runtime 境界で扱い、domain event や外部 gateway の抽象が必要なら `packages/core` に置く。
- outbox や event 保存など永続化が絡む部分は `packages/db` 側の責務として切り分ける。

## `06_interfaces` の置き場判定

- Repository contract は `packages/core` の `repositories/` に置く。
- 外部 API や message broker の抽象 contract は `packages/core` の `gateways/` に置く。
- HTTP request / response DTO は `apps/api` に置く。
- 認証済み actor や request metadata の受け渡しなど transport 境界の契約は `apps/api` に置く。
- 業務上の権限制約や role 判定のルールは `packages/core` 側の業務ロジックとして扱う。

## `07_domain_events` と `08_external_integrations` の扱い

- `07_domain_events` がある場合は、どの操作が発火点か、同期 transaction で守る範囲か、event で切り出す範囲かを先に決める。
- `08_external_integrations` がある場合は、`packages/core` には抽象 interface までを置き、concrete adapter は outer layer に分離する。
- concrete な外部 I/O 契約が `implementation` にない場合は、payload や retry 方針を推測で固定せず確認してから進める。

## 用語ずれを解消する場所

- domain 内部の用語は `domain_model` と `contexts` に合わせる。
- API 名とのずれは `apps/api` の DTO / Mapper / Presenter / Builder で吸収する。
- DB 名とのずれは `packages/db` の Repository / mapper で吸収する。
- 外部システム名とのずれは outer adapter 側で吸収し、`packages/core` へ外部都合を漏らさない。

## 設計差分の返却先

- 用語、bounded context 境界、上下流関係、共通概念のずれは `domain_model` へ返す。
- Aggregate、Repository、Service、Interface の責務ずれは `contexts` へ返す。
- route、DTO、error response、security、DB schema、async contract のずれは `implementation` へ返す。
- どの文書にも根拠がない実装判断を置いた場合は、最終報告で仮置き前提として明示する。

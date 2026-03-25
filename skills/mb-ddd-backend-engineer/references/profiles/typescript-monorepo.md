# TypeScript モノレポ実装プロファイル

## このプロファイルについて

このプロファイルは、DDD 設計書を TypeScript モノレポのバックエンド実装へ落とすときの正本である。
初版の対象 stack は次のとおり。

- `packages/core`: TypeScript スクラッチ。framework 非依存の業務ロジック。
- `packages/db`: Prisma を使う RDB persistence。
- `apps/api`: NestJS による API runtime。

ディレクトリ方針と責務分離は、`~/workspace/makia` の `packages/core` `packages/db` `apps/api` 構成を参考にしている。
別言語や別 framework を追加するときは、この `references/profiles/` 配下へ新しい profile を追加し、先にどの profile を使うか決めてから実装する。

## 適用条件

- 対象 repo が `apps/` と `packages/` を持つ TypeScript モノレポである。
- `docs/designs/domain_model` `docs/designs/contexts` が存在し、API / DB / 非同期入口まで実装する場合は `docs/designs/implementation` も参照できる。
- `core -> db -> api` の責務分離でバックエンドを実装したい。

これに当てはまらない場合は、この profile を無理に流用せず、未対応として追加 profile の必要性を報告する。

## 実装前に決めること

1. 今回の完了点
- どの use case を実装完了とみなすか。
- write だけか、read も必要か。
- 同期 API だけか、webhook / batch / worker も含むか。

2. 対象 bounded context
- どの context を主語にするか。
- 複数 context をまたぐなら、どちらが完了責務を持つか。

3. 既存 repo ルール
- package manager、workspace 設定、build / lint / test script。
- 既存 module 名、export 方針、test の colocate ルール。

4. 未確定事項
- 識別子の払い出し元。
- 一貫性境界と transaction の範囲。
- API の認可、エラー応答、外部連携。

## 設計書の読み分け

- `domain_model` は用語、bounded context 境界、上下流関係の正本として使う。
- `contexts` は ValueObject、Entity、Aggregate、Repository、Service、Interface の正本として使う。
- `implementation/00_overview.md` は今回その context でどの入口と保存対象を実装するかの正本として使う。
- `implementation/openapi.yml` は HTTP API 契約の正本として使い、対象 bounded context の operation は tag で読み分ける。
- `implementation/NN_<bounded-context>/02_database` は Prisma schema と永続化制約の正本として使う。
- `implementation/NN_<bounded-context>/03_async_contracts` は webhook / event / worker 契約の正本として使う。
- 具体契約が上位の責務定義と矛盾する場合は、どれか一方を黙って採用せず、不整合として解消してから実装する。

## ディレクトリ対応

```text
packages/core/
  src/
    shared/
    <bounded-context>/
      application/
      query/
      domain/
      repositories/
      gateways/

packages/db/
  prisma/
    schema.prisma
    migrations/
  src/
    client/
    persistence/
      <context-or-aggregate>/
    test-support/

apps/api/
  src/
    bootstrap/
    modules/
      <module-name>/
        <module-name>.module.ts
        presentation/
          http/
          webhook/
          batch/
          worker/
    shared/
```

### `packages/core`

- `packages/core/src` の top-level は bounded context 単位にする。
- `application` は write side の完了点を担う。
- `query` は read side の DTO 組み立てを担う。
- `domain` は Entity、ValueObject、Aggregate、Policy、DomainService の正本にする。
- `repositories` と `gateways` には interface だけを置く。
- 複数 context で同じ意味を持つ error や契約だけを `shared` に置く。

### `packages/db`

- `prisma/schema.prisma` は永続化モデルの正本にする。
- `src/client` には PrismaClient provider や transaction 制御を置く。
- `src/persistence/<context-or-aggregate>` に Prisma repository を置く。
- DB 固有の test-support は `src/test-support` に置く。

### `apps/api`

- `src/modules/<module-name>/` に NestJS module と runtime 入口をまとめる。
- `presentation/http` `presentation/webhook` `presentation/batch` `presentation/worker` は必要な分だけ作る。
- `apps/api` は composition root として扱い、業務ロジック本体は持ち込まない。

## 設計書からコードへの写像

| 設計書の要素 | `packages/core` | `packages/db` | `apps/api` |
| --- | --- | --- | --- |
| bounded context | `src/<bounded-context>/` ディレクトリ | `src/persistence/<context-or-aggregate>/` の単位を決める材料 | `src/modules/<module-name>/` の単位を決める材料 |
| ValueObject | `domain/*.vo.ts` | Prisma scalar / JSON / relation との対応を決める | DTO 変換時の値の受け渡し |
| Entity | `domain/*.entity.ts` | row / relation との相互変換 | 基本的に直接持たない |
| Aggregate | `domain/*.aggregate.ts` | 保存単位、transaction 範囲、複数 table 更新の境界 | write use case の完了点 |
| Repository | `repositories/*.repository.ts` | `persistence/**/prisma-*.repository.ts` | module で concrete 実装を配線 |
| DomainService | `domain/*.service.ts` | 必要なら repository 側で補助変換 | 呼び出さない。ApplicationService 経由で使う |
| ApplicationService | `application/*.app-service.ts` | transaction runner や repository 実装を渡す | controller / worker から呼ぶ |
| QueryService | `query/*.query-service.ts` | read に必要な repository 実装を渡す | controller から呼ぶ |
| Interface 一覧 | repository / gateway / shared contract / DTO のどれかを見極める | concrete 実装が必要なものだけ作る | request / response DTO、Nest 配線 |
| Domain Event | event contract や発火点を置く | outbox や event 保存が必要ならここで扱う | webhook / worker の入口設計へ反映 |
| External Integration | gateway interface を置く | DB だけで完結しない場合は原則ここに持ち込まない | 外部イベント受信口の配線を置く |
| `implementation/openapi.yml` | domain に transport 都合を漏らさないための境界確認に使う。対象 bounded context は tag で絞る | 原則触れない | controller、DTO、認可、error response の正本 |
| `implementation/NN_<bounded-context>/02_database` | Aggregate と Repository の保存責務確認に使う | Prisma model、relation、制約の正本 | 原則触れない |
| `implementation/NN_<bounded-context>/03_async_contracts` | event 発火点、gateway interface の切り分けに使う | outbox、delivery 記録、冪等性保存の要否を決める | webhook / worker / batch 入口の正本 |

`08_external_integrations` に concrete adapter が必要な場合は、repo に既存の `packages/integration` 相当があるか確認する。
ない場合は placement を決め打ちせず、まずユーザーへ確認する。

## 実装順序

1. `packages/core`
- context ディレクトリを作り、domain、repository interface、application/query service を先に置く。
- 命名は `*.aggregate.ts` `*.entity.ts` `*.vo.ts` `*.service.ts` `*.repository.ts` `*.app-service.ts` `*.query-service.ts` を使う。
- context 内 `index.ts` と `packages/core/src/index.ts` の公開面を更新する。
- unit test は対象ディレクトリ近傍の `__tests__` に置き、fake repository で業務ルールを確認する。

2. `packages/db`
- schema を更新し、必要な relation、unique 制約、soft delete、timestamp を反映する。
- `PrismaClientProvider` 相当があるか確認し、なければ transaction 共有と env 解決の責務を明確にして実装する。
- Prisma repository では複数 table 更新や JSON 再構成を隠蔽し、利用側に永続化詳細を漏らさない。
- `src/persistence/index.ts` と `src/index.ts` の export を揃える。

3. `apps/api`
- module は context ごとに薄く作り、controller は request / response 境界に集中させる。
- Prisma repository と app/query service の配線は module で完結させる。
- `apps/api/src/app.module.ts` に module を登録する。
- controller に業務ロジック、Prisma 操作、複雑な DTO 再構成を書かない。

4. 非同期入口と外部連携
- `implementation/NN_<bounded-context>/03_async_contracts` がある場合は、契約単位で webhook / worker / batch の入口を作る。
- 署名検証、delivery ID、retry、冪等性は入口か persistence のどちらに責務を置くかを先に決める。
- concrete adapter の置き場が既存 repo にない場合は、placement を決め打ちせず確認する。

## `packages/core` 実装ルール

- framework 依存の import を持ち込まない。
- top-level を `application` `query` `repositories` の責務別へ戻さず、必ず context-first 構成にする。
- `shared` は「複数 context から同じ意味で使う契約」だけに絞る。
- Service は constructor で repository / gateway interface を受け取る。
- 先行 stub を置く場合も、なぜそのファイルが存在するかが分かる短いコメントを付ける。

## `packages/db` 実装ルール

- Prisma model は API DTO ではなく、永続化都合に基づいて設計する。
- repository は Prisma record と aggregate の相互変換責務を持つ。
- transaction をまたぐ複数保存は、ApplicationService の完了点と揃えて扱う。
- repository error や data integrity error が既存 repo にあるなら、その規約を優先して合わせる。
- repository test は DB 実装近傍へ置き、永続化挙動を確認する。

## `apps/api` 実装ルール

- module 名は bounded context または runtime の責務名に合わせる。
- `presentation/http` 配下に controller と必要な DTO を置く。
- webhook / batch / worker が不要なら空ディレクトリを作らない。
- Nest token や interface は複数実装切り替えが本当に必要なときだけ導入する。
- API 側の test は入口と配線の確認に絞り、業務ロジックの主戦場は `packages/core` `packages/db` に置く。
- `openapi.yml` や async contract に書かれた transport 名を domain 内部へ漏らさない。

## 検証

- 変更した package / app の build、lint、型検査、test を順に実行する。
- repo に `verify` `check` `ci` のような包括 script があるなら、それを優先する。
- Prisma schema を触ったら、repo 既定の migration / generate 手順まで確認する。
- すべて実行できない場合は、環境不足と未確認範囲を最終報告へ残す。

## 実装後に報告すること

- どの bounded context の何を実装したか。
- `core` `db` `api` で追加または更新した主な責務。
- 設計書どおりに実装した点と、既存コード都合で調整した点。
- 仮置き前提、未実装 TODO、未確認の検証。

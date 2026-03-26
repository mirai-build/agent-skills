# TypeScript NestJS 実装プロファイル

## このプロファイルについて

このプロファイルは `apps/api` / `api` に閉じる NestJS 固有の実装ルールをまとめた正本である。
フレームワーク非依存の monorepo 標準は `references/profiles/typescript/monorepo.md` を先に読み、このファイルでは NestJS に依存する tree、責務、Controller / DTO / Mapper / Presenter / Builder のルールだけを扱う。

この profile では monorepo path を `apps/api` と表記するが、repo に `api/` がある場合も同じ責務分担として読み替えてよい。
response DTO の生成責務は `Pipe` と呼ばず、`Mapper` `Presenter` `Builder` で表現する。
`ValidationPipe` は request DTO の入力検証に使う NestJS 組み込み機能として扱い、response 生成とは混同しない。

## 責務分担

| 置き場 | 持つもの |
| --- | --- |
| `api` / `apps/api` | controller、request / response DTO、`ValidationPipe` を使う入力検証、guard / interceptor / exception filter、Nest module、custom provider による DI 配線、HTTP / webhook / batch / worker の入口処理、`packages/core` の use case 呼び出し、response DTO 型の明示、Mapper / Presenter / Builder による response 変換 |
| `packages/core` | entity、value object、domain service、use case / application service、repository interface、domain / application error、外部依存の抽象 interface |
| `packages/db` | DB 接続、ORM、repository 実装、transaction、DB record と domain object の mapper、永続化に閉じた query 実装 |

## 推奨ディレクトリ構成

以下は概念上の `api/` tree であり、現在の monorepo では `apps/api/` へ読み替える。

```text
api/
  src/
    app.module.ts
    main.ts
    bootstrap/
      config/
      filters/
      validation/
    modules/
      authentication/
        authentication.module.ts
        presentation/
          http/
            authentication.controller.ts
            dto/
            mappers/
            presenters/
            builders/
            validators/
            __tests__/
    shared/
      nest/
        decorators/
        guards/
        interceptors/
      observability/
```

## 構成の意図

- `packages/core` はフレームワーク非依存の業務本体に保つ。
- `packages/db` は DB 永続化アダプタとして閉じ込める。
- `api` / `apps/api` は HTTP 境界と NestJS の配線に集中させる。
- `api` / `apps/api` は薄く保ち、業務ロジックを持たせない。
- `packages/core` は NestJS / ORM / DB 実装詳細に依存させない。
- response DTO の表現責務は、単純変換なら Mapper、レスポンス表現の組み立てなら Presenter、最終 DTO の組み立てなら Builder として明示する。

## `api` 配下の各ディレクトリの責務

- `bootstrap/config`: アプリ起動時の config 読み込み、global provider 初期化。
- `bootstrap/filters`: `packages/core` の error を HTTP エラーへ変換する。
- `bootstrap/validation`: 共通の `ValidationPipe` 設定、request DTO の入力検証設定。
- `modules/<context>`: 機能単位の Nest module を置く。
- `presentation/http`: controller、DTO、HTTP 入口を置く。
- `presentation/http/dto`: request / response DTO を置く。request DTO は `class-validator` を前提にし、response DTO は controller の戻り値型として明示する。
- `presentation/http/mappers`: 単純な項目変換だけを担う Mapper を置く。
- `presentation/http/presenters`: response 表現を作る責務が中心の Presenter を置く。
- `presentation/http/builders`: 最終 DTO を組み立てる責務が中心の Builder を置く。
- `presentation/http/validators`: DTO で使う validator を置く。
- `shared/nest/guards`: 認証認可の入口判定を置く。
- `shared/nest/interceptors`: access log、tracing、latency 計測を置く。
- `__tests__/`: 対象コンポーネントに最も近い unit test を置く。

## 実装パターン

- `Module`: context ごとに module を切り、custom provider で `packages/core` の use case と `packages/db` の repository 実装を配線する。module は DI の composition root として扱う。
- `Controller`: 薄く保ち、request DTO を受け、認証済み user や request metadata を取得し、`packages/core` の use case を呼ぶ。戻り値型は必ず response DTO で明示し、response の生成は Presenter / Builder へ委譲する。controller でその場の object literal を組み立てない。業務ルールや DB 操作は書かない。
- `DTO / Validation`: DTO は HTTP 入力 / 出力表現として扱い、domain model と兼用しない。入力検証は DTO class と `ValidationPipe` を基本にする。

### Mapper / Presenter / Builder の使い分け

- `Mapper`: 単純な項目変換だけを担当する。例として `toDto(domainObject): ResponseItemDto` のような形にする。
- `Presenter`: response 表現を作る責務が中心のときに使う。collection、meta、link、request 由来の表現調整などをまとめ、必要に応じて複数の Mapper を組み合わせる。
- `Builder`: 最終 DTO を組み立てる責務が中心のときに使う。`BuildXxxDtoInput` のような入力型を定義し、`build(input): XxxDto` の形で返す。
- 引数が 3 つ以上に増える、または意味のまとまりを明示したいときは、Presenter でも `PresentXxxInput` のような入力型を定義してよい。
- response 生成責務に `Pipe` という名前を使わない。`ValidationPipe` は request 検証の組み込み機能としてだけ扱う。

### 命名の目安

- `AuditLogResponseMapper#toDto`
- `AuditLogPresenter#presentList`
- `AuditLogExportResponseDtoBuilder#build`
- `BuildAuditLogExportResponseDtoInput`
- `PresentAuditLogListInput`

## 例

```ts
import { Injectable } from "@nestjs/common";

import type { ApiRequest } from "../../../../../shared/observability/requestContext.js";
import type { AuditLogExportResponseDto } from "../dto/auditLogExportResponseDto.js";
import { buildAuditLogExportResponseDto } from "./helpers/buildAuditLogExportResponseDto.js";

type BuildAuditLogExportResponseDtoInput = {
  request: ApiRequest;
  stored: {
    exportId: string;
    fileName: string;
    expiresAt: Date;
  };
  auditLogId: number | bigint;
  recordCount: number;
};

@Injectable()
export class AuditLogExportResponseDtoBuilder {
  build(input: BuildAuditLogExportResponseDtoInput): AuditLogExportResponseDto {
    return buildAuditLogExportResponseDto(
      input.request,
      input.stored,
      input.auditLogId,
      input.recordCount,
    );
  }
}
```

```ts
import { Injectable } from "@nestjs/common";
import type { ApiRequest } from "../../../../../shared/observability/requestContext.js";
import { buildPaginatedMetaResponse } from "../../../../../shared/observability/responseBuilders.js";
import type { SearchAuditLogsResult } from "../../application/useCases/searchAuditLogsResult.js";
import { AuditLogListResponseDto } from "../dto/auditLogListResponseDto.js";
import { AuditLogResponseMapper } from "./auditLogResponseMapper.js";

@Injectable()
export class AuditLogPresenter {
  constructor(
    private readonly auditLogResponseMapper: AuditLogResponseMapper,
  ) {}

  presentList(
    request: ApiRequest,
    result: SearchAuditLogsResult,
  ): AuditLogListResponseDto {
    return {
      data: result.data.map((auditLog) =>
        this.auditLogResponseMapper.toDto(auditLog),
      ),
      meta: buildPaginatedMetaResponse(request, result.meta),
    };
  }
}
```

## 監査・認証認可・例外処理の置き場

- `Guard`: 認証済みか、ロール判定、入口の認可を扱う。
- `Filter`: `packages/core` の error を HTTP エラーへ変換する。
- `Interceptor`: access log、tracing、latency 計測を扱う。
- `Unit Test`: 対象コンポーネントのディレクトリ直下にある `__tests__/` へ置き、controller、validator、Mapper、Presenter、Builder、guard、interceptor、filter、module の近くで責務単位に確認する。

## `apps/api` 実装ルール

- module 名は bounded context または runtime の責務名に合わせる。
- `src/app.module.ts` `src/main.ts` を global entry point とし、共通の config / filter / validation は `src/bootstrap/` 配下へ整理する。
- `src/modules/<module-name>/` には `<module-name>.module.ts` と runtime 入口だけを置き、NestJS 固有ではない ApplicationService、QueryService、Repository interface、Prisma repository は `packages/core` `packages/db` へ分離する。
- `presentation/http` 配下には controller を薄いファイルとして置き、DTO、必要な Mapper / Presenter / Builder / validator を API 境界に閉じ込める。補助要素が少ない間は controller ごとのディレクトリを無理に増やさない。
- request DTO は `class-validator` と `ValidationPipe` を基本に扱い、DTO を domain model と兼用しない。
- response は基本的に DTO で返し、controller の戻り値型で明示する。response DTO の生成は Presenter / Builder を通して行う。
- webhook / batch / worker が不要なら空ディレクトリを作らない。
- module をまたいで共有する decorator / guard / interceptor は `src/shared/nest/`、observability は `src/shared/observability/` に置く。`packages/core` の error を HTTP エラーへ変換する filter は `src/bootstrap/filters/` へ寄せる。
- `apps/api` の unit test も対象コンポーネントに最も近いディレクトリ直下の `__tests__/` に必ず置き、別置きの共通 test フォルダへ逃がさない。
- Nest token や interface は複数実装切り替えが本当に必要なときだけ導入する。
- `openapi.yml` や async contract に書かれた transport 名を domain 内部へ漏らさない。

## アンチパターン

- controller に業務ロジックを書く。
- controller でその場の object literal から response を組み立てる。
- response DTO 生成クラスに `Pipe` という名前を付ける。
- response 生成責務を custom pipe へ押し込む。
- `api` / `apps/api` で DB 操作や ORM を直接扱う。
- `packages/core` に NestJS 依存を持ち込む。
- `packages/core` に ORM 実装を置く。
- DTO を domain model と兼用する。
- guard に業務ルールまで押し込む。
- interceptor / filter で use case 相当の判断をする。
- repository 実装を use case 化する。
- `api` / `apps/api` を fat service 化する。
- 責務の曖昧な `shared` / `common` に何でも入れる。
- 対象コンポーネントから離れた共通 `tests/` `specs/` フォルダへユニットテストを置く。

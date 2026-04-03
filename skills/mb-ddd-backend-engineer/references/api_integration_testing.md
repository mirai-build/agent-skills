# API 結合テストガイド

API 実装で扱う結合テストの正本。
NestJS の API テストは Playwright などのブラウザ E2E ではなく、`@nestjs/testing` と `supertest` を使って app を起動し、HTTP 入口から `packages/core` `packages/db` を通り、テスト用 DB まで接続して確認する結合テストとして扱う。
unit test や component test の代替ではなく、API と永続化をまたいだ完了確認として扱う。

## 着手条件

- 対象 use case の `packages/core` `packages/db` `apps/api` 実装がそろっている。
- API から呼ばれる ApplicationService / QueryService、Repository interface、concrete Repository、schema / migration / generate、module 配線、controller、DTO、Presenter / Builder、必要な guard / filter / interceptor が実装済みである。
- 対象 route が依存する非同期入口や外部 adapter がある場合は、結合テストで必要な範囲まで実装済みか、テスト用の fake / stub 方針が決まっている。
- テスト用 DB、env、app bootstrap を起動できる。
- どれかが欠ける場合は結合テストを先に書かず、backend component の実装完了を優先する。

## 配置ルール

- 既存 repo に API 結合テスト用のディレクトリ、起動 helper、script があるならそれを優先して流用する。
- 既存ルールがない場合は、spec を `api/tests/http-integration/<bounded-context>/` へ置く。
- unit test は引き続き対象コンポーネント直下の `__tests__/` に colocate し、DB 接続付き API 結合テストはそこへ混ぜない。
- 結合テストで複数 route から共有する fixture や helper は、既存 harness の共通置き場へ寄せる。

## 実装ルール

- NestJS の module 配線、DI、filter、validation を含めて実アプリ相当の構成で起動する。
- NestJS では `@nestjs/testing` で testing module / app を組み立て、`supertest` で request を送る。
- DB は mock にせず、テスト用 DB / schema / transaction reset を使って本物へ接続する。
- 外部 API、queue、mail など DB 以外の outbound integration は、既存 repo の方針に従って fake / stub / test double を使ってよい。ただし DB を mock へ置き換えない。
- request は `implementation/openapi.yml` の契約に合わせて送り、status code、response body、header を確認する。
- response だけで終わらず、DB へ保存された record、更新された状態、transaction の成否、冪等性や rollback を必要に応じて確認する。
- 対象 route ごとに、最低でも happy path と高リスクな失敗系を扱う。失敗系には validation、認可、not found、conflict、重複実行、整合性違反のうち設計上重要なものを優先する。
- test data は最小限にし、seed / fixture / factory のどれを使う場合も再現可能で順序依存を作らない。

## 進め方

1. 先に対象 use case の backend component 一式がそろっているか確認する。
2. 既存の結合テスト harness、test DB 起動方法、reset 手順、script を確認する。
3. route 単位で、事前データ、request、期待する response、確認すべき DB 変化を整理する。
4. 既存 harness がなければ、最小限の bootstrap / support / script を追加してから spec を書く。
5. unit test、build、型検査が通ることを確認したうえで API 結合テストを実行する。

## 最終確認

- API 結合テストは API 実装のあとに追加するのではなく、API を含む use case の完了条件として扱う。
- 実行コマンド、使った test DB 前提、seed / cleanup 方針、確認した endpoint を最終報告へ残す。
- 環境不足で API 結合テストを実行できない場合は、どの backend component までは実装済みで、何が不足して未実行なのかを明示する。

# 実装フローガイド

初動棚卸しから実装完了まで、何をどの順で確認し、どこで手を止めるかをそろえるためのガイド。
この文書は進行順と完了条件を扱い、具体的な配置規約や命名は profile 文書へ委ねる。

## 0. 初動棚卸し

- `docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation` を確認し、対象 bounded context、主要 use case、API / DB / async の入口候補を抜き出す。
- 既存コード、ディレクトリ構成、workspace、package manager、scripts、既存 module、検証コマンドを確認する。
- TypeScript では既存 export、shared contract、generated type、DTO を先に確認し、今回本当に追加が必要な型だけを洗い出す。
- 今回が新規実装か既存拡張かを整理し、どこまでを今回の完了点にするかを要約する。

## 1. 実装範囲を絞る

- 1 回の作業で扱う bounded context と use case を明確にする。
- 複数 context をまたぐ場合は、依存順に分割して小さく進める。
- write だけか、read API も含むか、同期 API だけか、Webhook / batch / worker まで含むかを先に決める。
- API を含む場合は、DB 接続付き API 結合テストを完了条件へ含めるか、環境不足で今回はどこまで実装するかを先に決める。
- 設計書に不足がある場合は、どこまでを質問で埋め、どこから先は実装を止めるかを決める。

## 2. profile を判定する

- 対象 repo が TypeScript モノレポなら `references/profiles/typescript/monorepo.md` を適用する。
- `apps/api` が NestJS なら `references/profiles/typescript/nest.md` も適用する。
- 現在サポートしている profile は TypeScript モノレポだけとし、該当しない構成は未対応として報告する。

## 3. `packages/core` を先にそろえる

- `contexts` を正本に、ValueObject、Entity、Aggregate、Repository interface、ApplicationService、QueryService、Gateway interface を先にそろえる。
- `packages/db` や `apps/api` の実装に着手する前に、後続 layer が参照する抽象と公開面を固める。
- 既存の ValueObject、Entity、shared contract、service の result 型で表現できるものは流用し、同義の型 alias や input type を増やさない。
- 詳細なディレクトリ構成、命名、共有物の置き場、test colocate のルールは `references/profiles/typescript/monorepo.md` を正本にする。
- 代表コンポーネントには、参照した設計書パスを短い日本語コメントで残す。

## 4. `packages/db` を実装する

- `implementation/NN_<bounded-context>/02_database` を正本に、永続化モデル、制約、transaction 境界を実装する。
- `packages/core` で先に定義した Repository interface を `implements` する concrete 実装を追加する。
- `packages/core` の型と ORM / generated type を優先して使い、永続化都合の mirror type は境界上の意味が増えるときだけ追加する。
- 業務判断は `packages/db` へ持ち込まず、永続化都合の変換と保存責務に閉じ込める。
- 詳細な Repository 配置、mapper / helper の切り出し、test colocate のルールは `references/profiles/typescript/monorepo.md` を正本にする。

## 5. `apps/api` を実装する

- `implementation/openapi.yml` を正本に、対象 bounded context の tag から route、DTO、error response、security を読み取る。
- controller / handler は薄い入口に保ち、`packages/core` の use case を呼ぶ構成にする。
- DTO や Presenter / Builder の入力型は transport 境界を明確にするために必要なものだけ追加し、既存 DTO や core の result 型で足りるなら流用する。
- response 生成、validation、NestJS 固有の責務分担、アンチパターンは `references/profiles/typescript/nest.md` を正本にする。
- module 配線や composition root 以外では `packages/db` の concrete 実装へ直接依存しない。

## 6. 非同期入口と外部連携を実装する

- `implementation/NN_<bounded-context>/03_async_contracts` がある場合は、Webhook / worker / batch の入口、署名検証、冪等性、retry、delivery ID 管理をその契約に合わせる。
- `contexts/07_domain_events` `08_external_integrations` だけがあり concrete 契約が未整備なら、外部 I/O 形状を推測で固定せず確認してから進める。
- outbox や event 保存が必要な場合は、`packages/core` `packages/db` `apps/api` のどこに責務を置くかを明示したうえで実装する。

## 7. API 結合テストを実装する

- API を実装対象に含む場合は、`packages/core` `packages/db` `apps/api` と必要な非同期入口 / 外部 adapter がそろってから、DB 接続付き API 結合テストへ着手する。
- NestJS の API テストは `@nestjs/testing` と `supertest` を使う結合テストとして扱い、Playwright などのブラウザ E2E とは分ける。
- 結合テストの置き場、bootstrap、DB reset、確認観点は `references/api_integration_testing.md` を正本にする。
- 結合テストでは HTTP response だけでなく、DB へ保存された状態や transaction の結果まで確認する。

## 8. 検証と仕上げ

- 変更した package / app を中心に build、lint、型検査、test を実行する。repo 既定のコマンドがあればそれを優先する。
- API を実装対象に含み、結合テストを実行できる環境があるなら、DB 接続付き API 結合テストも同じターンで実行する。
- export を更新し、利用側から必要な公開面がそろっているか確認する。
- 変更ファイル、実装した use case、仮置き前提、未実装 TODO、実施した検証をまとめて報告する。
- 実装過程で見つけた設計書との差分は、`domain_model` `contexts` `implementation` のどこへ返すべきかまで添えて報告する。

## 完了条件

- 対象 bounded context と今回の完了点が説明できる。
- 適用した profile と参照した設計書が説明できる。
- `packages/core -> packages/db -> apps/api` の順で、必要な export と unit test まで同じターンでそろっている。
- API を実装対象に含む場合は、結合テストの着手条件を満たしたうえで DB 接続付き API 結合テストまでそろっているか、未実施なら不足条件が説明できる。
- 未確定事項や仮置き前提が残る場合は、コードコメントまたは最終報告で明示している。
- 設計書と実装のずれを、どの文書へ返すべきか判断して報告している。

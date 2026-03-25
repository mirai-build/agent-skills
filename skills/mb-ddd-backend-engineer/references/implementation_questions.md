# 実装前の確認質問ガイド

DDD 設計書から実装へ落とすとき、設計書だけでは足りない項目を確認するためのガイドである。
一度に全部を聞かず、手戻りが少ない順に 1〜3 テーマずつ聞く。
質問へ進む前に、対象 bounded context の `docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation` を読み、どの論点が本当に未確定かを仕分ける。

## 0. 設計書の不足と不整合

まず、質問が必要なのか、それとも設計書間の不整合を解消すべきなのかを切り分ける。

- `implementation/01_api/openapi.yml` はあるか。あるなら、route、request / response、error response、security はそこから読めるか。
- `implementation/02_database` はあるか。あるなら、table、制約、監査項目、relation はそこから読めるか。
- `implementation/03_async_contracts` はあるか。あるなら、topic / endpoint、payload、認証 / 署名、冪等性、再送方針はそこから読めるか。
- `implementation` と `contexts` で、Aggregate 境界、Repository 責務、ApplicationService の完了点に食い違いがないか。
- `domain_model` の用語と API / DB の具体名がずれている場合、どこで翻訳するかが決まっているか。

理由:
設計書ですでに答えがあるのに聞き直したり、不整合を抱えたまま実装したりしないため。

## 1. 完了点と対象範囲

最初に、今回どこまで作れば「実装できた」と言えるかを確定する。

- 今回の対象 use case は何か。
- write だけで十分か、read API も同時に必要か。
- 同期 HTTP API だけか、webhook / batch / worker まで必要か。
- 今回は新規 context か、既存 context の拡張か。

理由:
完了点が曖昧だと、`core` `db` `api` のどこまで実装するかがぶれる。

## 2. Aggregate と一貫性境界

aggregate と transaction の単位が読み切れないときは、ここを優先して確認する。

- どの Entity / ValueObject までを 1 回の保存で一貫させる必要があるか。
- 同時更新時に競合として扱う単位は何か。
- 複数 aggregate をまたぐ処理は同期 transaction か、event / 非同期連携か。
- 削除は物理削除か、soft delete か。

理由:
ここが曖昧だと、Repository の境界、Prisma schema、ApplicationService の transaction 設計が決められない。

## 3. 識別子と状態遷移

ID と状態が曖昧なまま実装すると、後から破壊的変更になりやすい。

- ID は UUID か、DB 採番か、外部システム由来か。
- 生成タイミングは ApplicationService か DB か。
- 主な status と遷移条件は何か。
- `createdAt` `updatedAt` `deletedAt` 以外に監査項目が必要か。

理由:
ID 生成位置と状態遷移は domain model、schema、API すべてに影響する。

## 4. 永続化形と検索要件

read 要件は `query` と schema の形に直結する。

- `implementation/02_database` の table 設計で足りない検索・集計要件はあるか。
- 一覧取得、詳細取得、検索、並び替え、ページングは何が必要か。
- unique 制約や複合キーはあるか。
- JSON で保持してよい項目と、relation 化すべき項目は何か。
- 履歴管理、バージョン管理、監査ログは必要か。

理由:
Prisma model と QueryService の形を先に合わせるため。

## 5. API 境界

設計書に `06_interfaces` があっても、API として何を返すかは不足しやすい。

- `implementation/01_api/openapi.yml` で未確定の request / response schema や example はどこか。
- API の caller は誰か。管理画面、外部システム、batch、worker のどれか。
- request / response で最低限必要な項目は何か。
- 認可は actor 単位か、organization 単位か、role 単位か。
- エラー時は 404 / 409 / 422 など、どの意味で返したいか。

理由:
controller、DTO、ApplicationError の扱いが変わるため。

## 6. 外部連携と非同期処理

`07_domain_events` `08_external_integrations` があるときは、同期 / 非同期を明示する。

- `implementation/03_async_contracts` がない場合、どの契約を今回 concrete に決める必要があるか。
- 外部システムへ即時反映が必要か、後続 job でよいか。
- retry、冪等性、重複受信対策は必要か。
- webhook 受信時に署名検証や delivery ID 管理が必要か。
- event をコード上の契約だけで持つか、outbox など永続化も必要か。

理由:
`apps/api` の入口種別と、`packages/db` へ持たせる責務が変わるため。

## 7. 質問の出し方

- 先に既存コードと設計書から推測できる部分は埋めてから聞く。
- 「何を教えて下さい」だけでなく、「どの実装判断に必要か」を一言添える。
- 答えづらそうなら選択肢を添える。

例:

- ID は `ApplicationService` で UUID を振る前提で進めてもよいですか。それとも DB 採番が必要ですか。
- 一覧 API では `status` と `updatedAt` の sort が必要そうですが、優先度が高いのはどちらですか。
- この処理は同一 transaction で保存する理解で進めていますが、domain event に切り出す方が近いですか。

# 実装向け設計ガイド

この資料は、`mb-domain-driven-design` でドメイン設計の後に API や DB を含む実装向け設計を整理するときの観点をまとめたガイドである。
一度に全部を聞かず、いま作っている文書に必要な項目から 1〜3 テーマずつ確認する。

## 共通ルール

- このガイドは、対象 bounded context の `domain_model` と `contexts` が揃っているときだけ使う。
- まず `domain_model` と `contexts` から読み取れることを整理し、そこから推測できる項目は質問前に埋める。
- API や DB の都合で bounded context や aggregate の責務を崩さない。
- 実装用の名前がユビキタス言語や宣言済みのシステム英語名と異なる場合は、差分と理由を文書へ残す。
- 回答が難しそうなら、選択肢や仮説を先に提示して確認する。

## 出力の正本

- API 設計は `implementation/openapi.yml` を正本とし、bounded context は tag で区切る。
- DB 設計は `02_database/00_overview.md` の Mermaid ER 図と、各 table の詳細文書を正本とする。
- 各 table 詳細では、少なくとも `| 物理名 | 説明 | データ型 | 備考 |` の表形式でカラム一覧を出す。
- 非同期イベントや Webhook がある場合は、`03_async_contracts/00_overview.md` と各契約詳細を正本とする。

## API 設計で聞くこと

### 入口と caller

- この入口は誰が使うか。管理画面、外部システム、worker、batch のどれか。
- 同期 HTTP API、GraphQL、webhook、batch 起動のどれに近いか。
- どのユースケースを開始または参照するための入口か。

### 認可と前提条件

- actor、organization、role のどの単位で認可を掛けるか。
- 呼び出し前に満たしているべき前提条件は何か。
- 二重送信や再実行が起きたとき、同じ結果として扱う必要はあるか。

### 入出力

- request で最低限必要な項目は何か。
- response で caller が必ず受け取りたい項目は何か。
- 一覧 API の場合、filter、sort、pagination で必要な条件は何か。
- API の項目名とドメイン内部の ValueObject / Entity 名が違う場合、どこで変換するか。

### エラーと運用

- 404、409、422、429 など、どの意味の失敗を caller へ返したいか。
- タイムアウト、部分成功、外部連携失敗をどう扱うか。
- 監査ログやメトリクスとして残すべき情報は何か。

### OpenAPI として詰めること

- path、method、operationId、tag をどう切るか。tag は原則 bounded context 単位にそろえる。
- requestBody、parameter、response schema をどの名前で components 化するか。
- security scheme と認可前提をどう表現するか。
- example や enum、format をどこまで明記するか。

## DB / 永続化設計で聞くこと

### 保存対象

- どの Aggregate や read model を、どの保存単位で持つか。
- table、view、collection、event store のどれで表すのが近いか。
- write 用モデルと read 用モデルを分ける必要はあるか。

### 制約と一貫性

- unique 制約、複合キー、参照整合性で守るべき条件は何か。
- transaction で同時に守るべき更新は何か。
- soft delete、履歴保持、監査列、バージョン列が必要か。

### 検索と性能

- 主な検索条件、並び替え、集計は何か。
- index を貼らないと困りそうなアクセスはどれか。
- 保持期間、アーカイブ、パーティション、データ量見込みに制約はあるか。

### 名前と変換

- DB の column 名、enum 値、状態値がドメイン用語とずれるか。
- Repository がどこまで ORM record と Aggregate の変換責務を持つか。
- JSON カラムへ寄せる項目と正規化する項目の線引きは何か。

### ER 図と table 定義として詰めること

- Mermaid ER 図で、どの relation と cardinality を表現するか。
- 各 table の主キー、外部キー、unique、index をどこまで明示するか。
- カラム一覧の備考に、nullable、default、制約、監査列、論理削除の扱いをどう書くか。

## 非同期イベント / Webhook 契約で聞くこと

### 契約の境界

- この契約は送信か受信か。domain event 配信、外部 webhook 受信、外部 webhook 送信のどれか。
- どのユースケースや状態変化を契機に発火 / 受信するか。
- どの topic、queue、endpoint、event type を使うか。

### 契約内容

- payload に最低限必要なフィールドは何か。
- provider 固有の header、署名、delivery ID、retry count はあるか。
- versioning は event 名、header、payload のどこで表現するか。

### 配送保証と障害時の扱い

- at-least-once、at-most-once、順序保証のどれを前提にするか。
- retry、dead letter、再送、重複受信対策をどうするか。
- 失敗時に caller / provider / 運用担当へどう見せるか。

### セキュリティと運用

- 署名検証、IP 制限、認証トークンなど何が必要か。
- 監査ログ、トレース ID、delivery ID として何を残すか。
- テストやローカル検証で再現すべき代表 payload は何か。

## 追加すると役立つ詳細設計

- 認可 / 権限マトリクス
  - actor や role ごとに、どの API / 操作が許可されるかを一覧化する。
- エラー一覧
  - 業務エラー、HTTP ステータス、caller への見せ方を対応付ける。
- 状態遷移図
  - status を持つ aggregate がある場合、状態遷移と禁止遷移を明確にする。
- 非同期イベント / webhook 契約
  - domain event、外部通知、受信 webhook がある場合、payload、署名、再送、冪等性、運用時の扱いを整理する。
- データライフサイクル
  - 保持期間、アーカイブ、物理削除、マイグレーション観点を明確にする。

## 実装へ渡す前の最終確認

- API 文書から、どの ApplicationService / QueryService を呼ぶか追えるか。
- DB 文書から、どの Repository / Aggregate を保存するか追えるか。
- caller 視点の契約とドメイン内部の用語差が説明できるか。
- エラー、認可、冪等性、監査、再実行方針が抜けていないか。
- 実装スキルへ渡す前提として、未確定事項と仮置きが明示されているか。

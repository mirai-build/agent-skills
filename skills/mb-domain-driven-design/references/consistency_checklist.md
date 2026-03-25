# 整合性チェックリスト

設計を更新したら、少なくとも次の観点で整合性を確認する。

## システムの目的と価値

- 解決する問題と、コア業務の判断根拠がつながっているか。
- 対象ユーザーの困りごとが、コンテキスト設計の対象ユースケースへ落ちているか。
- スコープ外の項目が、後続ドキュメントで暗黙に実装対象になっていないか。
- 各ディレクトリ、または context 配下カテゴリの `00_overview.md` が最新で、後続の詳細ドキュメントを正しく案内できているか。
- 現在の成熟度に対して、飛ばしすぎたフェーズへ進んでいないか。

## 用語

- 同じ概念に複数の呼び名を使っていないか。
- 日本語名とシステム英語名が 1 対 1 で対応付いているか。
- システム英語名が原則 2 語以内で、API 名、DB 名、コード識別子へ流用しやすい形になっているか。例外がある場合は理由が残っているか。
- 画面、API、DB、業務現場で呼び名が異なる場合、その差分を説明できているか。
- ユビキタス言語と Mermaid 図の要素名が一致しているか。

## ドメインモデリング

- `01_system_purpose` `02_actors` `03_usecases` `04_journeys` `05_bounded_contexts` の順で読める構成になっているか。
- コア業務 / 支援業務の切り分け理由が、提供価値や業務上の役割と結び付いているか。
- actor 定義がユースケースや bounded context 分割の前提としてつながっているか。
- サブドメインへ分割した理由が、責務や会話の明確化に結び付いているか。
- Bounded Context 候補とドメインモデル図の範囲が矛盾していないか。
- Bounded Context 候補が、どのコア業務または支援業務に属するか追えるか。
- ドメインイベント、ルール、ホットスポットが文書間で欠落していないか。
- ユースケースを追加した場合、主要 actor、開始条件、完了条件、主な flow、関係する context が追えるか。
- ユーザージャーニーを追加した場合、関連ユースケース、時系列、各 context の関与箇所が追えるか。

## コンテキスト配下の設計対象

- Value Object の不変条件が、Entity や Aggregate の設計と矛盾していないか。
- Aggregate の一貫性境界と Repository の永続化単位が一致しているか。
- Domain Service に、Application Service が持つべき調停ロジックが入り込んでいないか。
- Application Service が、ドメインルールそのものを抱え込みすぎていないか。
- Query Service が読み込み専用の責務に閉じており、更新責務を持っていないか。
- Interface の入力表現とドメイン内部の表現の変換責務が明確か。
- Domain Event を追加した場合、発火元、発火条件、利用先が追えるか。
- External Integration を追加した場合、連携先、連携方向、障害時の扱いが追えるか。

## コンテキスト設計

- `domain_model/05_bounded_contexts` で bounded context 候補と主要用語が整理される前に、context 設計へ進んでいないか。
- bounded context の日本語名とシステム英語名が、`contexts/NN_<bounded-context>/` のディレクトリ名と対応しているか。
- ユースケースがある場合、各 context がどのユースケースを主に担うか説明できるか。
- ユーザージャーニーがある場合、各 context がどのジャーニーのどの区間を担うか説明できるか。
- 各コンテキスト設計が、どの Application Service、Query Service、Aggregate を使うか追えるか。
- `06_interfaces` を除く各カテゴリの `00_overview.md` に載っている項目ごとに、対応する詳細ドキュメントが存在するか。overview だけで終わっていないか。
- `07_domain_events` `08_external_integrations` は、本当に必要な context にだけ追加されているか。不要な context で惰性的に増えていないか。
- 詳細ドキュメントのタイトルがカテゴリ名のまま残っておらず、設計対象の実名になっているか。テンプレート由来の注記が残っていないか。
- Value Object、Entity、Aggregate、Repository、Domain Service、Application Service、Query Service、Interface の責務分担が重複していないか。
- 正常系、例外系、権限、監査、外部連携、再実行方針が抜けていないか。
- 永続化順序やトランザクション境界が、各設計対象の前提と一致しているか。
- コンテキスト設計で新しく出た概念が、必要なら上位ドキュメントへ反映されているか。

## 実装向け設計

- 対象 bounded context の `domain_model` と `contexts` が揃う前に、API / DB 設計へ進んでいないか。
- `implementation/00_overview.md` と各 context 配下の `00_overview.md` が最新で、API / DB 詳細ドキュメントを正しく案内できているか。
- 実装向け設計で使う context 名、API 名、DB 名が宣言済みのシステム英語名と対応付いているか。
- API 設計の正本として `implementation/openapi.yml` が存在し、主要な path / schema / error / security が追えるか。
- `implementation/openapi.yml` の tag が bounded context と対応し、対象 context の operation を迷わず追えるか。
- API 設計から、どの ApplicationService / QueryService を呼ぶか追えるか。
- API の request / response / error が caller の責務と一致しているか。
- API の項目名がドメイン用語と異なる場合、その変換責務が説明されているか。
- DB 設計の `00_overview.md` に Mermaid の ER 図があり、table 間の関係が追えるか。
- DB / 永続化設計から、どの Aggregate / Repository を保存するか追えるか。
- 各 table 詳細に `| 物理名 | 説明 | データ型 | 備考 |` のカラム一覧があり、制約や nullable など必要な補足が追えるか。
- DB の制約、index、削除方針、監査項目がユースケースと矛盾していないか。
- 非同期イベントや Webhook がある場合、`03_async_contracts` が存在し、topic / endpoint、payload、署名 / 認証、再送、冪等性、失敗時の扱いが追えるか。
- 実装向け設計で新しく出た API 名、DB 名、状態名が必要に応じて上位設計へ反映されているか。

## 更新時の確認

- 仮置きだった前提が確定したとき、関連ドキュメントをすべて更新したか。
- 変更理由が大きい場合、どの設計判断が変わったか説明できるか。
- 未解決事項と次に確認したい質問を残せているか。
- `domain_model` を更新した場合、影響を受ける `contexts` と `implementation` を見直したか。
- `contexts` を更新した場合、影響を受ける `implementation` を見直したか。

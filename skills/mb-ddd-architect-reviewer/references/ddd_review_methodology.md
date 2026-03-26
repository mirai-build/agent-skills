# DDD 設計レビュー方法論

この資料は、`mb-ddd-architect-reviewer` が設計書をレビューするときの基準をまとめたものである。
2026-03-26 時点で、主に Martin Fowler と Microsoft Learn / Azure Architecture Center の公開資料を確認し、安定して再利用しやすい観点だけを抽出している。

## 使い方

- まず設計書を「ドメイン理解」「戦略設計」「戦術設計」「実装接続」に分類する。
- いま揃っている層まででレビュー深度を決める。上流が薄い状態で、下流だけ細かく減点しない。
- 指摘を書くときは、方法論の名前だけでなく「その欠落が何を壊すか」まで言語化する。
- 迷ったら、レビュー対象の問題が「用語」「境界」「不変条件」「整合性」「外部境界」のどこに属するかを先に決める。

## 1. 戦略設計のレビュー観点

### ドメイン理解

- DDD の出発点は、技術より先に業務理解を作ることにある。
- Microsoft の domain analysis ガイドでは、実装前に business function とその関係を整理し、event storming のような方法で共有理解を作ることを勧めている。
- したがって、設計書レビューでは最初に「誰の、どんな業務課題を、どの use case で解くのか」が読み取れるかを確認する。

#### 典型的な不足

- システム目的がなく、画面や API の説明だけが並んでいる。
- actor はあるが、各 actor が何を完了とみなすか分からない。
- use case と bounded context のつながりが見えない。

### ユビキタス言語

- Microsoft は、ユビキタス言語を「会話、文書、コードで一貫して使う共有語彙」と説明している。
- Martin Fowler も bounded context の中ではモデルが一貫している必要があると強調している。
- そのためレビューでは、同じ用語が文書、図、API、DB、コード候補で同じ意味を保っているかを見る。

#### 典型的な不足

- 同じ語が context ごとに意味を変えるのに、その境界が宣言されていない。
- 画面用語、業務用語、コード名の対応表がない。
- 外部 API の語彙が内部ドメインへそのまま侵入している。

### サブドメインと bounded context

- Microsoft の domain analysis では、最初に core / supporting / generic subdomain を見極め、その後に bounded context を定義する流れが推奨されている。
- bounded context は「どのモデルがどこで有効か」を決める境界であり、技術レイヤの分割ではない。
- したがってレビューでは、context 分割理由が業務能力や会話境界で説明されるかを確認する。

#### 典型的な不足

- `API` `DB` `notification` のような技術責務で context を切っている。
- 1 つの context が複数の unrelated business capability を抱えている。
- core subdomain と generic subdomain が同じ深さで扱われ、投資優先度が読み取れない。

### Context Map と外部境界

- Microsoft は context map を、bounded context 間の関係と責務を明確にする手段として整理している。
- 関係パターンとして、Customer-Supplier、Open Host Service + Published Language、Anti-Corruption Layer、Separate Ways などが挙げられている。
- レビューでは、単に矢印があるかではなく「誰が upstream で、誰が downstream か」「どこで翻訳し、どこで保護するか」が説明できるかを確認する。

#### 典型的な不足

- context 間に依存はあるが、責務の主従や契約オーナーが不明である。
- 外部システムとの境界に Anti-Corruption Layer 相当の説明がない。
- 共有モデル前提で結合しており、片方の変更がもう片方へ即波及する。

## 2. 戦術設計のレビュー観点

### Rich Domain Model か

- Microsoft の DDD-oriented microservice ガイドは、anemic-domain model を避け、entity や aggregate に振る舞いを持たせる設計を勧めている。
- そのため、レビューでは data 定義だけでなく、不変条件、状態遷移、業務ルールがどこに置かれているかを確認する。

#### 典型的な不足

- Entity が属性一覧だけで、振る舞いが Application Service 側へ流出している。
- 「何を守るか」は書いてあるが、「どこで守るか」が不明である。

### Entity / Value Object

- Entity は識別子とライフサイクルを持つ概念として扱う。
- Value Object は値として比較され、不変条件を自身で表現できるのが理想である。
- レビューでは、識別が必要なものを VO にしていないか、逆に単なる値を Entity にしていないかを見る。

#### 典型的な不足

- 日付範囲、金額、住所、ステータスなどのルールを VO へ閉じず、各所でバリデーションが重複している。
- 永続化都合だけで ID を生やし、本来 VO でよい概念が Entity 化している。

### Aggregate と整合性境界

- Martin Fowler は Aggregate を「単一 unit として扱うドメインオブジェクトの塊」と説明し、外部参照は root 経由に限定し、transaction は aggregate 境界をまたがないのが基本だとしている。
- Microsoft の domain events ガイドでも、複数 aggregate にまたがるルールは eventual consistency を検討し、必要なら domain event でつなぐ考え方が整理されている。
- したがってレビューでは、「何を同時に守るか」「どこまでが 1 transaction か」「複数 aggregate 間の整合性をどう扱うか」を必ず見る。

#### 典型的な不足

- 1 つの aggregate に unrelated な更新理由が詰め込まれ、境界が大きすぎる。
- 複数 aggregate を常に同時更新しているのに、transaction 方針や event 設計がない。
- Root を介さず内部 entity を直接更新する前提になっている。

### Domain Service / Application Service / Query Service

- Tactical DDD では、domain rule は entity や aggregate に寄せ、単一 aggregate に閉じない純粋な業務判断だけを Domain Service へ置くのが基本となる。
- Application Service は use case の orchestration、認可、transaction、外部呼び出しをまとめる層として扱う。
- Query Service は読み取り専用の最適化層であり、更新責務を持たせない。

#### 典型的な不足

- Domain Service が単なる呼び出し順の調停だけをしている。
- Application Service が業務ルールそのものを抱え、domain model が空洞化している。
- Query Service が更新や副作用を持っている。

### Repository

- Microsoft は repository を、永続化関心を domain model の外へ置くための DDD パターンとして説明している。
- そのため、repository は table ごとの CRUD ラッパではなく、aggregate の取得・保存境界として評価する。

#### 典型的な不足

- table ごとに repository を切り、domain 側の境界と一致していない。
- domain model が永続化都合へ引きずられ、repository が業務ルールまで引き受けている。

### Domain Event

- Microsoft の domain events ガイドでは、domain event を同一 domain 内の副作用分離や複数 aggregate への伝播に使う整理が示されている。
- レビューでは、event を使う理由、発火元、購読側、整合性戦略、失敗時の扱いが文書化されているかを確認する。

#### 典型的な不足

- 重要な business event が暗黙のままで、連携や監査の起点が見えない。
- Domain Event と外部公開する integration event が混同されている。
- 冪等性、再送、失敗時補償が必要なのに何も書かれていない。

## 3. 実装接続レビューの観点

- use case と API / UI / batch / worker の対応が追えるか。
- aggregate と repository と DB テーブル群の対応が追えるか。
- 認可、監査、履歴、例外系、差し戻し、再実行、SLA 制約など、業務運用に効く論点が抜けていないか。
- external system との境界で、内部モデルを守る翻訳層が設計されているか。

実装接続のレビューは、上流が揃っているときだけ細かく行う。
bounded context や aggregate 境界が曖昧なまま API / DB を細かく直しても、後で大きく手戻りしやすい。

## 4. レビュー時の判断順序

1. 目的と actor が読めるか。
2. ユビキタス言語と use case が読めるか。
3. サブドメイン、bounded context、context map が読めるか。
4. tactical design が責務分離できているか。
5. 実装接続で抜けや矛盾がないか。

この順序を崩すのは、対象が明確に「実装直前の 1 context だけ」と分かっている場合に限る。

## 5. 指摘の書き方

- 単に「DDD らしくない」と書かず、何の観点が欠けているかを明示する。
- 「不足している artefact 名」だけでなく、「その不足がどんな誤実装や合意齟齬を招くか」まで添える。
- 可能なら 1 指摘につき 1 つの修正指示へ落とし込み、`mb-ddd-architect` がそのまま扱える粒度にする。
- 修正順序は、上流を先、下流を後にする。

## 参考ソース

- [Use domain analysis to model microservices](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis)
  - 戦略設計、ユビキタス言語、subdomain 分類、bounded context、context map の見方を整理するために参照した。
- [Design a DDD-oriented microservice](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/ddd-oriented-microservice)
  - anemic model を避け、entity / aggregate / domain service をどう見るかの整理に使った。
- [Domain events: Design and implementation](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/domain-events-design-implementation)
  - aggregate 間整合性、eventual consistency、domain event の扱いを整理するために参照した。
- [Design the infrastructure persistence layer](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design)
  - repository を永続化関心の分離として見る観点を整理するために参照した。
- [Bounded Context](https://martinfowler.com/bliki/BoundedContext.html)
  - bounded context とモデル一貫性の考え方を確認するために参照した。
- [DDD Aggregate](https://martinfowler.com/bliki/DDD_Aggregate.html)
  - aggregate root、外部参照、transaction 境界の考え方を確認するために参照した。

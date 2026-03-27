# `mb-ddd-architect` 文書構造ガイド

この資料は、`mb-ddd-architect-qa` が `skills/mb-ddd-architect` により整備された `docs/designs` を読むときの正本である。
Q&A では最初に「今どの文書があり、どこまで確定しているか」を確認し、その後で質問別に深掘りする。

## 1. まず押さえる標準構造

### `docs/designs/domain_model`

- `01_system_purpose`
  - システムの目的、対象課題、提供価値を確認する。
- `02_actors`
  - 誰が何の立場で関わるかを確認する。
- `03_usecases`
  - 主要な業務フローとシステム責務を確認する。
- `04_journeys`
  - use case 同士の流れを確認する。
- `05_bounded_contexts`
  - bounded context の切り方、責務分担、context map を確認する。

### `docs/designs/contexts/NN_<bounded-context>/`

- `00_overview.md`
  - その context の目的、責務、主な文書一覧を確認する入口。
- `01_value_objects`
  - 不変条件を持つ値概念を確認する。
- `02_entities`
  - 識別子を持つ概念とライフサイクルを確認する。
- `03_aggregates`
  - 同時に守る不変条件の境界を確認する。
- `04_repositories`
  - 永続化や取得の責務単位を確認する。
- `05_services`
  - domain service / application service / query service の役割分担を確認する。
- `06_interfaces`
  - 外部公開インターフェースや依存境界を確認する。
- `07_domain_events`
  - 複数 aggregate や他 context へ伝播するイベントを確認する。
- `08_external_integrations`
  - 外部システムとの接続責務や翻訳境界を確認する。

### `docs/designs/implementation`

- `00_overview.md`
  - implementation 全体の入口と、context ごとの実装対象を確認する。
- `openapi.yml`
  - API の正本。tag で bounded context を区別する。
- `NN_<bounded-context>/02_database`
  - ER 図、table 一覧、各 table 詳細を確認する。
- `NN_<bounded-context>/03_async_contracts`
  - 非同期イベントや Webhook の payload、認証、再送、冪等性を確認する。

## 2. 読む順番

1. `domain_model` で目的と境界を押さえる。
2. 対象 bounded context の `contexts` を読み、責務とモデルを確認する。
3. API、DB、非同期契約が質問に含まれるときだけ `implementation` を読む。

`implementation` だけでは「なぜその構造なのか」が分からないため、必ず `domain_model` と `contexts` を先に読む。

## 2.5 打ち切り条件

次の 3 点が揃ったら、追加探索を止めて回答へ移る。

- 直接の質問に答える主張が 1 つ定まっている
- その主張を支える根拠文書が 2〜4 件そろっている
- 未確定点がある場合は、その不足を 1〜3 件で言語化できている

次のような探索は避ける。

- 直接の答えに不要な隣接 bounded context の深掘り
- `00_overview.md` で未作成と分かるカテゴリをさらに探し続けること
- 同じ論点について `contexts` と `implementation` の周辺文書を際限なく広げること
- `docs/designs` 全件一覧や repo 全体への広い grep を初動で流すこと
- entity 名や service 名だけで `docs/designs` 全体を横断検索すること
- `docs/designs` や対象 context 配下を `ls` / `find` で列挙してから読むこと

## 2.6 初動の最小セット

標準構造の repo では、まず次の最小セットから入る。

1. `docs/designs/00_overview.md`
2. 質問に対応する `domain_model` の正本 1 件
3. 対象 context の `00_overview.md`
4. 直接の答えに効く詳細文書 1〜2 件

この段階で答えられるなら、追加探索しない。

標準規約で推定できる場合は、repo 全体検索より次の既定パスを優先する。

- service 質問:
  - `contexts/NN_<context>/05_services/00_overview.md`
  - `contexts/NN_<context>/05_services/02_application_services.md`
  - `contexts/NN_<context>/05_services/03_query_services.md`
- 責務配置質問:
  - `contexts/NN_<context>/00_overview.md`
  - `contexts/NN_<context>/03_aggregates/00_overview.md`
  - `contexts/NN_<context>/04_repositories/00_overview.md`
  - 必要な個別詳細
- DB 質問:
  - `contexts/NN_<context>/03_aggregates/01_<aggregate>.md`
  - `contexts/NN_<context>/04_repositories/01_<aggregate>_repository.md`
  - `implementation/NN_<context>/02_database/00_overview.md`
  - `implementation/NN_<context>/02_database/01_<table>.md`

質問語から上記パスを推定できる場合は、entity 名や service 名で repo 全体を grep しない。
また、標準構造がある repo では `ls` / `find` でディレクトリを列挙せず、既定パスへ直接飛ぶ。

## 2.7 追加探索の条件

次のどちらかに当てはまるときだけ、既定ルートの外へ 1〜2 文書だけ追加してよい。

- 既定ルートの文書同士で結論が衝突している
- 既定ルートの文書だけでは `不足または確認事項` を具体化できない

それ以外では、追加探索せずに回答へ移る。

## 3. 質問別の参照マップ

### どのようなサービスを実装すべきか

最優先で読む文書:

- `docs/designs/00_overview.md`
- `domain_model/03_usecases`
- `domain_model/04_journeys`
- 対象 context の `05_services`
- 必要に応じて `06_interfaces` `07_domain_events`

見る観点:

- use case ごとに誰が何を完了したいのか
- 業務判断を持つのは domain service か aggregate か
- orchestration を行うのは application service か
- 参照専用の問い合わせは query service へ分けるべきか

回答の要点:

- 「サービス名」だけでなく、入力、出力、責務境界、どの aggregate / repository / interface と関わるかまで説明する。
- 実装方法ではなく、設計上どの service を置くべきかに焦点を当てる。
- ログイン、組織参加、契約更新のように連続する処理があっても、質問で聞かれている完了点を主回答に固定する。
- 後続の service が必要でも、主回答には混ぜず「ログイン後に続く service」などの補足として分離する。
- 典型的には `00_overview`、use case、service 文書、必要なら journey の 4 件で止める。

### どこにどう設計すべきか

最優先で読む文書:

- `docs/designs/00_overview.md`
- `domain_model/05_bounded_contexts`
- 対象 context の `00_overview.md`
- 対象カテゴリの詳細文書

見る観点:

- その責務はどの bounded context に属するか
- aggregate 内で閉じる判断か、application service の調停か
- interface と external integration のどちらで扱うべきか
- 他 context のモデルをそのまま持ち込んでいないか

回答の要点:

- 「どこに置くか」だけでなく、「なぜそこに置くと境界と責務が自然か」を説明する。
- 配置先のディレクトリやカテゴリ名を示し、対応する根拠文書を添える。
- 対象カテゴリが未作成なら、推測で別カテゴリへ寄せ切らず、「未整備のため確定不能」と返す。

### DB 構造はどうすべきか

最優先で読む文書:

- `docs/designs/00_overview.md`
- 対象 context の `03_aggregates`
- 対象 context の `04_repositories`
- `implementation/NN_<bounded-context>/02_database`
- 必要に応じて `implementation/openapi.yml`

見る観点:

- 何を 1 つの整合性境界として保存するか
- repository がどの aggregate を永続化するか
- table が aggregate / entity / value object のどこに対応するか
- API や外部契約の識別子と DB の物理名がどう対応するか

回答の要点:

- まずドメイン上の保存単位と不変条件を説明し、その後に table や column の話へ下りる。
- `implementation/02_database` が未整備なら、物理設計は未確定として扱う。
- Webhook 履歴や監査 table のような周辺 table は、直接質問されていない限り補足に留める。
- 典型的には aggregate、repository、database overview、対象 table 詳細の 4 件で止める。

### API や外部連携をどう考えるべきか

最優先で読む文書:

- 対象 context の `06_interfaces`
- `08_external_integrations`
- `implementation/openapi.yml`
- `03_async_contracts`

見る観点:

- ドメイン用語と公開 API 名の翻訳境界
- 同期 API と非同期契約の役割分担
- 冪等性、認可、再送、失敗時の扱い

## 4. 情報不足のときの返し方

- `domain_model` が不足している:
  - 目的、actor、use case、bounded context が薄いため、下流設計は仮説止まりと伝える。
- `contexts` が不足している:
  - service、aggregate、repository の責務は確定できないため、推測と不足を分けて返す。
- `implementation` が不足している:
  - API / DB / 非同期契約は未確定とし、物理設計や外部契約を断定しない。

不足が大きいときは、次のように返す。

- どの文書が不足しているか
- その不足のせいで何が確定できないか
- `mb-ddd-architect` で次に整備すべき文書

## 5. 回答テンプレート

```md
## 結論

[質問への短い回答]

## 根拠

- [参照文書 1] から読めること
- [参照文書 2] から読めること

## 不足または確認事項

- [未記載のため断定できない点]
- [追加で確認したい論点]
```

質問が広い場合は、先に主論点を 1 つ選び、「今回は service 設計として回答する」のように前提を明示する。
調査ログや読み順の説明は、最終回答に長く残さない。

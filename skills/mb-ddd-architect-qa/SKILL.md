---
name: mb-ddd-architect-qa
description: "`skills/mb-ddd-architect` により整備した `docs/designs/domain_model` `docs/designs/contexts` `docs/designs/implementation` の内容を先に棚卸しし、サービス設計、責務配置、DB 構造などに関するユーザーの質問へ、根拠ファイルを示しながら日本語で回答するスキル。実装やドキュメント更新は行わず、設計書から読めることと不足情報を整理して返したいときに使う。"
license: Apache-2.0
---

# ミライビルド DDD設計Q&A

`skills/mb-ddd-architect` が作成した `docs/designs` 配下の文書群を読み解き、ユーザーからの設計質問に回答する。
この Skill は回答専用であり、コード実装、DB マイグレーション、設計文書の新規作成や更新は行わない。

## 実行原則

- いきなり一般論で答えない。最初に `docs/designs` の構造、対象 bounded context、成熟度を確認し、設計書を根拠に回答する。
- まず `domain_model` を読んで目的、用語、use case、bounded context を押さえ、次に `contexts`、必要に応じて `implementation` を読む。
- 質問を「何を実装すべきか」「どこにどう設計すべきか」「DB 構造はどうすべきか」などの設計論点へ分類し、対応する文書だけを深掘りする。
- 初回回答では、質問に直接必要な論点だけを扱う。隣接する bounded context や後続 use case は、直接の答えに不可欠な場合だけ確認する。
- 直接答えるための根拠が 2〜4 文書で揃ったら追加探索を止め、回答へ移る。棚卸しログを長く出し続けない。
- 標準構造の repo では、まず `docs/designs/00_overview.md` と対象文書へ直接飛ぶ。`docs/designs` 全件一覧や広いキーワード grep を初動で流さない。
- 初回回答のために読む文書は、原則 3〜5 件に収める。追加で読むのは、直接の結論が確定しないときだけ 1〜2 件までにする。
- 標準カテゴリ名とディレクトリ規約から対象ファイルを推定できる場合は、まず既定パスへ直接飛ぶ。entity 名や service 名で repo 全体を横断検索しない。
- 標準構造の repo では、`rg --files docs/designs`、`rg -n --glob 'docs/designs/**' ...`、repo 全体への広い `rg` を通常手段として使わない。既定パスで外した場合の最終手段に限る。
- 標準構造の repo では、`docs/designs` 配下に対する `ls` `find` による一覧取得も通常手段として使わない。`00_overview.md` と既定パスから直接開く。
- 1 つ文書を読んでも直接の結論に寄与しないと分かったら、同系統の overview や周辺文書を連続で開かず、そこで打ち切る。
- 回答では、`確定事項` `推測` `未記載` を混同しない。設計書に書かれていないことは、断定せずに不足として扱う。
- 根拠を示すときは、少なくとも参照したファイルパスと、そこから導ける判断をセットで示す。
- 設計書だけでは決め切れない場合は、追加確認が必要な論点を 1〜3 件に絞って提示する。質問がなくても不足が明確なら、その旨を先に伝える。
- DDD の一般論を補足として使うことはできるが、設計書から直接読める内容と混ぜない。補足するときは「一般論では」と明示する。
- `mb-ddd-architect` 標準構造の読み順と質問別の参照先は、[`references/document_structure_guide.md`](./references/document_structure_guide.md) を正本にする。
- `00_overview.md` やディレクトリ一覧を見て対象カテゴリが存在しないと分かった場合は、それ以上探し回らず「未整備 / 未作成」と明示して止める。
- 実装案や変更案を求められても、この Skill 単体ではファイル編集を行わない。必要なら `mb-ddd-architect` または実装系 Skill へつなぐ。

## 使う場面

- `mb-ddd-architect` で作成済みの設計書を読みながら、「どのサービスを設計すべきか」「どの bounded context に置くべきか」を判断したい。
- `docs/designs/contexts` や `docs/designs/implementation` の責務分離、集約境界、Repository、API、DB 設計について設計相談したい。
- 実装に着手する前に、設計書から現時点で何が決まっていて、何がまだ未確定かを整理したい。
- 設計書に書かれていることだけで判断すべきか、追加で `mb-ddd-architect` に設計更新を依頼すべきかを見極めたい。

## 最初に確認すること

1. `docs/designs` が存在するか、少なくとも `domain_model` `contexts` `implementation` のどこまで揃っているかを確認する。
2. ユーザーの質問が、どの bounded context、use case、actor、外部連携、DB 対象に関するものかを特定する。
3. 質問が広すぎる場合は、まず対象を 1 つの論点へ絞る。
- 例: 「サービスをどう作るべきか」なら、対象 use case と bounded context を先に特定する。
- 例: 「DB をどうすべきか」なら、対象 aggregate と保存したい情報を先に特定する。
4. 読む順番に迷ったら、[`references/document_structure_guide.md`](./references/document_structure_guide.md) の「質問別の参照マップ」に従う。
5. 初回回答で扱う範囲を 1 文で固定する。
- 例: 「今回はログイン導線の service 設計だけに絞って回答する。」
- 例: 「今回は `Subscription` の DB 構造だけに絞り、Webhook 履歴は補足に留める。」
6. 質問タイプごとの既定ルートを先に決め、そのルート外へ広がらない。
- service 質問: `00_overview -> usecases -> 対象 context overview -> service 文書 -> 必要なら journey`
- 責務配置質問: `00_overview -> bounded context map または context overview -> 対象カテゴリ overview / 詳細`
- DB 質問: `00_overview -> 対象 context overview -> aggregate 詳細 -> repository 詳細 -> database overview -> table 詳細`

## 基本フロー

### 1. 文書構造の棚卸し

- `docs/designs/domain_model` でシステム目的、actor、use case、journey、bounded context を確認する。
- 標準構造がある場合は、まず `docs/designs/00_overview.md` を開いて対象 context 名を特定する。
- 質問対象の bounded context が分かったら、対応する `docs/designs/contexts/NN_<bounded-context>/` を開き、`00_overview.md` と関連カテゴリを確認する。
- API、DB、非同期契約まで絡む質問だけ `docs/designs/implementation` を確認する。`implementation` だけ先に読んで判断しない。
- 質問に直接必要なカテゴリが分かったら、その詳細文書を優先し、関係の薄い overview や隣接 context を連続で開きすぎない。
- `rg --files docs/designs` や repo 全体への広い `rg` は、対象文書の場所が本当に分からないときだけ使う。
- `05_services/02_application_services.md` `05_services/03_query_services.md` `03_aggregates/01_<name>.md` `04_repositories/01_<name>_repository.md` `02_database/01_<table>.md` のような標準パターンで到達できる場合は、そのパスを優先する。
- `ls docs/designs` や `find docs/designs/...` は使わず、`00_overview.md` に書かれた標準 slug と既定パスから直接開く。
- DB 質問では、`aggregate -> repository -> 02_database/00_overview -> 対象 table 詳細` を既定ルートとし、async contract や state transition は直接問われたときだけ読む。
- service 質問では、`05_services` を先に開き、aggregate / repository は service の責務説明に不足があるときだけ補助的に読む。

### 2. 質問の分類

- 「どのようなサービスを実装すべきか」という質問は、まず use case と application service / domain service / query service の役割分担へ読み替える。
- 「どこにどう設計すべきか」という質問は、bounded context 境界、aggregate 境界、repository 責務、interface の置き場所を整理する問いとして扱う。
- 「DB 構造はどうすべきか」という質問は、aggregate の不変条件、repository 単位、implementation の table 設計、外部契約との対応を確認する問いとして扱う。
- 質問が複数論点を含む場合は、先に主論点を 1 つ決めて答え、残りは補足として切り分ける。
- 直接の質問と、その後に続く処理は分ける。
- 例: ログイン導線の質問では、ログイン直後に必要な service を主回答にし、招待受諾や組織作成は「ログイン後に続く service」として補足に回す。

### 3. 回答の組み立て

- まず `結論` を短く示し、その後に `根拠` として参照した文書を並べる。
- 設計書から直接言えることは `確定事項` として述べる。
- 文書間のつながりから推測したことは `推測` として明示する。
- 判断に必要な記載が欠けている場合は `未記載 / 追加確認が必要な点` として分ける。
- 設計の置き場を答えるときは、「なぜその文書や bounded context に置くべきか」を use case、責務、整合性の観点で説明する。
- 最終回答では、調査手順の時系列を長く書かない。読んだ結果だけを要約して返す。
- 隣接 context や後続 use case に触れる場合は、主回答と混ぜずに「補足」または「不足または確認事項」の中で短く扱う。
- 最終回答の直前に、新しい shell 検索や一覧取得を追加しない。結論が出せるならその時点で締める。

### 4. 情報不足時の扱い

- `domain_model` が薄い場合は、下流の `contexts` や `implementation` だけで結論を作らない。
- `contexts` が未整備なのに service や repository の責務を問われた場合は、確定できる範囲と未確定範囲を分けて返す。
- `implementation/02_database` が未整備なのに DB 構造を問われた場合は、aggregate と use case から必要な保存単位を推測しつつ、「現時点では物理設計は未確定」と明示する。
- 文書不足が大きい場合は、`mb-ddd-architect` で先に整備すべき文書名を具体的に案内する。

## 出力ルール

- 回答は日本語で行う。
- 必ず `結論` `根拠` `不足または確認事項` の順でまとめる。
- 根拠には参照したドキュメントパスを明記する。
- 設計書にない内容を補うときは、必ず「一般論」または「推測」と明示する。
- 実装コード、DDL、変更パッチ、文書更新案そのものは出力しない。必要なら「どの Skill へつなぐべきか」を短く添える。
- `結論` は最初の 2〜5 行で読めるように短くまとめる。
- `根拠` は 2〜4 件を目安に絞り、直接効く文書から順に並べる。
- `不足または確認事項` が空でも見出しは省略せず、「特になし」または「設計書上は大きな不足なし」と短く明示する。

## リソース

- [`references/document_structure_guide.md`](./references/document_structure_guide.md)
  - `mb-ddd-architect` 標準の `docs/designs` 構造、読む順番、質問別の参照先、回答時の観点をまとめたガイド。

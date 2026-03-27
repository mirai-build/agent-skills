---
name: mb-ux-designer
description: ユーザージャーニーを起点に、`docs/designs/domain_model` を参照しながらプロジェクトルートの `ux/` に画面構成ドキュメントを段階的に整備するスキル。前提となる `01_system_purpose` や `04_journeys` が不足している場合は、自分で補完せず `mb-ddd-architect` へ委譲し、前提がそろっていれば `03_basic_layouts` `04_screen_inventory` `05_navigation_map` `06_screen_details` の順で整理したいときに使う。
license: Apache-2.0
---

# ミライビルド UXデザイナー

ユーザージャーニーを起点に、プロジェクトルートの `ux/` 配下の画面構成ドキュメントを段階的に整備する。
詳細 UI や実装配置へ飛ばず、まずは `basic_layouts` `screen_inventory` `navigation_map` `screen_details` を「基本構成 → 一覧 → 遷移 → 詳細」の順で読める状態にそろえる。

## 実行原則

- 最初に `docs/designs/domain_model/01_system_purpose` `02_actors` `03_usecases` `04_journeys` を確認する。
- `01_system_purpose` または `04_journeys` が不足・未整備なら、自分で補完しない。不足点と必要な前提を整理して `mb-ddd-architect` へ委譲して終了する。
- `02_actors` と `03_usecases` は補助参照とし、画面の目的、主 actor、完了条件、遷移理由を補うために使う。
- `ux/01_experience_scope` と `02_user_journeys` は正本を持たず、`domain_model` へのリンクだけを置く。本文を重複して書かない。
- 1 回の作業で 1 つの段階だけ進める。`03_basic_layouts` `04_screen_inventory` `05_navigation_map` `06_screen_details` を同時に広げすぎない。
- `03_basic_layouts` では、プロダクト全体のナビゲーション方針、画面の大分類、レイアウトの基本型、利用端末ごとのレスポンシブ方針、共通 UI 領域を定義する。見た目のワイヤーまではここで決めない。
- `03_basic_layouts` の共通 UI 領域は、存在するものだけを書く。存在しないものを機械的に列挙しない。本来あるべきところを意図的に外している場合だけ、その不採用を理由付きで書く。
- 基本構成は 1 つに固定しない。複数の基本構成パターンが必要なら、`03_basic_layouts/01_*.md` を複数作成して管理する。
- `04_screen_inventory` は overview を正本とし、画面一覧、簡単な説明、ユーザージャーニーとの対応を表形式で管理する。
- 主要状態は既定で `通常` `空状態` `入力・業務エラー` `権限不足` を扱う。読み込み、確認モーダル、部分エラーなどは必要なときだけ追加する。
- 画面遷移図は `05_navigation_map` で 1 ジャーニー 1 ファイルを基本とし、`04_screen_inventory` で定義した画面同士の接続関係を Mermaid と表で整理する。
- 各画面詳細は `06_screen_details` で 1 画面 1 ファイルを正本とし、画面遷移の責務は持たせない。`入口と出口` のような遷移定義は書かない。
- 同じ画面を複数ジャーニーで使う場合も、画面詳細は 1 ファイルのままにし、ジャーニー別の利用文脈と完了条件を分けて整理する。
- 各画面詳細では、どの基本構成を参照する画面かに加え、主要な画面内 UI と UI ごとの責務、必要な端末差分を明示する。
- 詳細ドキュメントを追加または更新したら、対応する `00_overview.md` の一覧も同時に更新する。
- 確定事項、仮置き、未確定事項を区別して記載する。仮置きで進める場合は、どこが仮説かを明示する。
- 用語が `domain_model` と衝突する場合は、勝手に新語を作らず、どちらを正とするか確認してから反映する。

## 使う場面

- 新規プロダクトや新機能で、ユーザージャーニーをもとに必要画面の一覧化から始めたい。
- すでにある `domain_model` を参照しながら、`ux/` に画面構成の入口を整備したい。
- UI の見た目や実装に入る前に、画面の基本構成、画面一覧、遷移、画面詳細を文書として固めたい。
- 画面一覧はあるが、基本構成や遷移整理が薄く、画面詳細を安定して書ける前提をそろえたい。

## 最初に確認すること

1. 既存資料を確認する。少なくとも `docs/designs/domain_model`、既存の `ux/`、要件書、画面メモ、画面一覧、ワイヤー、既存コードを調べる。
2. 前提文書がそろっているかを確認する。
- `01_system_purpose/00_overview.md`
- `02_actors/00_overview.md`
- `03_usecases/00_overview.md`
- `04_journeys/00_overview.md`
3. `ux/` の成熟度を見て、次のどの段階にいるかを判定する。
- UX 文書が未整備、または基本構成が薄い: `03_basic_layouts` から始める。
- `basic_layouts` はあるが画面一覧が薄い: `04_screen_inventory` を整備する。
- `screen_inventory` はあるが画面遷移が薄い: `05_navigation_map` で 1 ジャーニー分の遷移を整理する。
- `navigation_map` まであるが画面詳細が薄い: `06_screen_details` を 1 画面ずつ整備する。
4. 前提文書が不足していれば、`mb-ddd-architect` へ委譲するために不足点を整理する。
- どの文書が欠けているか
- 画面設計へ進めない理由
- 最低限ほしい材料
5. ユーザーへ、次のような材料があれば共有してもらう。
- 既存の画面一覧、ワイヤー、画面メモ
- 主要ユーザーと利用端末
- 主要フロー、例外フロー、権限制約
- 必ず出したい情報と、主要アクション

## 成熟度に応じた進め方

### 1. UX 文書が未整備、または `basic_layouts` が薄いとき

- まず `ux/00_overview.md` を作成または更新し、整備順を共有する。
- 続いて `01_experience_scope/00_overview.md` と `02_user_journeys/00_overview.md` を作成し、`domain_model` の正本へのリンクを置く。
- そのうえで `03_basic_layouts/00_overview.md` を作成し、基本構成パターンの一覧を整理する。
- 基本構成の詳細は 1 パターンずつ `03_basic_layouts/01_*.md` で追加する。

### 2. `basic_layouts` があり、`screen_inventory` が薄いとき

- `04_screen_inventory/00_overview.md` を作成または更新し、画面一覧、簡単な説明、ユーザージャーニーとの対応を表で整理する。
- 画面ごとの接続関係や詳細定義はここへ書き込まない。遷移は `05_navigation_map`、画面ごとの責務は `06_screen_details` へ分ける。

### 3. `screen_inventory` があり、`navigation_map` が薄いとき

- `05_navigation_map/00_overview.md` を作成または更新し、遷移図を持つジャーニーの一覧を整理する。
- 1 回の作業では 1 ジャーニー分だけ `05_navigation_map/01_*.md` を作成または更新する。
- `navigation_map` では、正常遷移だけでなく、キャンセル、差し戻し、権限不足、離脱を追えるようにする。

### 4. `navigation_map` があり、`screen_details` が薄いとき

- `06_screen_details/00_overview.md` を作成または更新し、どの画面の詳細が定義済みかを一覧化する。
- 対象は 1 回の作業で 1 画面に絞る。
- `06_screen_details/01_*.md` では、画面の役割、利用文脈、画面内 UI、表示責務と操作責務、主要状態、関連文書を整理する。
- 画面遷移の入口と出口は `05_navigation_map` の責務として扱い、画面詳細へ重複して書き込まない。

## 基本フロー

1. 前提確認
- `domain_model` の `01_system_purpose` `02_actors` `03_usecases` `04_journeys` を読み、画面構成へ必要な前提がそろっているかを判定する。
- `01_system_purpose` または `04_journeys` が不足していれば、足りない材料を列挙して `mb-ddd-architect` を使うよう案内する。

2. 画面一覧の整理
- [`assets/templates/00_overview.md`](./assets/templates/00_overview.md) をもとに `ux/00_overview.md` を作成または更新する。
- [`assets/templates/01_experience_scope/00_overview.md`](./assets/templates/01_experience_scope/00_overview.md) と [`assets/templates/02_user_journeys/00_overview.md`](./assets/templates/02_user_journeys/00_overview.md) をもとに、`domain_model` へのリンク入口を整える。
- [`assets/templates/03_basic_layouts/00_overview.md`](./assets/templates/03_basic_layouts/00_overview.md) と [`assets/templates/03_basic_layouts/01_basic_layout.md`](./assets/templates/03_basic_layouts/01_basic_layout.md) を使い、画面基本構成と利用端末ごとのレスポンシブ方針をパターン単位で整理する。
- [`assets/templates/04_screen_inventory/00_overview.md`](./assets/templates/04_screen_inventory/00_overview.md) を使い、必要画面の一覧を整理する。

3. 画面遷移の整理
- [`assets/templates/05_navigation_map/00_overview.md`](./assets/templates/05_navigation_map/00_overview.md) と [`assets/templates/05_navigation_map/01_navigation_map.md`](./assets/templates/05_navigation_map/01_navigation_map.md) を使い、ジャーニーごとの画面遷移を Mermaid と表で整理する。
- `04_screen_inventory` で定義した画面同士の接続関係を、どの条件でどこへ進むかまで明示する。

4. 各画面詳細の整理
- [`assets/templates/06_screen_details/00_overview.md`](./assets/templates/06_screen_details/00_overview.md) と [`assets/templates/06_screen_details/01_screen_detail.md`](./assets/templates/06_screen_details/01_screen_detail.md) を使い、画面ごとの責務、利用文脈、画面内 UI を整理する。
- 各画面詳細では、参照する基本構成、画面の役割、ジャーニー別の利用文脈と完了条件、画面内 UI ごとの責務、主要状態を明示する。

5. 仕上げ
- [`references/consistency_checklist.md`](./references/consistency_checklist.md) を使って整合性を確認する。
- 作成または更新したファイル、今回確定した内容、仮置きの前提、未解決の質問をまとめて共有する。

## ヒアリングの進め方

- 1 回の質問は 1〜3 テーマに絞り、今の段階に必要なものだけを聞く。
- 抽象的な質問だけを投げず、候補やたたき台を添えて答えやすくする。
- `basic_layouts` では「グローバルナビの単位」「ローカルナビの有無」「ロール差分の扱い方」「画面の大分類」「レイアウトの基本型」「利用端末ごとの表示差分」「共通 UI 領域」を優先して聞く。
- `screen_inventory` では「どのジャーニーに、どの画面が必要か」「その画面は何を一言で説明できるか」を優先して聞く。
- `navigation_map` では「どの画面からどの画面へ進むか」「どんな条件で次へ進むか」「途中で戻る / 失敗する / 離脱するのはどこか」を優先して聞く。
- `screen_details` では「この画面で必ず見せる情報」「この画面で主に判断・操作すること」「共有画面ならジャーニー別の利用文脈と完了条件」「主要な画面内 UI」「どの基本構成を参照する画面か」を優先して聞く。
- ユーザーが答えづらいときは、仮説案を 1 つ提示し、「この理解で近いですか」と確認する。

## 出力ルール

- Markdown で作成する。
- `ux/01_experience_scope/00_overview.md` には、`domain_model/01_system_purpose` `02_actors` へのリンクだけを置く。内容を重複して書かない。
- `ux/02_user_journeys/00_overview.md` には、`domain_model/04_journeys` へのリンクだけを置く。必要に応じて `03_usecases` を補助参照として案内する。
- `03_basic_layouts` では、プロダクト全体のナビゲーション方針、画面の大分類、レイアウトの基本型、利用端末ごとのレスポンシブ方針、共通 UI 領域を整理する。
- `03_basic_layouts` の共通 UI 領域は、存在するものだけを書く。存在しないものは原則書かず、本来あるべきところを意図的に外している場合だけ理由付きで書く。
- `04_screen_inventory` は overview を正本とし、画面一覧、簡単な説明、ユーザージャーニーとの対応を表形式で置く。
- 同じ画面を複数ジャーニーで共有する場合も、`04_screen_inventory` では画面を複製せず 1 行で管理し、対応ジャーニーへ複数記載する。
- `05_navigation_map` では、Mermaid の遷移図と、遷移条件の表を必ずセットで置く。
- `06_screen_details` の詳細タイトルは画面の実名にする。`Screen` や `画面テンプレート` のまま残さない。
- `06_screen_details` では、各画面について参照する基本構成、目的、主 actor、対応ジャーニー、代表的な開始条件と完了条件、ジャーニー別の利用文脈、画面内 UI、主要状態、関連 context を必ず追えるようにする。
- `06_screen_details` には `入口と出口` の節を置かない。遷移定義は `05_navigation_map` で管理する。
- `06_screen_details` の個別 UI は、ボタンやラベル単位ではなく、利用者が意味のまとまりとして認識する単位で整理する。
- 詳細テンプレートでは、確定事項、仮置き、未確定事項を区別して残す。
- 画面名、状態名、ジャーニー名は、既存の `domain_model` と呼び名をそろえる。
- 文書を追加または更新したら、関連する `00_overview.md` と相互リンクも更新し、不整合を残さない。

## リソース

- [`references/hearing_guide.md`](./references/hearing_guide.md)
  - `basic_layouts` `screen_inventory` `navigation_map` `screen_details` の各段階で、どんな観点をヒアリングすると手戻りが少ないかをまとめたガイド。
- [`references/consistency_checklist.md`](./references/consistency_checklist.md)
  - `domain_model` と `ux` 文書の整合性、画面一覧と遷移の対応、主要状態の漏れを点検するためのチェックリスト。
- [`assets/templates/00_overview.md`](./assets/templates/00_overview.md)
  - `ux/` 配下の入口をそろえるためのテンプレート。
- [`assets/templates/01_experience_scope/00_overview.md`](./assets/templates/01_experience_scope/00_overview.md)
  - `domain_model/01_system_purpose` `02_actors` へのリンク入口をそろえるためのテンプレート。
- [`assets/templates/02_user_journeys/00_overview.md`](./assets/templates/02_user_journeys/00_overview.md)
  - `domain_model/04_journeys` へのリンク入口をそろえるためのテンプレート。
- [`assets/templates/03_basic_layouts/`](./assets/templates/03_basic_layouts)
  - 基本構成パターンを整理するためのテンプレート群。
- [`assets/templates/04_screen_inventory/`](./assets/templates/04_screen_inventory)
  - 画面一覧 overview を整理するためのテンプレート群。
- [`assets/templates/05_navigation_map/`](./assets/templates/05_navigation_map)
  - ジャーニー単位の画面遷移図と遷移条件表を整えるためのテンプレート群。
- [`assets/templates/06_screen_details/`](./assets/templates/06_screen_details)
  - 各画面の責務と主要状態を整理するためのテンプレート群。

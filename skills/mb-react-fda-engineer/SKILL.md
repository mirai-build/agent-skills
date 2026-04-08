---
name: mb-react-fda-engineer
description: React の Feature Driven Architecture を前提にフロントエンド実装を追加・更新するスキル。最初に対象リポジトリの既存ディレクトリルール、利用ライブラリ、フレームワークを確認し、責務分離を保ちながら、TanStack Start と Next App Router の profile に沿って進めたいときに使う。
license: Apache-2.0
---

# ミライビルド React FDAエンジニア

## 概要

React の Feature Driven Architecture を基準に、現在のリポジトリへフロントエンド実装を追加または更新する。
最初に対象 repo の既存ディレクトリルール、利用ライブラリ、フレームワークを確認し、repo 固有ルールを優先したうえで、足りない部分だけをこの Skill の共通原則と framework profile で補う。

## 実行原則

- いきなり新しい tree を作らない。最初に `AGENTS.md` `README.md` `docs/` `ux/` などから、repo 固有のフロントエンド構成ルールがあるかを確認する。見つかった場合はそれを最優先とし、この Skill の規約は責務分離を補強する補助線として使う。
- repo 固有の frontend 構成ルールが見つからなかった場合は、この Skill の共通原則と選択した framework profile をベストプラクティスとして採用する。その場合は、採用した構成を対象 repo の `README.md` に明記し、後続実装で迷わないようにする。
- 対象 framework を先に確定する。初版の主対象は TanStack Start で、Next は App Router profile を参照して対応する。どちらにも当てはまらない場合は、共通原則までは使えても framework 固有ルールは未対応として扱う。
- 利用ライブラリは repo 既存採用とユーザー方針を先に確認する。profile に必須ライブラリがあっても、新規導入や置き換えの実行前にはユーザーへ確認する。特に UI library の選定や state / form stack の切り替えは独断で進めない。
- 画面の責務を `routing layer` `page composition layer` `feature context layer` `global shared layer` `infra layer` に分けて考える。ディレクトリ名が違っても、まずこの責務対応へ写像してから実装する。
- `features/<context>/<feature>` に context 層を入れるかは常に固定にしない。repo 規模、use case 数、共有 language、shared types/helpers の量、team 境界を見て判断し、判断材料が揃わなければユーザーに確認する。判定基準は [`references/context_partitioning.md`](./references/context_partitioning.md) を正本にする。
- route / app layer に表示責務や複雑な業務ロジックを溜めない。URL、loader / prefetch、layout、metadata など routing 起点の責務だけへ寄せる。
- page composition layer は複数 feature を組み合わせて画面を構成する場所とし、再利用される業務ロジックや状態は feature 側へ戻す。
- feature 内部の `components/` `hooks/` `helpers/` `providers/` `queries/` `schemas/` `stores/` `types/` は必要なものだけ作る。空ディレクトリを埋めるために増やさない。
- feature の外からは必ず `index.ts` の public API を経由して使う。別 feature の内部ファイルへ deep import しない。共通化が必要なら context の `shared/` か global `shared/` へ引き上げる。
- 新規追加した関数、クラス、複雑な処理には、保守時に意図が追える短い日本語コメントを付ける。

## 使う場面

- TanStack Start のアプリで、`routes` `pages` `features` `shared` `api` を責務分離しながら実装を追加したい。
- Next App Router のアプリで、framework 固有の制約を崩さずに FDA ベースの feature 構成へ整理したい。
- 既存 repo の frontend ディレクトリルールと利用ライブラリを尊重しつつ、feature 単位の実装配置と public API 境界をそろえたい。
- `features/<context>/<feature>` へ context 分割するか、`features/<feature>` で十分かを判断しながら進めたい。

## 最初の進め方

1. `AGENTS.md` `README.md` `docs/` `ux/` `package.json` router 設定を確認し、repo 固有の frontend ディレクトリルール、利用ライブラリ、framework を特定する。個別ルールが見つからなかった場合は、本 Skill の構成を採用する前提で進める。
2. [`references/implementation_flow.md`](./references/implementation_flow.md) を読み、初動棚卸し、profile 選定、context 分割判断、実装順、検証順をそろえる。
3. [`references/fda_principles.md`](./references/fda_principles.md) を読み、framework 非依存の責務分離と import 境界を確認する。
4. context 分割が論点になる場合は [`references/context_partitioning.md`](./references/context_partitioning.md) を読む。
5. repo が TanStack Start なら [`references/frameworks/tanstack-start.md`](./references/frameworks/tanstack-start.md) を、Next App Router なら [`references/frameworks/next-app-router.md`](./references/frameworks/next-app-router.md) を読む。repo 固有ルールがある場合は、それを優先しながら profile を補助線として使う。
6. profile が要求するライブラリと repo 既存採用との差分を整理し、新規導入や置き換えが必要なら先にユーザーへ確認する。
7. 変更対象を `route / app` `page composition` `feature` `shared` `api` のどこへ置くか決め、最小の vertical slice で実装する。
8. repo 固有ルールが見つからなかった場合は、採用した構成と利用ライブラリ方針を対象 repo の `README.md` へ追記する。
9. 最後に、採用した profile、context 分割の判断、利用ライブラリの判断、`README.md` 反映の有無、追加した public API、実施した検証を日本語で簡潔に報告する。

## 参照ルール

- framework 非依存の責務分離、依存方向、public API 境界は [`references/fda_principles.md`](./references/fda_principles.md) を正本にする。
- repo 固有ルールの探索順、profile 選定、実装順、最終報告の観点は [`references/implementation_flow.md`](./references/implementation_flow.md) を正本にする。
- `features/<context>/<feature>` を使うかどうかの判定は [`references/context_partitioning.md`](./references/context_partitioning.md) を正本にする。
- TanStack Start の既定構成は [`references/frameworks/tanstack-start.md`](./references/frameworks/tanstack-start.md) を正本にする。
- Next App Router の既定構成は [`references/frameworks/next-app-router.md`](./references/frameworks/next-app-router.md) を正本にする。
- repo 固有ルールと Skill ルールがぶつかる場合は、まず repo 固有ルールを優先し、責務分離が崩れる箇所だけを明示して補う。

## リソース

- [`references/implementation_flow.md`](./references/implementation_flow.md)
  - 既存ルールの見つけ方、framework profile の選び方、実装順と検証順をまとめたガイド。
- [`references/fda_principles.md`](./references/fda_principles.md)
  - framework 非依存で守る責務分離、依存方向、public API 境界をまとめた共通原則。
- [`references/context_partitioning.md`](./references/context_partitioning.md)
  - `features/<context>/<feature>` へ分けるか、flat feature にするかの判断基準。
- [`references/frameworks/tanstack-start.md`](./references/frameworks/tanstack-start.md)
  - TanStack Start 向けの標準 tree と、`src/api` `src/routes` `src/pages` `src/features` `src/shared` の責務。
- [`references/frameworks/next-app-router.md`](./references/frameworks/next-app-router.md)
  - Next App Router 向けの標準 tree と、`src/app` `src/screens` `src/features` `src/shared` `src/api` の責務。

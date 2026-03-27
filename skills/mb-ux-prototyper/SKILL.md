---
name: mb-ux-prototyper
description: mb-ux-designer で整えた UX 設計をもとに、Build Web Apps plugin の skill も併用しながら ux/prototype へ TanStack Start ベースの画面プロトタイプを実装するスキル。pnpm dev で画面遷移を確認し、Storybook で主要状態を確認したいときに使う。
license: Apache-2.0
---

# ミライビルド UXプロトタイパー

`skills/mb-ux-designer` で整理した `ux/03_basic_layouts` `04_screen_inventory` `05_navigation_map` `06_screen_details` を入力に、プロジェクトルートの `ux/prototype` へ TanStack Start ベースの画面プロトタイプを実装する。
目的は API 接続前の導線確認と画面全体の見え方の検証であり、`pnpm dev` では画面遷移、Storybook では状態差分を確認できる形へ責務分離する。

## 実行原則

- 最初に `ux/03_basic_layouts` `04_screen_inventory` `05_navigation_map` `06_screen_details` と `docs/designs/domain_model` を確認し、画面名、ジャーニー名、状態名の正本をそろえる。
- `screen_inventory` `navigation_map` `screen_details` のいずれかが不足し、ルート構成や画面責務を決め切れない場合は推測で埋めず、不足点を整理して `mb-ux-designer` の利用を提案する。
- 実装先は原則 `ux/prototype` とし、既存の TanStack Start や Storybook 構成があれば repo の流儀を優先しつつ、その配下へ寄せる。
- `pnpm dev` は画面遷移と通常フローの確認を主目的にし、複雑な状態切り替えは抱え込まない。状態差分は Storybook の画面単位 story へ寄せる。
- Story はコンポーネント単位ではなく画面単位で作る。1 story で画面全体を確認できる構成にし、`通常` `空状態` `入力・業務エラー` `権限不足` などの差分は scenario ごとに切り替える。
- API や外部通信は実装しない。データはローカル fixture、ローカル state、画面遷移用の固定データで扱う。
- 外部システムや今回の対象外画面へ遷移する必要がある場合は、`ux/prototype` 内に簡易モック画面を置いて受ける。モックは「外部画面であること」と「戻り先 / 次アクション」が分かる最小構成に留める。
- UI kit は Radix と shadcn を使ってよいが、shadcn の既成レイアウトをそのまま多用しない。特に `Sidebar` のようなアプリ骨格は安易に流用せず、必要な構造を Tailwind CSS v4 と Radix primitive で組み立てる。
- `Build Web Apps` plugin が利用可能な環境では、その skill を優先的に併用する。特に見た目の方向性を固める段階では `build-web-apps:frontend-skill`、React / TanStack Start 実装では `build-web-apps:react-best-practices`、shadcn 利用時は `build-web-apps:shadcn` を参照する。
- UI レビューやアクセシビリティ確認を求められたら `build-web-apps:web-design-guidelines` を使って変更箇所を見直す。プレビュー共有やデプロイを求められたら `build-web-apps:deploy-to-vercel` を使い、既定で preview deploy を選ぶ。
- 新規追加した関数、クラス、複雑な処理には、保守時に意図が追える短い日本語コメントを付ける。
- 既存 repo に alias、lint、Storybook、ルーティング規約がある場合はそれを優先し、`ux` の設計用語とコード上の命名がずれる場合は差分を報告する。

## Build Web Apps plugin 併用方針

- `build-web-apps:frontend-skill`
  - `03_basic_layouts` と `06_screen_details` を読んだ直後に使い、visual thesis、content plan、interaction thesis を短く固めてから UI 実装へ入る。
- `build-web-apps:react-best-practices`
  - route、screen、story を実装または更新するときに使い、state 配置、再レンダリング、import、重い処理の扱いを崩さない。
- `build-web-apps:shadcn`
  - `components.json` がある repo や shadcn を追加・更新する場面で使う。既存 component と alias を確認し、既成のアプリ骨格をそのまま流用しない。
- `build-web-apps:web-design-guidelines`
  - UI レビュー、UX レビュー、アクセシビリティ観点の確認を求められたときに使う。変更した画面、story、レイアウト関連ファイルを対象にする。
- `build-web-apps:deploy-to-vercel`
  - ユーザーが preview URL や共有環境を求めたときに使う。`ux/prototype` 単体でも既存 frontend workspace 配下でも、対象 directory を明示して preview deploy する。

## 使う場面

- `skills/mb-ux-designer` で整理した UX 設計を、実際に触れる TanStack Start の画面プロトタイプへ落とし込みたい。
- API 実装前に、画面遷移、導線、レイアウト、主要状態の見え方をローカルだけで確認したい。
- `pnpm dev` では導線だけを見たい一方、状態差分は Storybook で画面単位に整理したい。
- 対象外の外部画面も含めて導線をつなぎたいが、本実装までは不要なので簡易モックで受けたい。
- Radix と shadcn を使いつつ、shadcn 依存の強すぎるレイアウトには寄せず、後で育てやすいプロトタイプを作りたい。

## 最初の進め方

1. `ux/` と `docs/designs/domain_model`、既存フロントエンド構成、package manager、Storybook 設定、Tailwind CSS v4 設定を確認し、今回のプロトタイプ対象範囲を決める。
2. [`references/prototype_playbook.md`](./references/prototype_playbook.md) を読み、`ux/prototype` の置き方、route と screen と story の責務分離、外部画面モックの扱い方、`Build Web Apps` plugin の使い分けを確定する。
3. `Build Web Apps` plugin が使える環境では、まず `build-web-apps:frontend-skill` で visual thesis と interaction thesis を固め、その後 `03_basic_layouts` をもとにアプリ骨格を決め、`04_screen_inventory` `05_navigation_map` から route を切り、`06_screen_details` をもとに各画面を実装する。
4. route、screen、story、shadcn component の実装では `build-web-apps:react-best-practices` と `build-web-apps:shadcn` を参照し、主要状態は [`references/verification_checklist.md`](./references/verification_checklist.md) を見ながら Storybook の画面単位 story へ切り出し、`pnpm dev` には通常フローだけを残す。
5. 作成または更新した route、screen、story、mock、設定ファイルを共有し、必要に応じて `build-web-apps:web-design-guidelines` または `build-web-apps:deploy-to-vercel` を使って仕上げ確認や preview 共有まで進める。

## 参照ルール

- `ux/prototype` の推奨構成、route / screen / story / mock の責務分離、実装順序は [`references/prototype_playbook.md`](./references/prototype_playbook.md) を正本にする。
- 実装完了時の確認項目、Storybook に寄せるべき状態、外部画面モックの確認観点は [`references/verification_checklist.md`](./references/verification_checklist.md) を使う。
- `Build Web Apps` plugin の各 skill をどの場面で併用するかは [`references/prototype_playbook.md`](./references/prototype_playbook.md) の「Build Web Apps plugin を併用する順序」を正本にする。
- `SKILL.md` には発火条件と判断の入口だけを置き、細かい実装パターンや確認項目は `references/` 側へ寄せる。

## 出力ルール

- 実装先は原則 `ux/prototype` とし、TanStack Start の route が `screen_inventory` と `navigation_map` の画面遷移を追えるようにする。
- 画面名、ジャーニー名、主要状態名は `ux/` の文書とそろえる。コード都合で別名が必要なときは対応関係を説明する。
- Storybook の story は画面単位で作成し、コンポーネント単位 story を量産しない。
- 外部画面モックには、モックであること、想定している外部画面名、戻り先または次アクションを明示する。
- API 呼び出し、外部通信、認証連携は入れない。表示切り替えはローカル state と fixture で完結させる。
- 仕上げでは、`pnpm dev` で確認できる導線、Storybook で確認できる状態、今回モックに留めた範囲を分けて報告する。

## リソース

- [`references/prototype_playbook.md`](./references/prototype_playbook.md)
  - `ux/` の設計文書を TanStack Start の route / screen / story へ写像する手順、`ux/prototype` の構成方針、外部画面モックの作り方をまとめた実装ガイド。
- [`references/verification_checklist.md`](./references/verification_checklist.md)
  - `pnpm dev` と Storybook の責務分離、状態差分のカバー範囲、ローカル state の完結性、コメント付与の確認観点をまとめたチェックリスト。

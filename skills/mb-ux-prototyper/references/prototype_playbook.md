# プロトタイプ実装プレイブック

`mb-ux-prototyper` は、`skills/mb-ux-designer` で整えた `ux/` 文書をそのまま UI 実装へ写経するのではなく、`route` `screen` `story` `mock` の責務へ分解して `ux/prototype` へ落とす。

## 入力として確認するもの

- `ux/03_basic_layouts`
- `ux/04_screen_inventory`
- `ux/05_navigation_map`
- `ux/06_screen_details`
- `docs/designs/domain_model/01_system_purpose`
- `docs/designs/domain_model/04_journeys`
- 既存の frontend workspace、Storybook 設定、Tailwind CSS v4 設定、TanStack Start 設定

`screen_inventory` `navigation_map` `screen_details` のどれかが薄く、route や画面責務を決め切れない場合は自分で補完しない。足りない前提を整理して `mb-ux-designer` を案内する。

## `ux/prototype` の基本責務

- `ux/prototype` は、プロダクト本体とは切り離した検証用の UI ワークスペースとして扱う。
- 既存 repo に TanStack Start の構成がある場合はそれを優先し、`ux/prototype` はその中の app root、package、workspace、または feature 置き場として整合する形を取る。
- 既存構成がない場合は、`ux/prototype` を TanStack Start アプリの最小単位として立ち上げる。
- API や外部通信は入れず、表示用データはローカル fixture と local state だけで完結させる。

## 推奨する責務分離

repo の流儀がある場合はそれを優先しつつ、次の責務分離を目安にする。

- `routes`
  - URL と画面遷移の責務だけを持つ。
  - `navigation_map` にある導線をたどれることを優先し、複雑な状態分岐は持ち込まない。
- `screens`
  - 画面全体の見た目と画面内ローカル state をまとめる。
  - `screen_details` にある表示責務と操作責務を反映する。
- `ui`
  - 再利用する低レベル部品を置く。Radix primitive の wrapper や軽い共通部品が中心。
  - layout 全体まで shadcn の既成パターンへ寄せすぎない。
- `mocks`
  - fixture data、外部画面の簡易モック、ローカル state の初期値を置く。
- `stories`
  - 画面単位 story を置く。画面全体の確認を目的にし、コンポーネント単位の story を増やしすぎない。

## 実装順序

1. `03_basic_layouts` を読んで、アプリ骨格と共通 UI 領域を決める。
2. `04_screen_inventory` をもとに、今回作る画面とモックで済ませる画面を切り分ける。
3. `05_navigation_map` を route に写像し、`pnpm dev` で正常導線をたどれる最低限の遷移を作る。
4. `06_screen_details` をもとに、各画面の表示責務と操作責務を screen 実装へ落とす。
5. `通常` 以外の状態は Storybook の画面単位 story へ分離する。
6. 対象外画面や外部システム画面は、`ux/prototype` 内の簡易モック画面で受ける。

## Build Web Apps plugin を併用する順序

`Build Web Apps` plugin が使える環境では、`mb-ux-prototyper` 単独で閉じずに次の順で併用する。

1. `build-web-apps:frontend-skill`
   - `03_basic_layouts` と対象画面の `06_screen_details` を読んだ直後に使う。
   - 実装前に visual thesis、content plan、interaction thesis を短く決め、画面の見た目を generic にしない。
2. `build-web-apps:react-best-practices`
   - route、screen、story を書くたびに参照する。
   - 特に state の置き場所、不要な再レンダリング、重い処理、import の切り方を点検する。
3. `build-web-apps:shadcn`
   - shadcn component を新規追加または更新するときに使う。
   - `components.json`、alias、iconLibrary、Tailwind 設定を確認し、既存 component を優先して使う。
4. `build-web-apps:web-design-guidelines`
   - UI レビューやアクセシビリティ観点の確認を求められたときに使う。
   - 変更した route、screen、story、global CSS を対象に見直す。
5. `build-web-apps:deploy-to-vercel`
   - ユーザーが preview URL や共有環境を求めたときに使う。
   - 既定で production ではなく preview deploy を選び、対象 directory を明示してデプロイする。

## `pnpm dev` と Storybook の切り分け

### `pnpm dev` に残すもの

- ジャーニーの開始から完了までの通常導線
- 主要な画面遷移
- レイアウトや導線のつながり確認
- 1 画面あたり代表的な通常状態

### Storybook に寄せるもの

- `空状態`
- `入力・業務エラー`
- `権限不足`
- ローカル state によるタブ切り替え、展開状態、選択状態
- バリエーション比較が必要な文言差分、表示差分、注意喚起 UI

Storybook 側では、1 story ごとに画面全体が分かるようにする。個別部品の粒度へ崩しすぎず、screen を直接レンダリングする構成を優先する。

## Radix と shadcn の使い方

- アクセシビリティ付きの振る舞いが必要な箇所は、Radix primitive を優先して使う。
- shadcn は button、dialog、select などの土台として使ってよいが、アプリ全体の shell を既製品へ寄せる使い方は避ける。
- 特に `Sidebar` のようなアプリ骨格コンポーネントは、`03_basic_layouts` の要求に合わせて自前で組み立てる前提にする。
- Tailwind CSS v4 の token と utility を使い、色、余白、境界線、タイポグラフィの判断を component ごとにばらつかせない。
- `build-web-apps:shadcn` を使うときも、この Skill では `Sidebar` や dashboard block をそのまま画面骨格に採用しない。あくまで低レベル部品の導入と既存 component の安全な更新に使う。

## 外部画面モックの作り方

外部システムや今回の対象外画面へ遷移する必要がある場合は、簡易モックで十分とする。

- 画面上部に「外部画面モック」など、モックであることが分かる表示を置く。
- どの外部画面を想定しているか、何のために遷移してきたかを 1〜2 文で示す。
- 「前の画面へ戻る」「プロトタイプへ戻る」「次の画面へ進む」のような最小限の導線だけを置く。
- 外部画面内の複雑な業務ロジックや詳細 UI は再現しない。

## 報告時に含めること

- 実装した画面と、モックで受けた画面の一覧
- `pnpm dev` で確認できる導線
- Storybook で確認できる状態差分
- UX 文書から見て仮置きにした箇所
- 本実装で API や外部連携が必要になる見込み箇所

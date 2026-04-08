# FDA 共通原則

この文書は、TanStack Start や Next など framework ごとの差分をまたいで守る、Feature Driven Architecture ベースの共通原則をまとめる。
ディレクトリ名は repo ごとに違ってよいが、まずはこの文書の責務へ写像してから配置を決める。

## 適用優先順位

1. 対象 repo に明示されている frontend ディレクトリ構成ルール
2. 対象 framework の profile
3. この文書の共通原則

repo 固有ルールが見つかった場合は、それを最優先とする。
この文書は「どこに何を置くべきか」を考える補助線であり、repo の合意済み構成を上書きするために使わない。

## レイヤーの責務

### 1. routing layer

- URL、route 定義、loader / prefetch、layout、metadata、framework 固有の route hook を置く。
- 画面表示は page composition layer へ委譲し、自分では feature UI を組み立てない。
- 例:
  - TanStack Start の `src/routes`
  - Next App Router の `src/app`

### 2. page composition layer

- 複数 feature を組み合わせて 1 画面を構築する。
- 画面固有の layout 組み立て、section 配置、画面単位の軽い orchestration を担う。
- ここへ置くのは「画面としての組み立て」であり、再利用される業務ロジック、永続的な状態、feature 専用 UI は feature 側へ戻す。
- 例:
  - TanStack Start の `src/pages`
  - Next App Router の `src/screens` または repo 既存の `views/`

### 3. feature context layer

- ユーザー価値やユースケース単位のまとまりを置く。
- feature 外へ見せる契約は `index.ts` に集約し、内部構造は閉じ込める。
- context を切る場合は `src/features/<context>/<feature>`、切らない場合は `src/features/<feature>` とする。
- 同一 context で共通に使う type や helper は `shared/` に寄せる。

### 4. global shared layer

- project 全体で使う汎用 UI、汎用 helper、共通 type を置く。
- domain 固有の用語や feature 専用状態を持ち込まない。
- `shared/ui` は dumb component を基本とし、feature 固有の振る舞いは受け取った props に閉じ込める。

### 5. infra layer

- 外部 API 通信、server function、server action、request / response adapter など外部境界の処理を置く。
- React component を置かない。
- framework 固有の HTTP endpoint 実装は profile 側のルールに従う。

## 依存方向

- `routing layer -> page composition layer -> feature context layer -> shared / api`
- `feature context layer -> context shared -> global shared / api`
- `global shared layer` は feature を import しない。
- `infra layer` は page composition や feature UI を import しない。
- 別 feature の内部ファイルへ deep import しない。必要な依存は相手 feature の `index.ts` を経由する。
- 2 つ以上の feature から同じ内部 helper を参照したくなったら、context `shared/` か global `shared/` へ引き上げる。

## feature 内の基本構成

`src/features/<context>/<feature-name>/` または `src/features/<feature-name>/` の配下では、必要なディレクトリだけを作る。
空の箱を先回りで全部作らない。

- `components/`
  - この feature 専用の UI component
- `hooks/`
  - React hook。UI と状態や副作用の橋渡しを行う
- `helpers/`
  - React へ依存しない純粋関数
- `providers/`
  - Prop Drilling を避けるための Context Provider
- `queries/`
  - React Query など client cache を使う async state
- `schemas/`
  - Zod などの validation schema
- `stores/`
  - Zustand などの local state
- `types/`
  - feature 内に閉じる type
- `index.ts`
  - page composition layer や他 feature に公開する public API

## 命名と export の原則

- 画面や feature の主役になる component は、役割が分かる PascalCase 名を使う。
- `index.ts` には外部利用を許可する component、hook、type だけを export する。
- feature 内部でしか使わない helper や type を、惰性で `index.ts` へ流さない。
- 1 つの file に責務を詰め込みすぎたら、`helpers/` `hooks/` `components/` へ分解して public API を保つ。

## repo 固有ルールがあるときの扱い

- `docs/frontend.md` `README.md` `AGENTS.md` `architecture` 文書などに既存ルールがあるなら、その命名と tree を優先する。
- この文書の役割は、名前を揃えることではなく責務分離を崩さないことにある。
- たとえば repo 既定が `src/views` なら、`page composition layer = views` と読み替えてよい。
- 逆に、repo 固有ルールが route file へ重い UI と状態を詰め込む構成なら、そのまま踏襲するのではなく、どの責務を切り出すかを報告に明示する。

## コメント方針

- 新規追加した関数、クラス、複雑な処理には、保守時に意図が追える短い日本語コメントを付ける。
- コメントは「何をしているか」より「なぜその置き場や分岐が必要か」を優先する。

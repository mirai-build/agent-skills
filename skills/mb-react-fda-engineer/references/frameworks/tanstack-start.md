# TanStack Start プロファイル

この文書は TanStack Start を対象にするときの標準構成と責務分離を定義する。
対象 repo に既存の frontend ディレクトリルールがある場合はそれを優先し、この文書は不足部分の補助線として使う。

## 標準ディレクトリ構成

repo 固有ルールがまだなく、TanStack Start で FDA 構成を導入または整理したい場合は、次を既定の正本とする。
この既定構成を採用した場合は、対象 repo の `README.md` にも同じ構成と利用ライブラリ方針を明記する。

```text
src/
├── api/                        # 【インフラ層】外部通信やサーバー関数 (fetch の純関数, createServerFn)
│   ├── products.ts             # 例: fetchProducts, createProduct
│   └── cart.ts                 # 例: addToCartRequest
│
├── routes/                     # 【ルーティング層】URL 定義・loader での事前データフェッチ (表示責務なし)
│   ├── __root.tsx
│   ├── index.tsx               # / (pages/home/HomePage をレンダリング)
│   └── products/
│       ├── index.tsx           # /products (pages/products/ProductListPage をレンダリング)
│       └── $productId.tsx      # /products/:productId
│
├── pages/                      # 【ページ構成層】複数の Feature を組み合わせて「画面」を構築
│   ├── home/
│   │   └── HomePage.tsx
│   └── products/
│       ├── ProductListPage.tsx
│       └── ProductDetailPage.tsx
│
├── features/                   # 【機能コンテキスト層】境界付けられたコンテキスト
│   ├── products/               # 📦 コンテキスト: 商品
│   │   ├── shared/             # コンテキスト内の共通資産
│   │   │   ├── types/          # 商品共通の型
│   │   │   └── helpers/        # 商品共通の純粋関数
│   │   ├── product-list/       # 🚀 機能: 商品一覧
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── queries/
│   │   │   ├── schemas/
│   │   │   ├── stores/
│   │   │   └── index.ts
│   │   ├── product-creation/   # 🚀 機能: 商品作成
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── queries/
│   │   │   ├── schemas/
│   │   │   └── index.ts
│   │   └── index.ts            # pages に公開する feature の入口を集約
│   └── cart/                   # 🛒 コンテキスト: カート
│       ├── shared/
│       │   ├── types/
│       │   └── helpers/
│       ├── add-to-cart-button/ # 🚀 機能: カート追加ボタン
│       │   ├── components/
│       │   ├── queries/
│       │   ├── schemas/
│       │   └── index.ts
│       └── index.ts
│
├── shared/                     # 【グローバル共有層】project 全体で使う汎用資産
│   ├── ui/                     # 汎用 Dumb UI
│   ├── helpers/                # 共通ユーティリティ
│   └── types/                  # グローバルな型定義
│
├── router.tsx                  # TanStack Router の設定・インスタンス生成
├── client.tsx                  # クライアントサイドのエントリーポイント
└── ssr.tsx                     # サーバーサイドのエントリーポイント
```

## 各層の扱い

### `src/api`

- 外部 API との通信、`createServerFn`、request helper を置く。
- React component や page composition を置かない。
- TanStack Query を使う場合も、query function 自体はここか feature の `queries/` から参照できる pure function として切り出す。

### `src/routes`

- route file は URL 定義、loader、beforeLoad、pending、error など routing 起点の責務だけを持つ。
- 画面 UI は `src/pages` へ委譲し、route file 自体は page component を返す薄い entrypoint として保つ。
- route file に feature 専用 UI の組み立てや複雑な state 管理を書き込まない。

### `src/pages`

- 画面単位の section 構成、layout 組み立て、複数 feature の並び順を決める。
- 再利用可能なロジックは feature へ戻す。
- route file から import されることを前提に、URL 固有の事情は page へ持ち込みすぎない。

### `src/features`

- 1 つの feature の public API は `index.ts` に集約する。
- `components/` `hooks/` `queries/` `schemas/` `stores/` などは必要な分だけ作る。
- context `shared/` は、その context 内の複数 feature で共有する type や helper に限定する。
- repo 規模が小さく context を切る必然が弱い場合は、`src/features/<feature>` の flat 構成も許容する。判断は [`../context_partitioning.md`](../context_partitioning.md) を使う。

### `src/shared`

- domain 非依存の UI や helper を置く。
- feature 専用 component や domain noun を持ち込まない。

## 利用ライブラリ方針

TanStack Start profile では、次を既定の利用ライブラリ方針とする。
ただし、既存 repo に別方針がある場合や新規導入が必要な場合は、実装前にユーザーへ確認する。

- React Query
  - 必須。server / client をまたぐ data fetching と cache の標準手段として扱う。
- React Hook Form + `@hookform/resolvers`
  - form が 1 つでもある project では必須。
- zod
  - React Hook Form を入れる場合は必須。schema を form validation の正本にする。
- TanStack Table
  - table が多い project では必須。
- Zustand
  - micro 規模の product 以外では必須。
- Tailwind CSS
  - 必須。
- `shadcn/ui`、MUI などの UI library
  - いずれか 1 つは必須。既定は `shadcn/ui` を第一候補にするが、実際の採用や変更前には必ずユーザーへ確認する。

### 確認ルール

- 既存 repo が同等ライブラリを採用済みなら、まずそれを尊重する。
- 新規導入や移行が必要な場合は、目的、影響範囲、代替案を短く整理してからユーザーへ確認する。
- UI library の選定は見た目だけで決めず、既存 design system、component 資産、チーム運用を見て決める。

## 実装時の注意

- `routes` から feature 内部 file へ deep import せず、`pages` や feature の `index.ts` を経由する。
- 既存 repo に route loader で query prefetch する流儀があるなら、それを踏襲する。
- repo に独自の `ui/` や token 管理ルールがある場合は `shared/ui` をむやみに増やさず、既存規約へ合わせる。

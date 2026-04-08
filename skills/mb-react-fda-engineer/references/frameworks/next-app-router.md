# Next App Router プロファイル

この文書は Next App Router を対象にするときの標準構成と責務分離を定義する。
TanStack Start と同じ発想で layer を分けるが、Next 固有の予約ディレクトリや server / client component の制約を踏まえて置き場を変える。

## 標準ディレクトリ構成

repo 固有ルールがまだなく、Next App Router で FDA 構成を導入または整理したい場合は、次を既定の正本とする。
この既定構成を採用した場合は、対象 repo の `README.md` にも同じ構成と利用ライブラリ方針を明記する。

```text
src/
├── api/                        # 【インフラ層】外部通信、server action、request helper
│   └── products/
│       ├── requests.ts         # 例: fetchProducts, fetchProductById
│       └── actions.ts          # 例: createProductAction
│
├── app/                        # 【ルーティング層】App Router の route segment と layout
│   ├── layout.tsx
│   ├── page.tsx                # screens/home/HomePage をレンダリング
│   ├── products/
│   │   ├── page.tsx            # screens/products/ProductListPage をレンダリング
│   │   └── [productId]/
│   │       └── page.tsx        # screens/products/ProductDetailPage をレンダリング
│   └── api/                    # Route Handler が必要なときだけ使う
│       └── products/
│           └── route.ts
│
├── screens/                    # 【ページ構成層】複数 feature を組み合わせて「画面」を構築
│   ├── home/
│   │   └── HomePage.tsx
│   └── products/
│       ├── ProductListPage.tsx
│       └── ProductDetailPage.tsx
│
├── features/                   # 【機能コンテキスト層】構成方針は TanStack Start と同じ
│   └── products/
│       ├── shared/
│       ├── product-list/
│       ├── product-creation/
│       └── index.ts
│
├── shared/                     # 【グローバル共有層】project 全体で使う汎用資産
│   ├── ui/
│   ├── helpers/
│   └── types/
│
└── middleware.ts               # 必要なときだけ
```

## `src/pages` を使わない理由

Next では `pages/` が framework の予約ディレクトリとして解釈されうるため、TanStack Start と同じ意味で `src/pages` を作ると混乱の原因になる。
この profile では、page composition layer の既定名を `src/screens` とする。

ただし、対象 repo がすでに `src/views` `src/page-components` など別名を採用しているなら、その既存名を優先してよい。
大切なのは名前より責務である。

## 各層の扱い

### `src/app`

- route segment、`page.tsx`、`layout.tsx`、`loading.tsx`、`error.tsx`、`generateMetadata`、route handler など、App Router 固有の責務だけを置く。
- `page.tsx` は `screens` を呼び出す薄い entrypoint として保つ。
- UI の主組み立てや feature orchestration は `screens` へ委譲する。

### `src/screens`

- 1 画面の構成、section 配置、複数 feature の組み合わせを担う。
- route segment 固有の file 名制約から UI を切り離すための置き場として使う。
- `src/pages` の役割を Next 向けに読み替えた layer と考える。

### `src/api`

- 外部 API 通信、server action、request helper を置く。
- `src/app/api` は HTTP endpoint を公開したいときの Route Handler 用であり、外部通信 helper の置き場ではない。
- repo が BFF 的な server function を多用する場合も、UI と混ぜずにこの layer へ寄せる。

### `src/features`

- directory の基本思想は TanStack Start と同じで、feature ごとの `index.ts` を public API にする。
- client state や form state、feature 専用 UI は feature 配下へ閉じ込める。
- context 分割の判断は [`../context_partitioning.md`](../context_partitioning.md) を使う。

## 利用ライブラリ方針

Next App Router profile でも、利用ライブラリの基本方針は TanStack Start と同じとする。
server component を既定にしつつも、project 標準として次を採用候補に置く。
ただし、既存 repo に別方針がある場合や新規導入が必要な場合は、実装前にユーザーへ確認する。

- React Query
  - 必須。
- React Hook Form + `@hookform/resolvers`
  - form が 1 つでもある project では必須。
- zod
  - React Hook Form を入れる場合は必須。
- TanStack Table
  - table が多い project では必須。
- Zustand
  - micro 規模の product 以外では必須。
- Tailwind CSS
  - 必須。
- `shadcn/ui`、MUI などの UI library
  - いずれか 1 つは必須。既定は `shadcn/ui` を第一候補にするが、実際の採用や変更前には必ずユーザーへ確認する。

## server / client component の扱い

- server component を既定とし、本当に必要な場所だけ `"use client"` を付ける。
- browser event、local state、effect が必要な UI は feature の `components/` や `hooks/` へ閉じ込める。
- 単純な server fetch まで無理に client hook 化しない。
- React Query や SWR を repo が採用している場合だけ、feature の `queries/` を使って client cache を管理する。

## 実装時の注意

- `app/page.tsx` へ大きな JSX や複雑な state を書き込まない。
- `app/api/route.ts` と `src/api` の責務を混同しない。
- 既存 repo に `server/` `services/` `lib/` などの置き場がある場合は、その役割を観察して `infra layer` との対応を取ってから実装する。
- UI library や state library の導入・変更が必要な場合は、既存 design system と運用方針を確認したうえでユーザーへ相談する。

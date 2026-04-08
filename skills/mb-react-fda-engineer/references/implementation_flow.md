# 実装フロー

この文書は、既存 repo のルール確認から framework profile の選定、feature 実装、検証、最終報告までの進め方を整理する。
新規 tree を押し付けるのではなく、既存 repo へ責務分離を保った変更を差し込むための手順として使う。

## 1. 既存ルールを棚卸しする

最初に次を軽く確認し、frontend の置き場や命名に明示ルールがあるかを探す。

- `AGENTS.md`
- `README.md`
- `docs/` `ux/` `architecture/`
- `package.json`
- router 設定 file
- 既存の `src/` tree

確認ポイント:

- frontend ディレクトリ構成の明示ルールがあるか
- framework は TanStack Start か Next App Router か
- data fetching、state 管理、form、schema、table、UI の既存採用ライブラリは何か
- route file と page / view file がどう分かれているか

repo 固有ルールが見つかった場合は、それを最優先とする。
この Skill の profile は、ルールが不足する箇所を補うためにだけ使う。
repo 固有ルールが見つからなかった場合は、この Skill の共通原則と framework profile を既定構成として採用し、その内容を対象 repo の `README.md` に残す。

## 2. framework profile を選ぶ

### TanStack Start の手がかり

- `@tanstack/start` を依存に持つ
- `src/routes/` が主 routing tree
- `router.tsx` `client.tsx` `ssr.tsx` がある
- `createFileRoute` や `createRootRoute` が使われている

### Next App Router の手がかり

- `next.config.js` `next.config.mjs` `next.config.ts`
- `src/app/` または `app/`
- `page.tsx` `layout.tsx` `loading.tsx` `error.tsx`
- route handler として `route.ts`

どちらでもない場合は、共通原則までは使えるが framework 固有ルールは未対応として扱い、追加 profile が必要と伝える。

## 2.5. 利用ライブラリ差分を確認する

- profile ごとの必須ライブラリと、対象 repo の既存採用ライブラリを突き合わせる。
- 新規導入や置き換えが必要な場合は、実装前にユーザーへ確認する。
- 特に `shadcn/ui` と MUI のどちらを使うか、Zustand を新規導入するか、form stack を RHF + zod へ寄せるかは独断で決めない。

## 3. context 分割の要否を決める

- まず現状 tree を確認し、すでに `features/<context>/<feature>` か flat feature かを把握する。
- 現状構成を壊す理由が明確でない限り、大きな再編は避ける。
- 新規導入や大きめの追加で判断が必要なときだけ [`context_partitioning.md`](./context_partitioning.md) を使う。
- 判断材料が不足しているなら、ユーザーへ確認する。

## 4. 変更をレイヤーへ割り当てる

変更要求を次のどこへ置くか決める。

- routing layer
  - URL、loader / prefetch、layout、metadata、route handler
- page composition layer
  - 画面組み立て、section 配置
- feature context layer
  - feature UI、hook、store、query、schema
- global shared layer
  - project 全体で使う UI / helper / type
- infra layer
  - 外部通信、server function、server action

「とりあえず route file に置く」「page file に全部書く」を避け、最も狭い責務へ置く。

## 5. 実装する

- 既存の naming、styling、state library、test 配置を踏襲する。
- 新規 directory は必要なものだけ作る。
- feature 外へ見せる契約は `index.ts` へ集約する。
- 別 feature から内部 file を直接参照しない。
- 新しい関数、クラス、複雑な処理には短い日本語コメントを付ける。
- repo 固有ルールが見つからなかった場合は、採用した構成と利用ライブラリ方針を対象 repo の `README.md` に追記する。

## 6. 検証する

- repo 既定の `check` `lint` `test` `build` などから、今回の変更に必要十分なものを選ぶ。
- 既定コマンドが見当たらない場合は、少なくとも型エラーや import 崩れがないかを確認する。
- route 追加や page wiring を行った場合は、最終的な import / export と entrypoint を見直す。

## 7. 最終報告で残すこと

最後の報告では次を短くまとめる。

1. repo 固有の frontend ルールを見つけたか
2. 使った framework profile
3. 利用ライブラリをどう判断したか
4. context 分割をどう判断したか
5. `README.md` へ構成ルールを反映したか
6. 主に触った layer と public API
7. 実施した検証と未実施項目

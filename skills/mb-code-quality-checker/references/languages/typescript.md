# TypeScript ルール

## 使う場面

- TypeScript リポジトリで整形、lint、型検査、テストを通したいとき
- `pnpm lint` `pnpm tsc` `pnpm test` を基本線にしつつ、repo 指定コマンドへ読み替える必要があるとき
- lint error、型エラー、unit test failure をまとめて直したいとき

## コマンドの決め方

### 1. package manager

- `package.json#packageManager` があれば最優先で使う。
- なければ `pnpm-lock.yaml` `package-lock.json` `yarn.lock` `bun.lockb` などの lockfile から推定する。
- それでも決まらない場合だけ pnpm を既定値として扱う。

### 2. 実行コマンド

- lint は `lint` 系 script を最優先する。なければ repo が明示するラッパーコマンドの中から lint を含むものを採用する。
- 型検査は `typecheck` `type-check` `check-types` `tsc` 系 script を優先する。repo 専用 wrapper が型検査を含むならそれでもよい。
- テストは `test` を基本に、repo が `test:unit` `test:ci` などを正式運用しているならその指定を優先する。
- モノレポで root wrapper がある場合は、`turbo run lint` や `nx run-many` のような repo 既定コマンドを優先し、ユーザーが対象 package を指定したときだけ scope を絞る。

### 3. 整形

- `format` `fmt` `lint:fix` `check:fix` などの明示 script があるときだけ使う。
- format script が無い場合は、lint や test を通すために必要な範囲だけ手修正する。
- 整形だけで大量差分が出る場合は、本当に必要な範囲かを確認してから進める。

## 失敗時の直し方

- lint failure は、まず設定違反かロジック不整合かを切り分ける。単純整形で直るのか、実装自体を修正すべきかを見誤らない。
- 型エラーは、型定義、ジェネリクス、戻り値、nullable、import path、ビルド設定のどこが壊れているかを先に絞る。
- テスト failure は、期待値が古いだけなのか、実装退行なのかを見て、安易に snapshot や assertion を更新しない。
- 1 つの修正で複数カテゴリに効く可能性がある場合でも、修正後は lint、型検査、テストを順に再確認する。
- 外部 API、DB、ブラウザ、生成物など環境依存で失敗している場合は、コードの問題と環境の問題を分けて報告する。

## 最終確認の順番

1. repo 既定の format または fix コマンドがあれば先に実行する
2. lint を通す
3. 型検査を通す
4. テストを通す
5. 実際に使ったコマンドと残課題を報告する

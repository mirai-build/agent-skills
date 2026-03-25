---
name: mb-code-quality-checker
description: 言語別ルールを切り替えながら、リポジトリの整形、lint、型検査、テストを通すためのスキル。最初に対象言語を決め、対応する `references/languages/` のルールを読み、package manager、workspace 構成、package.json scripts、CI や補助コマンドを確認して実行順を決める。初版は TypeScript をサポートし、既定では pnpm ベースで進めるが、repo 指定コマンドがある場合はそちらを優先する。
license: Apache-2.0
---

# コード品質チェッカー

対象言語に応じて品質確認ルールを切り替え、整形、lint、型検査、テストが通る状態まで持っていく。
まず言語を決めて対応するルールを読み、次にリポジトリが期待するコマンドを特定し、失敗したら最小限のコード修正を加え、最後に通過した確認コマンドをまとめて報告する。

## 実行原則

- 最初に対象言語を決め、対応する `references/languages/<language>.md` を読む。現在サポートしているのは TypeScript だけで、ほかの言語は未対応として扱う。
- いきなり検証コマンドを打たず、まず `scripts/detect_code_quality_context.py --repo /path/to/repo --language <language> --format json` で package manager、利用可能な script、workspace ヒントを確認する。
- 既定は pnpm を使うが、`package.json#packageManager`、lockfile、CI、`Makefile`、`justfile`、`turbo.json`、`nx.json` などが明示するコマンドを優先する。
- リポジトリが `verify` `check` `ci` のようなラッパーコマンドを明示している場合は、その中身を見て lint、型検査、テストを網羅しているか確認してから採用する。
- 整形は repo 既定の `format` `fmt` `lint:fix` などがあるときだけ自動実行する。明示コマンドがない場合に、独自の formatter コマンドを新規導入しない。
- 失敗時は、まず最初の失敗要因を潰す。無関係な全面整形や大規模リファクタは避ける。
- 修正後は、失敗したコマンドだけで終わらず、少なくともその後段の lint、型検査、テストまで再実行して通過を確認する。
- 依存関係のインストール、コード生成、ブラウザ起動、ネットワークアクセスが必要なら、理由を添えて権限昇格や追加実行を行う。

## 基本フロー

1. ユーザーが対象言語を指定していればそれを使い、未指定なら repo の構成から推定する。現時点で推定先が TypeScript 以外なら、未対応であることを伝えて止まる。
2. `references/languages/<language>.md` を読み、対象言語のコマンド決定ルールと修正方針を取り込む。
3. `scripts/detect_code_quality_context.py --repo /path/to/repo --language <language> --format json` で package manager、scripts、workspace ヒント、推奨コマンドを取得する。
4. `package.json`、lockfile、CI、補助タスク定義を見て、整形、lint、型検査、テストの正規コマンドを決める。
5. repo 既定の fix コマンドがある場合だけ先に整形または自動修正を行う。なければ lint や test のログを見て手作業で最小修正する。
6. 言語ルールに沿って検証コマンドを実行し、失敗したら原因を一つずつ潰して再実行する。
7. 最後に、実際に使った言語ルール、コマンド、修正内容、未実施確認を日本語で簡潔に報告する。

## 言語ルールの切り替え

- 言語ごとの実行ルールは `references/languages/` に置く。
- 新しい言語を追加するときは、まず `references/languages/<language>.md` を追加し、その言語用のコマンド候補を `scripts/detect_code_quality_context.py` に実装する。
- 現在サポートしているのは TypeScript だけなので、最初に `references/languages/typescript.md` を読む。

## 最終報告

最終報告では次をこの順でまとめる。

1. 採用した package manager と実行コマンド
2. 実施した修正の要点
3. lint、型検査、テストの通過結果
4. 権限や環境の都合で未実施の確認

## 同梱スクリプト

- `scripts/detect_code_quality_context.py`: 対象 repo の言語、package manager、利用可能な scripts、workspace ヒント、初期推奨コマンドを JSON またはテキストで返す。
- `references/languages/typescript.md`: TypeScript 用のコマンド選定基準、修正方針、最終確認の順番をまとめる。

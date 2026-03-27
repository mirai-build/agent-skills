---
name: mb-repo-quality-reviewer
description: リポジトリ全体の構造、責務分離、可読性、保守性、テスト容易性、過剰設計を総合評価し、改善優先順位と改善例を日本語で返すレビュー用スキル。最初に軽量棚卸しで repo の構造と言語を把握し、共通評価軸と言語別観点を組み合わせて診断したいときに使う。
license: Apache-2.0
---

# ミライビルド リポジトリ品質レビュワー

リポジトリ全体の構造や責務分離を起点に、コードの綺麗さを多面的にレビューする。
クリーンアーキテクチャ準拠かどうかだけで判断せず、可読性、保守性、設計品質、テスト容易性、過剰設計の有無を総合評価し、改善優先順位まで日本語で返す。

## 実行原則

- 最初に `scripts/detect_repo_review_context.py --repo /path/to/repo --format json` で、対象 repo の言語、主要 manifest、source/test 入口、CI、framework の手がかりを棚卸しする。
- クリーンアーキテクチャ準拠だけで高評価にしない。抽象化や層の多さを無条件に良しとせず、規模に対して妥当かで判断する。
- 小規模 repo ではシンプルさを優先して評価し、「層が少ない」こと自体は減点理由にしない。
- 指摘は減点方式で整理し、各問題点に必ず理由と重要度を付ける。主観だけで終わらせず、根拠となるファイルや構造を示す。
- 各指摘は主軸を 1 つに絞り、同じ問題を複数軸で重複減点しない。
- 既定ではレビュー専用として振る舞い、コード修正や自動整形は行わない。
- 対応言語は v1 では TypeScript と Python とする。未対応言語だけの repo は一般則でレビューし、言語固有の深掘りが未対応であることを明示する。
- `改善例` は必要な場合だけ短く示し、大きな修正コードを毎回出力しない。

## 使う場面

- リポジトリ全体の構造、責務分離、依存関係の整理が妥当かをレビューしたい。
- 単なる lint や test 成否ではなく、保守しやすい構造かどうかを評価したい。
- クリーンアーキテクチャ風の見た目に引きずられず、実用性と過剰設計も含めて診断したい。
- 改善点を重要度付きで並べ、どこから直すべきか優先順位を決めたい。

## 基本フロー

1. `scripts/detect_repo_review_context.py` で repo の構造と言語候補を棚卸しする。
2. [`references/review_methodology.md`](./references/review_methodology.md) を読み、5 軸、減点方式、ランク基準、規模別の見方を確定する。
3. 検出言語に応じて [`references/languages/typescript.md`](./references/languages/typescript.md) と [`references/languages/python.md`](./references/languages/python.md) の該当部分を読む。
4. 主要ディレクトリ、代表的なコード、テスト配置、依存関係を確認し、問題点を重要度付きで整理する。
5. [`assets/templates/review_report.md`](./assets/templates/review_report.md) の形式に沿って、`総合評価` `良い点` `問題点` `改善優先順位` `改善例` を日本語で返す。

## 出力ルール

- `総合評価` ではランクを `A / B / C / D` のいずれかで示す。
- `良い点` は箇条書きで簡潔に示す。
- `問題点` は各項目を `[高]` `[中]` `[低]` で始め、問題内容と「なぜ問題か」を短く必ず添える。
- `改善優先順位` は 1〜3 の番号付きで示し、最も改善効果の高い順に並べる。
- `改善例` は可能な場合だけ、修正コードまたは修正方針を短く示す。
- inline code comment directive はユーザーが明示的に求めたときだけ使う。

## リソース

- [`scripts/detect_repo_review_context.py`](./scripts/detect_repo_review_context.py)
  - repo の言語、manifest、framework、source/test 入口、CI の手がかりを read-only で棚卸しする補助スクリプト。
- [`references/review_methodology.md`](./references/review_methodology.md)
  - 5 軸、減点方式、重要度、ランク基準、根拠の書き方、小規模 repo の評価方針をまとめた共通評価基準。
- [`references/languages/typescript.md`](./references/languages/typescript.md)
  - TypeScript repo で重点的に確認する構造評価観点。
- [`references/languages/python.md`](./references/languages/python.md)
  - Python repo で重点的に確認する構造評価観点。
- [`assets/templates/review_report.md`](./assets/templates/review_report.md)
  - `総合評価 / 良い点 / 問題点 / 改善優先順位 / 改善例` の出力テンプレート。

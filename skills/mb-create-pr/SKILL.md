---
name: mb-create-pr
description: 任意の GitHub リポジトリで PR 作成時に、必須テンプレート、確認結果、スクリーンショットをそろえて日本語で PR を作成するスキル。
---

# ミライビルド PR作成

## 概要

GitHub PR を作成するときに、対象リポジトリのルールを確認したうえで、PR 本文の必須項目、動作確認結果、変更対象 UI のスクリーンショットをそろえる。
PR タイトルは必ず日本語で記載する。
PR の description（本文）は必ず日本語で記載し、この Skill のテンプレートを使用する。
PR コメント、レビューコメントも日本語で記載する。
機能実装、画面改修、コンポーネント追加など画面に変更がある PR は、画面確認後に作成し、スクリーンショット画像を必ず添付する。
スクリーンショット画像はコミットしない。

## 使う場面

- ユーザーが GitHub リポジトリで PR 作成、PR 本文作成、PR テンプレート作成を依頼した。
- 変更済みブランチから GitHub PR を作成する前に、本文と確認結果を標準化したい。
- 手作業で PR を作るユーザーへ、テンプレートと記入手順を渡したい。

## 対象リポジトリの確認

1. `AGENTS.md`、`.github/pull_request_template.md`、`.github/PULL_REQUEST_TEMPLATE/`、README、CI 設定を確認し、リポジトリ固有の PR ルールを優先する。
2. `package.json`、lockfile、Makefile、task runner、既存 CI から、実行すべき検証コマンドを決める。
3. この Skill のテンプレートとリポジトリ固有テンプレートが両方ある場合は、リポジトリ固有の必須項目を落とさず、この Skill の 4 項目も本文に含める。
4. リポジトリ構成を決め打ちしない。開発サーバー、Storybook、コンポーネントカタログ、E2E 環境の有無は対象リポジトリで確認してから使う。

## 必須テンプレート

PR 本文は `assets/pull_request_template.md` を使い、次の 4 項目を必ずすべて埋める。
該当する内容がない場合も空欄にせず、「該当なし（理由: ...）」のように理由を書く。

```markdown
## 対象チケットのリンク
- 

## 変更の概要
- 

## 動作確認（確認内容およびコマンド）
- 確認内容:
- 実行コマンド:
  - 
- 結果:

## スクリーンショット（各画面のスクリーンショット）
- 
```

## 記入手順

1. 対象チケットを確認する。ユーザー依頼、ブランチ名、コミット、関連ドキュメントからチケット URL を探し、不明な場合はユーザーに確認する。
2. 変更の概要は、ファイル名の羅列ではなくユーザーやレビュワーが理解しやすい単位でまとめる。
3. 動作確認には、確認した画面操作、期待結果、実行したコマンド、成功または未実行理由を記載する。実行コマンドは対象リポジトリの package manager、scripts、CI に合わせて選ぶ。
4. 機能実装、画面改修、コンポーネント追加など画面に変更がある場合は、PR 作成前に対象画面をブラウザで確認する。
5. 画面に変更がある場合は、変更対象の各画面、状態、コンポーネントのスクリーンショットを撮影し、PR の description へ必ず添付する。
6. UI 変更がない場合だけ、理由付きで「UI 変更なし」と書く。
7. PR タイトルと description が日本語で記載されていることを確認する。
8. 全項目が埋まっていること、スクリーンショット画像が作業ツリーに含まれていないことを確認してから PR を作成する。

## スクリーンショット取得手順

スクリーンショットは `/tmp/mb-create-pr-screenshots/<リポジトリ名またはブランチ名>/` に保存する。
リポジトリ配下には保存せず、撮影後に `git status --short` で画像ファイルが差分に含まれていないことを確認する。
補助スクリプトを使う場合は、この `SKILL.md` と同じディレクトリにある `scripts/capture_screenshots.mjs` を絶対パスで実行する。
このスクリプトは対象リポジトリのカレントディレクトリから実行し、Playwright は対象リポジトリ側の依存関係から読み込む。

アプリ画面を撮影する例:

```bash
node /path/to/mb-create-pr/scripts/capture_screenshots.mjs \
  --base-url http://localhost:<port> \
  --out-dir /tmp/mb-create-pr-screenshots/<branch-or-ticket> \
  "一覧画面=/items" \
  "詳細画面=/items/123"
```

コンポーネント単体を撮影する場合は、Storybook または確認用ページを起動し、その URL を同じスクリプトへ渡す。

```bash
node /path/to/mb-create-pr/scripts/capture_screenshots.mjs \
  --base-url http://localhost:6006 \
  --out-dir /tmp/mb-create-pr-screenshots/<branch-or-ticket> \
  "対象コンポーネント=/iframe.html?id=component--default"
```

レスポンシブ確認が必要な場合は、PC と SP を分けて撮影する。

```bash
node /path/to/mb-create-pr/scripts/capture_screenshots.mjs \
  --base-url http://localhost:<port> \
  --viewport 390x844 \
  --out-dir /tmp/mb-create-pr-screenshots/<branch-or-ticket>-sp \
  "一覧画面_SP=/items"
```

PR 作成前に画像を GitHub へ添付できない場合は、PR 作成後に GitHub 画面で `/tmp` の画像をスクリーンショット欄またはコメントへアップロードし、生成された Markdown を PR 本文へ反映する。
PR 本文には、撮影対象名、画像の反映状況が分かるように記載する。

## PR 作成フロー

1. `git status --short` で差分を確認し、今回の PR に含める変更だけを把握する。
2. 必要な確認コマンドとブラウザ操作を実行する。画面に変更がある PR は、対象画面の表示と操作を確認してから次へ進む。
3. 変更対象の画面とコンポーネントを洗い出し、画面に変更がある場合はスクリーンショットを必ず撮影する。
4. `/tmp` に日本語の PR description ファイルを作り、`assets/pull_request_template.md` の全項目を埋める。
5. PR タイトルは必ず日本語で、変更内容が分かる短い文にする。
6. `gh pr create --title "<日本語タイトル>" --body-file /tmp/<pr-body>.md` で PR を作成する。必要なら `--draft` を付ける。
7. 作成後、GitHub 上でスクリーンショット欄が空でないことを確認する。画像アップロードが必要な場合は、アップロード後に `gh pr edit --body-file` または GitHub 画面で本文を更新する。

## 最終報告

PR 作成後は、次を日本語で簡潔に報告する。

- PR URL
- 実行した確認コマンドと結果
- スクリーンショットの保存先と、PR 本文への反映状況
- 未実行または未反映がある場合の理由

## リソース

- `assets/pull_request_template.md`: PR 本文の必須テンプレート。
- `scripts/capture_screenshots.mjs`: Codex エージェントが Playwright で画面またはコンポーネントのスクリーンショットを取得するための補助スクリプト。

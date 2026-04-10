---
name: mb-document-downloader
description: 対象 SaaS の文書ページを取得し、Markdown へ変換してローカルリポジトリへ保存するスキル。
license: Apache-2.0
---

# ミライビルド 文書ダウンローダー

対象 SaaS の文書 URL または文書 ID を受け取り、対応 API で本文を取得して Markdown へ保存する。
最初の provider は Confluence とし、CLI では `--provider` で対象 SaaS を切り替えられる前提にそろえる。

この Skill は「SaaS 上の 1 文書を repo 内ドキュメントへ取り込みたい」「一次情報を Markdown 化して Git 管理したい」ときに使う。

## 現在サポートする provider

- `confluence`
  - `ATLASSIAN_TOKEN` を必須で使う。
  - `ATLASSIAN_EMAIL` または `ATLASSIAN_USER_EMAIL` があれば basic 認証、ない場合は bearer 認証を試せる。
  - Cloud ID を渡す運用にも対応する。

## 使う場面

- provider ごとの文書ページを Markdown へ変換し、`docs/` や `knowledge/` 配下へ保存したい。
- 指定文書の最新内容をローカル repo の一次資料として取り込みたい。
- ページ URL は分かるが、API 呼び出しや Markdown 化の手順を毎回手で組みたくない。
- 認証情報は `.envrc` や環境変数にあり、Codex から参照できる前提で作業したい。

## 基本フロー

1. まず入力を確定する。
- 優先して確認するのは `provider`、`文書 URL または文書 ID`、`保存先パス`、`provider 固有の接続情報`。
- URL があるなら、provider 実装で文書 ID やベース URL を抽出できるか確認する。
- 必要な token がシェルへ export 済みかを確認し、未反映なら `set -a; source ./.envrc >/dev/null 2>&1; set +a` のように読み込んでから進める。

2. provider 固有の認証方式を決める。
- Confluence では `ATLASSIAN_EMAIL` または `ATLASSIAN_USER_EMAIL` があれば basic 認証を優先する。
- Confluence の scoped token を使う場合は `--cloud-id` を使い、`api.atlassian.com` 経由へ向ける。
- provider を増やすときは、この段階で必要な環境変数と認証分岐を追加する。

3. 汎用 CLI から取得して保存する。
- 実行には [`scripts/download_document.py`](./scripts/download_document.py) を使う。
- provider は `--provider` で選び、対応する provider モジュールが API 呼び出しと Markdown 変換を担当する。
- 取得した本文は Markdown へ変換し、タイトルとメタデータを先頭に付けて保存する。

4. 完了報告をまとめる。
- 保存先ファイルパス、provider 名、文書 ID、タイトルを短く共有する。
- 認証エラーや URL 解決エラーが出た場合は、足りない引数や環境変数を 1〜2 個に絞って案内する。

## リソース

- [`scripts/download_document.py`](./scripts/download_document.py)
  - provider を選択して、保存処理と共通の Markdown 出力をまとめる入口スクリプト。
- [`scripts/providers/confluence.py`](./scripts/providers/confluence.py)
  - Confluence provider の API 呼び出し、本文変換、文書メタデータ抽出をまとめた実装。
- [`references/confluence_download_workflow.md`](./references/confluence_download_workflow.md)
  - Confluence を使うときの入力値、認証パターン、推奨コマンド例、制約事項をまとめた運用メモ。

## 実行例

Confluence のページ URL から取得する例:

```bash
set -a
source ./.envrc >/dev/null 2>&1
set +a

python3 skills/mb-document-downloader/scripts/download_document.py \
  --provider confluence \
  --page-url "https://example.atlassian.net/wiki/spaces/TEAM/pages/123456789/Page+Title" \
  --output "docs/confluence/page-title.md"
```

Confluence の scoped API token と Cloud ID を使う例:

```bash
set -a
source ./.envrc >/dev/null 2>&1
set +a

python3 skills/mb-document-downloader/scripts/download_document.py \
  --provider confluence \
  --page-id "123456789" \
  --cloud-id "$ATLASSIAN_CLOUD_ID" \
  --site-base-url "https://example.atlassian.net/wiki" \
  --output "docs/confluence/page-title.md"
```

Confluence の basic 認証を明示する例:

```bash
set -a
source ./.envrc >/dev/null 2>&1
set +a

python3 skills/mb-document-downloader/scripts/download_document.py \
  --provider confluence \
  --page-id "123456789" \
  --base-url "https://example.atlassian.net/wiki" \
  --user-email "$ATLASSIAN_EMAIL" \
  --auth-mode basic \
  --output "docs/confluence/page-title.md"
```

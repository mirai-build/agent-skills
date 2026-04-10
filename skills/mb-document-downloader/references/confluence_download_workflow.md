# Confluence provider 運用メモ

`mb-document-downloader` で provider に `confluence` を選ぶときの、迷いやすい入力値、認証、制約を整理したメモ。
SKILL.md には載せすぎたくない補足だけをここへ置く。

## 先に決めること

1. どのページを取るか
- `--page-url` を使うのが最も安全。
- URL に `?pageId=` がある場合も、`/pages/<id>/` 形式の場合も pageId を自動抽出できる。
- URL がなく pageId だけ分かっているときは、`--page-id` に加えて `--base-url` または `--cloud-id` を渡す。

2. どこへ保存するか
- `--output` は必須。
- 既定値は持たせていないので、repo のどこへ置くかを明示してから実行する。
- 例: `docs/confluence/xxx.md`, `knowledge/confluence/xxx.md`

3. どの認証パターンか
- 公式に安定しているのは email + token の basic 認証。
- Cloud の scoped token は `api.atlassian.com/ex/confluence/<cloudId>/...` を使う。
- bearer は環境都合で token 単体運用しているケース向けの逃げ道として残している。

## 推奨の環境変数

- `ATLASSIAN_TOKEN`
  - 必須。Confluence API 呼び出しに使う token。
- `ATLASSIAN_EMAIL`
  - 任意。basic 認証に使うメールアドレス。
- `ATLASSIAN_USER_EMAIL`
  - 任意。`ATLASSIAN_EMAIL` の別名として扱う。
- `ATLASSIAN_CLOUD_ID`
  - 任意。scoped API token を使うときだけ必要。

## 取得の流れ

1. `GET /wiki/api/v2/pages/{id}?body-format=view`
- まず Confluence v2 API で view HTML を直接取りにいく。

2. view HTML が取れない場合だけ async convert API へフォールバック
- `POST /wiki/rest/api/contentbody/convert/async/view`
- `GET /wiki/rest/api/contentbody/convert/async/{asyncId}`

3. HTML を Markdown へ変換
- 見出し、段落、リンク、画像、リスト、引用、コードブロック、表を Markdown へ寄せる。
- 変換しきれない Confluence マクロはプレーンテキスト寄りに落ちることがある。

4. ファイルへ保存
- タイトルを `#` 見出しとして先頭へ置く。
- 既定では pageId / version / source / exported at をメタデータ行として付ける。
- メタデータ不要なら `--skip-metadata` を使う。

## 推奨コマンド例

```bash
python3 skills/mb-document-downloader/scripts/download_document.py \
  --provider confluence \
  --page-url "https://example.atlassian.net/wiki/spaces/TEAM/pages/123456789/Page+Title" \
  --output "docs/confluence/page-title.md"
```

## エラー時の見方

### 401 Unauthorized

次を優先して確認する。

- `ATLASSIAN_TOKEN` が本当に export 済みか
- basic 認証が必要な token なのに `ATLASSIAN_EMAIL` または `--user-email` がない
- scoped token なのにサイト URL 直下へ投げており、`--cloud-id` を渡していない

### page-url から pageId を取れない

次のどちらかへ切り替える。

- `--page-id` を明示する
- `?pageId=` または `/pages/<id>/` を含む URL を渡す

### Markdown が完全にきれいにならない

以下は HTML からの近似変換になる。

- 複雑なレイアウト系マクロ
- 展開パネルや情報パネルの細かな装飾
- Confluence 独自のインタラクティブ要素

必要なら保存後の Markdown を repo 向けに整形する追加ステップを別 Skill や別タスクで行う。

## 公式参照

- Confluence Cloud REST API v2: Get page by id
  - https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/
- Atlassian Developer Guide: Authentication and authorization for developers
  - https://developer.atlassian.com/developer-guide/auth/
- Confluence Cloud scoped API tokens
  - https://support.atlassian.com/confluence/kb/scoped-api-tokens-in-confluence-cloud/

---
name: mb-git-clean-branches
description: マージ済みの Git ブランチを安全に整理するためのスキル。ローカル・リモート両方のブランチを列挙し、既定ではリポジトリのデフォルトブランチを基準に、通常 merge に加えて GitHub 上で merged 済み PR の head SHA 一致も見て削除候補を判定する。完全一致の除外対象ブランチ (`main`, `master`, `staging`, `stage`, `stg`, `develop`, `dev`) と保護対象ブランチを除外し、削除候補と除外対象を一覧化してからユーザーの同意を得て削除するときに使う。
license: Apache-2.0
---

# git ブランチ掃除

マージ済みブランチの掃除を、削除前の確認と同意取得を必ず挟みながら進める。
このスキルは特定リポジトリ向けではなく、任意の Git リポジトリで共通利用する前提で使う。

## 実行原則

- いきなり削除しない。必ず最初に `inspect` を実行して候補を確認する。
- 削除前に、削除候補と除外対象を分けてユーザーへ提示する。
- ユーザーが削除に同意するまで `delete` を実行しない。
- ローカル削除は `git branch -d`、リモート削除は `git push <remote> --delete <branch>` を使う。強制削除の `-D` は使わない。
- 完全一致の除外対象ブランチ `main` `master` `staging` `stage` `stg` `develop` `dev` は常に削除対象から外す。
- `develop-hogehoge` のように除外語を含むだけのブランチは、完全一致ではないので削除対象に含めてよい。
- 基準ブランチを省略したときは、まず GitHub のデフォルトブランチを使う。取得できない場合だけ `origin/HEAD`、さらに取れない場合だけ現在のローカルブランチへフォールバックする。
- GitHub リモートでは `gh` CLI を使って merged 済み PR も確認する。squash merge や rebase merge でも、現在のブランチ先端 SHA が merged PR の head SHA と一致していれば削除候補に含める。
- GitHub の保護ブランチ自動検出は `gh` CLI を使う。使えない場合は警告を伝え、必要なら `--protected-branch` で追加指定してから削除する。

## 基本フロー

1. 対象ディレクトリが Git リポジトリか確認する。
2. `scripts/git_merged_branch_cleanup.py inspect` で削除候補と除外対象を列挙する。
3. 基準ブランチ、警告、削除候補、除外対象を日本語で整理してユーザーへ提示する。
4. ユーザーに、どの対象種別とどのブランチを削除するかを確認する。
5. 同意されたブランチだけ `scripts/git_merged_branch_cleanup.py delete` で削除する。
6. 削除したブランチ、スキップしたブランチ、警告をまとめて報告する。

## inspect の使い方

基本は JSON 出力を使い、Codex 側で要約してユーザーへ見せる。

```bash
python3 scripts/git_merged_branch_cleanup.py inspect \
  --repo /path/to/repo \
  --scope both \
  --format json
```

必要に応じて次を追加する。

- `--scope local`: ローカルだけ調べる。
- `--scope remote`: リモートだけ調べる。
- `--remote upstream`: `origin` 以外のリモートを使う。
- `--base main`: 基準ブランチを明示する。既定のデフォルトブランチ判定を上書きしたいときに使う。
- `--protected-branch release`: 手動で保護対象ブランチを追加する。
- `--detect-provider-protection`: GitHub リモートで `gh` CLI が使えるとき、保護ブランチを自動検出する。

GitHub のデフォルトブランチ取得、merged PR 判定、保護ブランチ検出、リモート削除はネットワークアクセスが必要になりやすい。環境の制約で失敗したら、理由を添えて権限昇格や再実行を行う。

## inspect 結果の読み方

`inspect` の JSON では主に次を見る。

- `local_base` / `remote_base`: 判定に使った基準ブランチ
- `provider_default_branch` / `provider_default_branch_status`: GitHub から見たデフォルトブランチと取得状態
- `provider_merged_pr_branches` / `provider_pr_status`: merged PR を検出できたブランチ名と取得状態
- `candidates`: 削除候補
- `excluded`: 除外対象と除外理由
- `warnings`: 自動判定や GitHub 連携に関する注意点

ユーザーへ見せるときは、少なくとも次を含める。

- 削除候補
- 除外対象
- 除外理由
- merged PR 判定の成否
- 保護ブランチ自動検出の成否
- 基準ブランチ
- 警告

merged PR 判定が失敗した場合は、通常の Git ancestry 判定だけに戻っていることを明示する。保護ブランチ自動検出が失敗した、または未対応ホストだった場合は、その旨を明示し、追加の保護対象ブランチを指定するか確認してから削除へ進む。

## delete の使い方

`delete` には、ユーザーが同意したブランチだけを `scope:branch` 形式で渡す。

```bash
python3 scripts/git_merged_branch_cleanup.py delete \
  --repo /path/to/repo \
  --scope both \
  --format json \
  --branch local:feature/old-a \
  --branch remote:feature/old-a
```

`delete` は内部で再度 `inspect` 相当のチェックを行い、次のブランチは削除しない。

- 除外対象ブランチ
- 未マージブランチ
- merged PR の head SHA と一致しない squash/rebase merge 後の再利用ブランチ
- 現在チェックアウト中のローカルブランチ
- 保護対象ブランチ
- inspect 結果の候補に存在しないブランチ

ユーザーが除外対象の削除を求めた場合は、理由を説明していったん止まり、追加確認を取る。

## 出力のまとめ方

ユーザーへの返答は次の順番でまとめる。

1. 基準ブランチと対象範囲
2. 削除候補
3. 除外対象と理由
4. 警告
5. 削除確認の質問

削除後は次の順番でまとめる。

1. 実際に削除したブランチ
2. スキップしたブランチと理由
3. 残っている警告

## 同梱スクリプト

- `scripts/git_merged_branch_cleanup.py`: 削除候補の列挙と安全な削除を行う。

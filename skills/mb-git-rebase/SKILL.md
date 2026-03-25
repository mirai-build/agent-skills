---
name: mb-git-rebase
description: Git の rebase を安全に進めるためのスキル。対象ブランチを指定して rebase を実行し、コンフリクト時は rebase 先と現在ブランチの変更意図を読み解いて解消する。対象ブランチ未指定時は GitHub の open PR 先を優先し、Bitbucket や PR 自動取得失敗時は `origin/HEAD` とブランチ比較を使って候補を絞り込む。
license: Apache-2.0
---

# git rebase 支援

## 概要

安全確認、rebase 先の決定、`git fetch` による最新化、コンフリクト解消、結果報告までを一貫して進める。
判断が割れる競合は無理に片側へ寄せず、変更意図を整理したうえでユーザーに確認する。

## 実行原則

- いきなり `git rebase` を始めず、まず `scripts/resolve_rebase_context.py` で対象ブランチ、rebase 先候補、作業ツリー状態、進行中 rebase の有無を確認する。
- rebase 先を自動判定したいときは、先に `git fetch <remote> --prune` でリモート追跡参照を更新してから候補を確認する。
- 作業ツリーが dirty なときは、自動で stash しない。現在の変更をどう扱うかをユーザーへ確認してから進める。
- ユーザーが rebase 先ブランチを指定したときは、その指定を最優先する。
- ユーザーが rebase 先を指定していない場合で GitHub の open PR が見つかるときは、PR の base branch を rebase 先に使う。
- Bitbucket では PR 自動取得に固執しない。`origin/HEAD` と比較候補ブランチを見て rebase 先候補を絞り、必要ならユーザーへ確認する。
- rebase 先ブランチは、rebase 開始前に必ず `git fetch <remote> <base_branch>` で最新化する。`origin/main` のようなリモート追跡参照を基準に rebase する。
- コンフリクトは `ours` / `theirs` の機械的な採用で済ませず、rebase 先ブランチと現在ブランチの意図を読んで両立できる形を優先する。
- 意図の優先順位が決め切れないときは一度止まり、ファイル名、rebase 先側の変更意図、現在ブランチ側の変更意図、主な選択肢を日本語で示してユーザーへ判断を仰ぐ。

## 基本フロー

1. `git rev-parse --is-inside-work-tree` で Git リポジトリか確認する。
2. rebase 先を自動判定する必要がある場合は、`git fetch origin --prune` でリモート追跡参照を更新する。
3. `python3 scripts/resolve_rebase_context.py --repo /path/to/repo --remote origin --format json` で状況を取得する。
4. `worktree_dirty` が `true` の場合は、未コミット変更の扱いを確認してから進める。
5. `rebase_in_progress` が `true` の場合は、未解決ファイル一覧を確認し、続きから解消する。新しい rebase を重ねて始めない。
6. `resolved_base` がある場合はそのブランチを使う。`resolved_base` がなく `comparison_candidates` だけがある場合は、`origin/HEAD` と ahead / behind を見て候補を絞り、迷うならユーザーへ確認する。
7. 現在チェックアウト中のブランチが対象でないときは、作業ツリーが安全であることを確認したうえで対象ブランチへ切り替える。
8. `git fetch <remote> <base_branch>` で rebase 先を必ず最新化する。
9. `git rebase <remote>/<base_branch>` を実行する。ローカルにしかない rebase 先を使う必要がある場合だけ、理由を添えてローカル参照へ切り替える。
10. コンフリクトしたら `git status --short` と `git diff --name-only --diff-filter=U` で対象を洗い出し、必要に応じて `git diff --ours -- <file>` `git diff --theirs -- <file>` `git show REBASE_HEAD --stat` などで両側の意図を読む。
11. 解消できたファイルは `git add <file>` して `git rebase --continue` を繰り返す。
12. rebase 完了後は、必要なら影響範囲のテストやビルドを行い、rebase 先、解消した競合、ユーザー確認した判断点、残課題をまとめて報告する。

## rebase 先の決め方

### 1. 明示指定がある場合

ユーザーが `main` や `release/2026-03` のように rebase 先を指定したら、そのまま使う。

```bash
python3 scripts/resolve_rebase_context.py \
  --repo /path/to/repo \
  --remote origin \
  --branch feature/example \
  --base main \
  --format json
```

### 2. GitHub の open PR がある場合

`provider` が `github` のときは、`gh pr list --head <branch>` 相当で open PR を確認する。
PR が 1 件に定まる場合は、その `baseRefName` を rebase 先に使う。

### 3. Bitbucket または PR 自動取得に失敗した場合

Bitbucket は PR 取得に失敗しても止まらず、次の順で候補を絞る。

1. `origin/HEAD` が解決できるなら、そのブランチを第一候補にする。
2. `comparison_candidates` の ahead / behind を見て、`main` `master` `develop` などの近いブランチを確認する。
3. 候補が 1 つに定まらない場合だけ、ユーザーへ確認する。

`comparison_candidates` は、対象ブランチとリモート追跡ブランチの差分量を見て、比較しやすい順に並べている。

## コンフリクト解消の進め方

- まず `git status` と未解決ファイル一覧から、どのファイルが競合したかを把握する。
- 競合ファイルごとに、rebase 先ブランチで何を変えたか、現在ブランチで何を変えたかを commit message や diff から要約する。
- 両方の意図を両立できるなら、片側採用ではなく統合案を作る。
- 生成物や lock file で意図が読みづらい場合は、関連する設定ファイルや manifest 側の意図を先に確認する。
- 迷う場合は、少なくとも次を含めてユーザーへ確認する。

```text
ファイル: path/to/file
rebase 先の変更意図: 〜〜
現在ブランチの変更意図: 〜〜
主な選択肢: 〜〜
```

## 出力のまとめ方

ユーザーへの最終報告は次の順で簡潔にまとめる。

1. どのブランチをどこへ rebase したか
2. rebase 先をどう決めたか
3. `git fetch` で最新化したこと
4. 解消した競合ファイルと要点
5. ユーザーへ確認した判断点
6. 未実施テストや残課題

## リソース

- `scripts/resolve_rebase_context.py`: rebase 前の前提情報を JSON またはテキストで返す。GitHub では open PR の base branch を試し、Bitbucket や取得失敗時は `origin/HEAD` と比較候補ブランチを返す。

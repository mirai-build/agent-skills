# agent-skills

このリポジトリは、弊社のエンジニアが共用できる Codex App 用 Agent Skills を配置するためのリポジトリです。
再利用したい Skill を Git で管理し、ローカル環境や他リポジトリへ導入しやすい形で保管します。

## 同梱スキル

- `skill-creator`
  - 表示名は `スキルクリエイター` です。
  - Codex Skill の作成と更新を支援する Skill です。
  - 明確な指示がない限り、Skill 本文や関連ドキュメントを日本語で作成する前提にカスタマイズしています。
- `git-clean-merged-branches`
  - マージ済み Git ブランチの候補確認と安全な削除を支援する Skill です。
  - `skills/git-clean-merged-branches/` に同梱しています。

## ディレクトリ構成

- `skills/`: 配布対象の Skill 本体を配置します。
- `scripts/install_skills.py`: このリポジトリ内の Skill をインストールするためのスクリプトです。

## インストール方法

### 1. ローカル home へインストールする

Codex App に自動検出させたい場合は、home 配下へインストールします。
インストール先は `$CODEX_HOME/skills`、`CODEX_HOME` が未設定のときは `~/.codex/skills` です。

```bash
python3 scripts/install_skills.py --mode home --skill skill-creator --skill git-clean-merged-branches
```

すべての Skill をまとめてインストールする場合:

```bash
python3 scripts/install_skills.py --mode home --all
```

home へインストールしたあとは、Codex App を再起動して Skill を読み込んで下さい。

### 2. 他リポジトリへインストールする

他リポジトリの `skills/` 配下へコピーして、リポジトリと一緒に管理したい場合はこちらを使います。

```bash
python3 scripts/install_skills.py --mode repo --repo-path /path/to/target-repo --skill git-clean-merged-branches
```

すべての Skill をまとめてインストールする場合:

```bash
python3 scripts/install_skills.py --mode repo --repo-path /path/to/target-repo --all
```

repo へのインストールは、共有やバージョン管理を目的とした運用向けです。
Codex App の自動検出は通常 home へのインストールが前提なので、repo へ配置した Skill は対象リポジトリ側の運用に応じて明示参照して下さい。

### 3. インストール対象を一覧表示する

```bash
python3 scripts/install_skills.py --list
```

## 補足

- インストーラは別 Skill として増やさず、決定的に動作するスクリプトとして提供しています。
- 新しい Skill を追加したら `skills/` 配下へ配置し、必要に応じてこの README の一覧と導入例も更新して下さい。

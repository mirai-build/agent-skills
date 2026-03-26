# agent-skills

このリポジトリは、弊社のエンジニアが共用できる Codex App 用 Agent Skills を配置するためのリポジトリです。
再利用したい Skill を Git で管理し、ローカル環境や他リポジトリへ導入しやすい形で保管します。

## 同梱スキル

- `skill-creator`
  - 表示名は `スキルクリエイター` です。
  - Codex Skill の作成と更新を支援する Skill です。
  - 明確な指示がない限り、Skill 本文や関連ドキュメントを日本語で作成する前提にカスタマイズしています。
- `mb-git-clean-branches`
  - 表示名は `ミライビルド gitブランチ掃除` です。
  - マージ済み Git ブランチの候補確認と安全な削除を支援する Skill です。
  - `skills/mb-git-clean-branches/` に同梱しています。
- `mb-git-rebase`
  - 表示名は `ミライビルド git rebase` です。
  - GitHub の PR 先判定と Bitbucket 向けの比較候補提示を使い、安全な rebase と競合解消を支援する Skill です。
  - `skills/mb-git-rebase/` に同梱しています。
- `mb-ddd-architect`
  - 表示名は `ミライビルド DDDアーキテクト` です。
  - DDD に沿って不足情報を質問しながら、`docs/designs/` 配下の設計書を段階的に整備する Skill です。
  - `skills/mb-ddd-architect/` に同梱しています。
- `mb-ddd-architect-reviewer`
  - 表示名は `ミライビルド DDD設計レビュワー` です。
  - 一般的な DDD の戦略設計・戦術設計の観点から、`docs/design/` または `docs/designs/` の設計書をレビューし、過不足、重大リスク、改善優先度を整理する Skill です。
  - `skills/mb-ddd-architect-reviewer/` に同梱しています。
- `mb-ddd-backend-engineer`
  - 表示名は `ミライビルド DDD バックエンドエンジニア` です。
  - DDD 設計書を基に、TypeScript モノレポの `packages/core` `packages/db` `apps/api` へバックエンド実装を落とし込む Skill です。
  - 初版は `core: TypeScript` `db: Prisma` `api: NestJS` をサポートし、`skills/mb-ddd-backend-engineer/` に同梱しています。
- `mb-code-quality-checker`
  - 表示名は `ミライビルド コード品質チェッカー` です。
  - 言語別ルールで整形、lint、型検査、テストの実行コマンドを見極め、失敗時はコード修正まで進める Skill です。
  - 初版は TypeScript をサポートし、`skills/mb-code-quality-checker/` に同梱しています。

## ディレクトリ構成

- `skills/`: 配布対象の Skill 本体を配置します。
- `scripts/install_skills.py`: このリポジトリ内の Skill をインストールするためのスクリプトです。

## インストール方法

### 1. ローカル home へインストールする

Codex App に自動検出させたい場合は、home 配下へインストールします。
インストール先は `$CODEX_HOME/skills`、`CODEX_HOME` が未設定のときは `~/.codex/skills` です。

```bash
python3 scripts/install_skills.py --mode home --skill skill-creator --skill mb-git-clean-branches --skill mb-git-rebase --skill mb-ddd-architect --skill mb-ddd-architect-reviewer --skill mb-ddd-backend-engineer --skill mb-code-quality-checker
```

すべての Skill をまとめてインストールする場合:

```bash
python3 scripts/install_skills.py --mode home --all
```

home へインストールしたあとは、Codex App を再起動して Skill を読み込んで下さい。

### 2. 他リポジトリへインストールする

他リポジトリの `skills/` 配下へコピーして、リポジトリと一緒に管理したい場合はこちらを使います。

```bash
python3 scripts/install_skills.py --mode repo --repo-path /path/to/target-repo --skill mb-git-clean-branches --skill mb-git-rebase --skill mb-ddd-architect --skill mb-ddd-architect-reviewer --skill mb-ddd-backend-engineer --skill mb-code-quality-checker
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
- 新しい Skill には必ず `license.txt` を追加し、`SKILL.md` の frontmatter に `license` を記載して下さい。

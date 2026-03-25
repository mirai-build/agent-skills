---
name: skill-creator
description: Codex App 用の Skill を新規作成または更新するためのガイド。再利用できる手順、スクリプト、参照資料、アセットを整理し、`SKILL.md` と `agents/openai.yaml` を含む Skill を整備するときに使う。Skill 作成、Skill 更新、社内向け Skill 化、Skill テンプレート整備、Skill の運用改善を依頼されたときに使う。
---

# スキルクリエイター

Codex が再利用しやすい Skill を、ぶれない手順で作成または更新する。
このリポジトリ向けに、明確な指示がない限り Skill 本文と関連ドキュメントを日本語で作る前提へ調整している。

## 基本原則

- Skill 本文、参照資料、UI 向け説明文は、明確な指示がない限り日本語で作成する。
- Codex はすでに多くを知っている前提で、SKILL.md には非自明で再利用価値の高い情報だけを書く。
- 手順が壊れやすい作業はスクリプト化し、説明だけでは再現がぶれる処理を減らす。
- 詳細資料は `references/` に逃がし、SKILL.md は中核フローだけに絞る。
- 出力に必要なテンプレートや画像は `assets/` に置き、説明資料と混在させない。
- Skill ディレクトリには、運用上必須でない補助ドキュメントを増やさない。`README.md` や `CHANGELOG.md` は原則作らない。
- 新しく追加する関数、クラス、複雑な処理には、保守時に意図が追える短いコメントや docstring を付ける。

## 標準フロー

1. ユーザーがどんな依頼でその Skill を使うのか、具体例とトリガーを先に固める。
2. その依頼を繰り返し処理するときに、`scripts/` `references/` `assets/` のどれが再利用資産として必要かを決める。
3. 出力先を決める。社内共有リポジトリへ入れるならリポジトリ直下の `skills/`、個人の Codex 環境へ自動検出させるなら `$CODEX_HOME/skills`、未設定なら `~/.codex/skills` を使う。
4. 新規 Skill は `scripts/init_skill.py` で初期化する。既存 Skill 更新ならこの工程を飛ばしてよい。
5. SKILL.md、`agents/openai.yaml`、必要なリソースを実装する。
6. `scripts/quick_validate.py` で構造を検証する。
7. 難しい Skill は実タスクに近い依頼で forward-test し、指示やリソースを磨く。

## 初期化手順

新規 Skill は必ず `scripts/init_skill.py` を使って土台を作る。

```bash
python3 scripts/init_skill.py my-skill \
  --path /path/to/skills \
  --resources scripts,references \
  --interface display_name="日本語の表示名" \
  --interface short_description="25〜64文字の日本語説明をここに記載します" \
  --interface default_prompt="$my-skill を使って、日本語で Skill を作成または更新して下さい。"
```

初期化時のルール:

- `name` は英小文字、数字、ハイフンだけを使う。
- `display_name` `short_description` `default_prompt` は必ず日本語で指定する。
- `default_prompt` には必ず `$skill-name` を含める。
- `short_description` は 25〜64 文字に収める。
- `scripts/` `references/` `assets/` は必要なものだけ作る。

## `agents/openai.yaml` の扱い

- `agents/openai.yaml` の項目定義は `references/openai_yaml.md` を参照する。
- UI 向け文言は必ず日本語で作る。
- `display_name` は人が一覧で見てすぐ分かる表示名にする。
- `short_description` は短く要点が伝わる説明にする。
- `default_prompt` は 1 文程度で、Skill 名を `$skill-name` 形式で明示する。
- アイコンやブランドカラーは、ユーザーから明示的に指定された場合だけ付ける。
- SKILL.md を更新して UI 文言がずれたら `scripts/generate_openai_yaml.py` で再生成する。

再生成例:

```bash
python3 scripts/generate_openai_yaml.py /path/to/skill \
  --interface display_name="日本語の表示名" \
  --interface short_description="25〜64文字の日本語説明をここに記載します" \
  --interface default_prompt="$skill-name を使って、日本語で Skill を更新して下さい。"
```

## Skill 設計の観点

### SKILL.md

- frontmatter には `name` と `description` だけを書く。
- 本文は命令形または作業指示として書く。
- Skill が発火したあとに必要な判断フローだけを載せる。
- 500 行を大きく超えそうなら `references/` へ分割する。

### scripts/

- 同じ処理を繰り返し書き直しているなら、まずスクリプト化を検討する。
- 実行時に壊れやすい処理や引数の取り回しが複雑な処理は、スクリプトに寄せる。
- 追加したスクリプトは実際に動かして確認する。

### references/

- 読み込みが必要な資料だけを置く。
- API 仕様、ドメイン知識、社内ポリシー、長い判断基準はここへ置く。
- SKILL.md から直接リンクし、必要なときだけ読める構成にする。

### assets/

- 出力にコピーして使うテンプレート、画像、フォント、雛形を置く。
- 説明のための文書ではなく、成果物の素材を置く場所として使う。

## 更新時の観点

- 既存 Skill を更新するときは、まず現在の SKILL.md と `agents/openai.yaml` のずれを確認する。
- 以前の説明をそのまま残すより、今の運用に不要な情報を削ることを優先する。
- プレースホルダーやサンプルファイルを残すなら、残す理由があるかを確認する。不要なら削除する。

## 検証

基本検証:

```bash
python3 scripts/quick_validate.py /path/to/skill
```

確認するポイント:

- frontmatter が正しいか
- `name` が命名規則に沿っているか
- `description` が十分具体的か
- `agents/openai.yaml` の文言が日本語か
- スクリプトやテンプレートが実際に使えるか

## Forward-test

- サブエージェントを使えるときだけ forward-test する。
- 検証時は、答えや想定修正案を漏らさずに実タスクに近い依頼を渡す。
- 失敗したら、説明を足す前にスクリプト化や構造改善で直せないかを先に考える。
- 検証でできた一時成果物は必要に応じて片付け、次の検証へ不要な文脈を持ち込まない。

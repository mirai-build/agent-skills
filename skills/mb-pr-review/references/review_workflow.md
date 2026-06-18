# PRレビュー手順

GitHub PR とローカルブランチ差分のどちらでも、最初に比較対象を固定する。
対象が曖昧なままレビューを始めると指摘の再現性が落ちるため、base、head、差分範囲、読んだガイドを最後に報告できる状態にする。

## 1. 入力を固定する

### GitHub PR

- PR URL、PR 番号、または current branch の PR を特定する。
- `gh pr view <PR> --json url,title,baseRefName,headRefName,files,commits` または GitHub connector で base/head と変更ファイルを確認する。
- local checkout を汚さずに済むなら、`origin/<base>...origin/<head>` や `gh pr diff` の remote diff を優先する。
- head が fork で取得できない場合は、`gh pr diff` と PR files を source of truth にする。

### ローカルブランチ差分

- ユーザー指定の base があればそれを使う。
- 指定がない場合は remote default branch を基準にする。通常は `origin/main` または `origin/develop`。
- `git merge-base <base> <head>` を確認し、merge-base から head までをレビュー対象にする。
- working tree の未コミット差分も対象にする依頼なら、committed diff と working tree diff を分けて見る。

`scripts/collect_review_context.py` は、repo、base、head、変更ファイル、commit、ガイド候補を read-only で集める補助として使える。

```bash
python3 skills/mb-pr-review/scripts/collect_review_context.py \
  --repo /path/to/repo \
  --base origin/main \
  --head HEAD \
  --format markdown
```

## 2. コーディングガイドを読む

レビュー前に、次の順でガイドやプロジェクト固有ルールを探す。

1. `AGENTS.md`
2. `.github/copilot-instructions.md`
3. `.cursor/rules/`
4. `CONTRIBUTING.md`
5. `README.md`
6. `docs/` 配下の `coding` `style` `guide` `規約` `開発` を含む文書
7. package や app 単位の README、設計書、ADR

ガイドと実装が矛盾する場合は、まず実装経路、routing、permission、model、test、CI 設定を source of truth として確認する。
ただし、ガイド違反として指摘する場合は、どのガイドのどの方針に反しているかを明示する。

## 3. 3パスでレビューする

### 1パス目: P1 候補

- build、import、型、runtime、migration、query、API contract、認証認可、外部連携、日付、timezone、非同期、transaction、cache を見る。
- ユーザー操作、batch、worker、API request など、実際の到達経路を確認する。
- 破綻経路が説明できないものは `P1` にしない。

### 2パス目: P2 候補

- 既存の責務分離、ディレクトリルール、命名、型設計、テスト配置、shared/lib の使い方と比べる。
- 重複、巨大化、過剰抽象化、局所 helper の乱立、状態管理の置き場、例外処理の一貫性を確認する。
- ガイド違反は、保守時に困る理由が説明できるものを中心に指摘する。

### 3パス目: P3・重複・重大度調整

- TODO コメント、未実装の明示、軽微なコメント不足、表記ゆれ、follow-up 化できる点を拾う。
- 同じ根本原因の指摘を統合する。
- `P1` にした指摘を再読し、本当に明確な破綻経路があるか確認する。
- 明らかに未実装で落ちるだけの箇所は `P3` へ下げる。

## 4. 再現性を保つ

- ファイルは path 昇順、差分 hunk の出現順で読む。
- 指摘候補は scratch に残し、3 パス目で重複排除する。
- 根拠行を確認できるまで最終指摘にしない。
- 実行したコマンド、読んだガイド、読めなかった資料を記録する。
- 指摘の順序は `P1`、`P2`、`P3` の順。同じ重大度では影響範囲が広いものを先にする。

## 5. 出力テンプレート

```markdown
指摘事項
- [P1] タイトル
  - 根拠: path/to/file.ts:123
  - 問題: 何が起きるか
  - 理由: なぜ P1/P2/P3 なのか
  - 修正方向: どう直すべきか

確認事項
- レビュー結論が変わる可能性がある質問だけを書く。

確認した範囲
- 比較範囲:
- 読んだガイド:
- 実行したコマンド:
- 実行できなかった検証:
```

指摘がない場合は、`指摘事項はありません` と明記し、確認した範囲と残リスクを短く添える。

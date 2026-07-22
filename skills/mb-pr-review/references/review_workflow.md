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

## 3. 観点別の確認表を作る

変更ファイルを production code、test、設定、migration、document、生成物へ分類する。
生成物や vendor code を除外する場合は、対象と理由を記録する。

各レビュー対象について、scratch に次の確認表を作る。最終回答へ表全体を出す必要はないが、空欄を残したままレビューを終えない。

| ファイル | 正しさ・契約 | 責務分離 | Readable Code | テスト・規約 | 関連実装 |
| --- | --- | --- | --- | --- | --- |
| path/to/file | 済/候補 | 済/候補 | 済/候補 | 済/候補 | 確認した path |

差分 hunk だけで判断せず、変更した関数や class の呼び出し元、呼び出し先、型、test、近接する既存パターンを必要な範囲で読む。

## 4. 全変更ファイルを3パスでレビューする

重大度は探索の入口に使わない。3 パスで候補を収集・検証した後に P0/P1/P2/P3 を付ける。

### 1パス目: 全レンズで候補を集める

path 昇順、差分 hunk の出現順で全ファイルを確認し、次の観点から候補を残す。

- 正しさ・契約: build、import、型、runtime、migration、query、API contract、認証認可、外部連携、日付、非同期、transaction、cache。
- 責務分離・依存境界: [`lenses/responsibility_separation.md`](./lenses/responsibility_separation.md) の全項目。
- Readable Code: [`lenses/readable_code.md`](./lenses/readable_code.md) の全項目。
- テスト容易性・規約: 副作用の分離、mock 境界、test 配置、ガイド違反、仕様追跡性。

この時点では重大度を付けず、観測した事実と根拠行だけを記録する。

### 2パス目: レンズごとに根拠を検証する

- 正しさ・契約では、ユーザー操作、batch、worker、API request など実際の到達経路を確認する。
- 責務分離では、呼び出し元・呼び出し先・既存の配置規則を読み、変更理由、依存方向、所有権、副作用境界を確認する。
- Readable Code では、名前や制御フローを型・実装・call site と照合し、実際に誤読し得るか確認する。
- テスト容易性・規約では、既存 test、近接実装、ガイドの該当箇所を対照根拠にする。

サブエージェントを利用できる場合は、責務分離と Readable Code を別々のトラックへ委譲する。
主担当は正しさ・契約とテスト容易性・規約を確認し、各トラックの結果を反証して統合する。
利用できない場合も各レンズを順番に実行し、確認表へ結果を残す。

### 3パス目: 反証と見落としを確認する

- 確認表を使って全レビュー対象を再走査し、未確認のレンズがないか確認する。
- 候補を否定する既存仕様、test、呼び出し経路、設計上の理由がないか探す。
- 同じ根本原因の候補を統合し、差分外だけの問題や今回の変更で悪化していない問題を除外する。
- 根拠が揃った候補だけに [`severity_policy.md`](./severity_policy.md) を適用する。
- 明らかに未実装で落ちるだけの箇所は、既存機能の破壊でない限り P0/P1 にせず P3 へ下げる。

## 5. 指摘へ昇格させる証拠

候補を最終指摘にするには、原則として次の 4 点を示す。

1. 差分または関連実装で観測した事実
2. 壊れる経路、混在している責務、または誤読できる解釈
3. 実行時または保守時に生じる具体的な影響
4. 問題を解消する最小限の修正境界

次の理由だけでは指摘にしない。

- 行数や関数の長さが大きいという事実だけ。ただし、明示された行数規約への違反は根拠にできる。
- 将来再利用できそう、分割した方がきれい、早期 return の方が好み、という推測や個人差だけ。
- 既存ガイド、近接実装、呼び出し経路、変更影響のいずれでも裏付けられない設計論。

## 6. 再現性を保つ

- ファイルは path 昇順、差分 hunk の出現順で読む。
- 指摘候補と除外理由を scratch に残し、3 パス目で重複排除する。
- 根拠行と関連実装を確認できるまで最終指摘にしない。
- 実行したコマンド、読んだガイド、読めなかった資料を記録する。
- 指摘の順序は P0、P1、P2、P3。同じ重大度では影響範囲が広いものを先にする。

## 7. 出力テンプレート

```markdown
指摘事項
- [P2][責務分離: ポリシーとI/O] タイトル
  - 根拠: path/to/file.ts:123
  - 観測: 差分と関連実装で確認した事実
  - 影響: 実行時または保守時に何が困るか
  - 対照根拠: ガイド、既存パターン、call site、test
  - 修正方向: 問題を解消する最小限の境界

観点別確認結果
- 正しさ・契約: 対象7ファイル、指摘1件
- 責務分離・依存境界: 対象7ファイル、指摘1件
- Readable Code: 対象7ファイル、指摘なし
- テスト容易性・規約: 対象5ファイル、指摘なし、生成物2ファイルを除外

確認事項
- レビュー結論が変わる可能性がある質問だけを書く。

確認した範囲
- 比較範囲:
- 読んだガイド:
- 関連実装:
- 実行したコマンド:
- 実行できなかった検証:
```

指摘がない場合は、最初に `指摘事項はありません` と明記し、観点別確認結果と残リスクを続ける。

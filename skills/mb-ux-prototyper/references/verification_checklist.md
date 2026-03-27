# 検証チェックリスト

`mb-ux-prototyper` で `ux/prototype` を更新したら、少なくとも次を確認する。

## UX 文書との対応

- 画面名、ジャーニー名、主要状態名が `ux/` の文書とそろっているか。
- `04_screen_inventory` にある対象画面が、route または mock として実装されているか。
- `05_navigation_map` の主要遷移が `pnpm dev` 上で追えるか。
- `06_screen_details` の表示責務と操作責務が screen 実装へ反映されているか。

## `pnpm dev` 側の責務

- 通常導線の確認に必要な route がそろっているか。
- 1 画面に状態切り替え UI を詰め込みすぎていないか。
- route 側に業務ロジックや API 前提の処理を持ち込んでいないか。

## Storybook 側の責務

- story がコンポーネント単位ではなく画面単位になっているか。
- `通常` `空状態` `入力・業務エラー` `権限不足` のうち必要な状態を story で確認できるか。
- tab、accordion、selection、dialog など local state で変わる見た目を story で再現できるか。

## ローカル完結性

- API 呼び出しや外部通信が入っていないか。
- fixture や local state だけで画面表示が成立しているか。
- 認証、外部連携、ファイル入出力を前提にした動作が残っていないか。

## 外部画面モック

- 外部システムや対象外画面への遷移先が、簡易モックで途切れずにつながっているか。
- モック画面であることが明示されているか。
- 戻り先または次アクションが最低限用意されているか。
- 本来の外部画面実装まで作り込みすぎていないか。

## UI 実装方針

- Tailwind CSS v4 の token と utility の使い方が画面間でぶれていないか。
- Radix と shadcn の採用が必要最低限に留まっているか。
- `Sidebar` などのレイアウト骨格を shadcn 既製コンポーネントへ依存しすぎていないか。

## Build Web Apps plugin 活用

- 見た目の方向性を新たに決めた画面では、`build-web-apps:frontend-skill` の visual thesis と interaction thesis が実装へ反映されているか。
- route、screen、story の実装で、`build-web-apps:react-best-practices` に反する重い state 配置や不要な再レンダリングを増やしていないか。
- shadcn を追加または更新した場合、`build-web-apps:shadcn` に沿って既存 component、alias、Tailwind 設定を確認したか。
- ユーザーが UI レビューを求めた場合、`build-web-apps:web-design-guidelines` を使って変更箇所を見直したか。
- ユーザーが共有用 URL を求めた場合、`build-web-apps:deploy-to-vercel` で preview deploy する前提を維持しているか。

## 保守性

- 新規追加した関数、クラス、複雑な処理に短い日本語コメントが付いているか。
- fixture、mock、story、screen の責務が混ざっていないか。
- ファイル名や directory 名から役割を追えるか。

## 最終共有

- 作成または更新した主要ファイルを共有したか。
- `pnpm dev` で確認してほしい導線と、Storybook で確認してほしい状態を分けて伝えたか。
- 仮置き、未対応、今後 API 実装が必要な箇所を明示したか。

# TypeScript 構造評価観点

## 主に見るポイント

- monorepo の package 境界が整理されているか
- feature 単位または責務単位でディレクトリが分かれているか
- 型定義と実装の責務が混線していないか
- フロント、バックエンド、共有コードの境界が崩れていないか
- DI や interface が規模に対して過剰でないか
- barrel export や import 方向が依存関係を分かりにくくしていないか
- テストが対象コードの近くにあり、差し替えしやすい形になっているか

## 典型的な良い状態

- package または app ごとの責務が README なしでもある程度追える
- `src/` 配下が feature か layer のどちらかへ一貫して整理されている
- domain 型、DTO、UI state などが無秩序に混ざっていない
- 外部依存が adapter や client 層へ寄り、業務ロジックから直接参照されにくい

## 典型的な問題

- `shared` `common` `utils` に責務の違うものが集まりすぎている
- interface と実装が 1:1 で大量に並び、実際の差し替え要件が見えない
- barrel export が深く、import 元から依存方向が追いづらい
- フロントエンド用の型と API / DB 由来の型がそのまま混在している
- `index.ts` の多用で依存が循環しやすい
- test が遠く、feature 単位の挙動を追いにくい

## 過剰設計として見やすい例

- 小規模 repo なのに layer が細かく分かれすぎている
- 実装が 1 つしかない interface が大量にあり、保守コストだけ増えている
- factory、builder、service、use case などの抽象名が多い一方で責務の差が曖昧

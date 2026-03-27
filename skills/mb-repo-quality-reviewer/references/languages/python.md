# Python 構造評価観点

## 主に見るポイント

- package 境界と import 方向が整理されているか
- Django / FastAPI / Flask など framework 層と業務ロジックが混線していないか
- settings、ORM model、service、domain logic の責務が適切に分かれているか
- 循環 import や module 間の密結合が強すぎないか
- スクリプトが散在しすぎず、運用用途とアプリ本体が区別できるか
- テストで外部依存を差し替えやすい構造になっているか

## 典型的な良い状態

- package ごとに責務がある程度追える
- framework の request / response 処理と業務ルールが分かれている
- DB 操作や外部 API 呼び出しが薄い gateway や repository 相当へ寄っている
- テストが feature または module 単位でまとまり、fixture の責務も追える

## 典型的な問題

- `utils.py` や `helpers.py` に業務ロジックが集まりすぎている
- settings や環境変数参照が業務コードの各所に散らばっている
- ORM model に業務判断と I/O が密集し、修正影響が大きい
- management script や adhoc script が増え、正規の入口が分かりにくい
- import 循環回避のための局所 import が増え、構造の歪みを隠している

## 過剰設計として見やすい例

- 小規模 service なのに repository、service、use case、adapter を細かく分けすぎている
- 実装が単純なのに抽象 base class や protocol が多く、理解コストが高い
- framework 依存を避けるための層が増えすぎ、逆にデータの流れが読みにくい

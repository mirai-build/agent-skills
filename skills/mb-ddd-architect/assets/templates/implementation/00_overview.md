# 実装設計一覧

> 使い方: `implementation` 配下の入口として最初に作成し、共有 `openapi.yml` と bounded context ごとの DB / 非同期契約設計への導線にする。詳細ドキュメントを追加したら、この一覧も更新する。

## 0. 文書の目的

この文書は、実装向け設計配下の文書を「一覧（概略）→ 詳細」の順で読めるようにし、どの bounded context をどこまで実装設計したかを共有するための正本である。

## 1. この一覧で扱うこと

- 共有 `openapi.yml` に集約した API 設計
- bounded context ごとの DB / 永続化設計
- 実装前に確認が必要な未確定事項

## 2. 共有 API 正本

- `openapi.yml`
- bounded context ごとの API は tag で分ける。

## 3. 対象 Context 一覧

| Context（日本語） | システム英語名 | 実装設計の狙い | 主な入口 | 主な保存対象 | 関連詳細ドキュメント |
| --- | --- | --- | --- | --- | --- |
| [記入] | [記入] | [記入] | [記入] | [記入] | `openapi.yml` `NN_<bounded-context>/00_overview.md` |

## 4. ドキュメント案内

| ドキュメント | 役割 | 更新タイミング |
| --- | --- | --- |
| `openapi.yml` | API 設計の正本。bounded context は tag で区切る | API 設計が更新されたとき |
| `NN_<bounded-context>/00_overview.md` | 1 context 分の実装設計の入口 | 対象 context の API / DB 設計が更新されたとき |

## 5. 未確定事項

- [記入]

# 実装設計概要

> 使い方: 1 つの bounded context ごとに最初に作成し、この context の API / DB 設計の入口にする。カテゴリ一覧へ項目を載せたら、各カテゴリ配下の詳細ドキュメントも必ず作成する。

## 0. 文書の目的

この文書は、対象 bounded context の実装対象、入口、保存対象を一覧で把握し、後続の API / DB 設計文書へつなぐための正本である。

## 基本情報

- Context 名:
- 対応するコンテキスト設計:
- 主な caller:
- 主な保存対象:

## 1. この Context の実装で決めること

- [記入]

## 2. 対象ユースケース

| ユースケース | 利用する Service | 入口 | 保存対象 |
| --- | --- | --- | --- |
| [記入] | [記入] | [記入] | [記入] |

## 3. 関連文書

| ドキュメント | 役割 |
| --- | --- |
| `01_api/00_overview.md` | API 設計の概要と `openapi.yml` への入口 |
| `01_api/openapi.yml` | API 設計の正本 |
| `02_database/00_overview.md` | Mermaid ER 図と table 一覧の入口 |
| `03_async_contracts/00_overview.md` | 必要な場合だけ追加する非同期イベント / Webhook 契約一覧の入口 |

## 4. 未確定事項

- [記入]

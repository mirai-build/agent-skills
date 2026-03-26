# DB / 永続化設計概要

> 使い方: この bounded context の DB 設計概要として、Mermaid の ER 図と table 一覧を整理する。項目を載せたら、各 table の詳細ドキュメントも必ず作成する。

## 0. 文書の目的

この文書は、この bounded context に関係する DB / 永続化設計を、ER 図と table 一覧で把握するための正本である。

## 1. Mermaid ER 図

```mermaid
erDiagram
    [TABLE_A] ||--o{ [TABLE_B] : "[relation]"
```

## 2. Table 一覧

| 物理名 | 役割 | 対応する Aggregate / Repository | 関連詳細ドキュメント |
| --- | --- | --- | --- |
| [記入] | [記入] | [記入] | `01_[table-name].md` |

# UX設計一覧

> 使い方: プロジェクトルートの `ux/` 配下の入口として最初に作成し、どの順で画面構成を深めるかを一覧で把握できるようにする。詳細ドキュメントを追加したら、この一覧も更新する。

## 0. 文書の目的

この文書は、プロジェクトルートの `ux/` 配下の設計を「前提 → 基本構成 → 一覧 → 遷移 → 詳細」の順で読めるようにし、`01_experience_scope` `02_user_journeys` `03_basic_layouts` `04_screen_inventory` `05_navigation_map` `06_screen_details` の整備順を共有するための正本である。

## 1. 整備順

| 段階 | ディレクトリ | 役割 |
| --- | --- | --- |
| 1 | `01_experience_scope/` | `domain_model` の体験スコープ正本へのリンク入口 |
| 2 | `02_user_journeys/` | `domain_model` のジャーニー正本へのリンク入口 |
| 3 | `03_basic_layouts/` | 画面基本構成パターンの整理 |
| 4 | `04_screen_inventory/` | 必要画面の一覧整理 |
| 5 | `05_navigation_map/` | ジャーニー単位の画面遷移整理 |
| 6 | `06_screen_details/` | 1 画面単位の責務と主要状態の整理 |

## 2. ドキュメント案内

| ドキュメント | 役割 | 更新タイミング |
| --- | --- | --- |
| `01_experience_scope/00_overview.md` | 体験スコープの正本を案内する入口 | `domain_model/01_system_purpose` `02_actors` の参照先が変わったとき |
| `02_user_journeys/00_overview.md` | ジャーニーの正本を案内する入口 | `domain_model/04_journeys` の参照先が変わったとき |
| `03_basic_layouts/00_overview.md` | 基本構成配下の入口 | 基本構成パターンの追加、削除、方針見直しが入ったとき |
| `04_screen_inventory/00_overview.md` | 画面一覧配下の入口 | 画面候補の追加、削除、簡単な説明の見直しが入ったとき |
| `05_navigation_map/00_overview.md` | 画面遷移配下の入口 | ジャーニーごとの遷移整理を追加、更新したとき |
| `06_screen_details/00_overview.md` | 画面詳細配下の入口 | 画面詳細の追加、削除、責務見直しが入ったとき |

## 3. 未確定事項

- [記入]

# `agents/openai.yaml` の項目

`agents/openai.yaml` は、Skill の UI 表示や依存関係を定義するための設定ファイルです。
主に Codex App や実行基盤が読み取るためのファイルであり、Skill 本文そのものではありません。

## 全体例

```yaml
interface:
  display_name: "任意の表示名"
  short_description: "任意の短い説明文"
  icon_small: "./assets/icon-small.png"
  icon_large: "./assets/icon-large.svg"
  brand_color: "#3B82F6"
  default_prompt: "$skill-name を使って、ここに短い依頼文を書きます。"

dependencies:
  tools:
    - type: "mcp"
      value: "github"
      description: "GitHub MCP server"
      transport: "streamable_http"
      url: "https://api.githubcopilot.com/mcp/"

policy:
  allow_implicit_invocation: true
```

## 基本ルール

- 文字列値はすべてダブルクオートで囲む。
- キー名はクオートしない。
- `interface.display_name` `interface.short_description` `interface.default_prompt` は人が見る文言なので、日本語で書く。
- `interface.default_prompt` には必ず `$skill-name` を含める。
- `interface.short_description` は 25〜64 文字に収める。
- アイコンやブランドカラーは、必要なときだけ追加する。

## 主な項目

- `interface.display_name`
  - Skill 一覧やチップに出る表示名。
- `interface.short_description`
  - 一覧で素早く内容を把握するための短い説明。
- `interface.icon_small`
  - 小さなアイコン画像の相対パス。
- `interface.icon_large`
  - 大きめのロゴ画像の相対パス。
- `interface.brand_color`
  - UI 補助表示に使う 16 進カラーコード。
- `interface.default_prompt`
  - Skill 起動時に差し込む初期プロンプト。
- `dependencies.tools[].type`
  - 依存ツールの種別。現状は `mcp` を想定する。
- `dependencies.tools[].value`
  - 依存先ツールの識別子。
- `dependencies.tools[].description`
  - 依存の意味を説明する人向け文言。
- `dependencies.tools[].transport`
  - `mcp` 接続の transport 種別。
- `dependencies.tools[].url`
  - MCP サーバー URL。
- `policy.allow_implicit_invocation`
  - `false` のときは自動注入せず、`$skill` で明示呼び出しした場合だけ使う。

## このリポジトリでの推奨

- `display_name` は日本語の表示名を明示する。
- `short_description` は日本語で簡潔に書き、一覧から用途が推測できるようにする。
- `default_prompt` は日本語 1 文を基本にし、Skill をどう使ってほしいかを端的に示す。
- 迷ったら、まず `display_name` `short_description` `default_prompt` だけを確実に整える。

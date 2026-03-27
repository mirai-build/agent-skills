#!/usr/bin/env python3
"""Skill の雛形を作成する。"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

from generate_openai_yaml import write_openai_yaml

MAX_SKILL_NAME_LENGTH = 64
ALLOWED_RESOURCES = {"scripts", "references", "assets"}

SKILL_TEMPLATE = """---
name: {skill_name}
description: [TODO: Skill 一覧で発見されやすいよう、何をする Skill かを平文の日本語で書く。冒頭を他 Skill 名、パス、コマンド、Markdown 記法から始めない]
---

# [TODO: 日本語の表示名を記載する]

## 概要

[TODO: この Skill で何ができるかを 1〜2 文で日本語記載する]

## 使う場面

- [TODO: どんな依頼でこの Skill を使うか]
- [TODO: どんな条件でこの Skill を呼び出すか]

## 基本フロー

1. [TODO: 最初に確認すること]
2. [TODO: 実行の主手順]
3. [TODO: 出力や報告のまとめ方]

## リソース

[TODO: `scripts/` `references/` `assets/` のうち必要なものだけを説明する。不要ならこのセクションを削除する]
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""`{skill_name}` 用のサンプルスクリプト。必要なら実装を置き換える。"""


def main() -> None:
    """この Skill で繰り返し実行したい処理を実装する。"""

    print("{skill_name} のサンプルスクリプトです。")


if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# {skill_title} の参考資料

このファイルは参考資料の置き場所を示すサンプルです。
API 仕様、業務知識、長い判断基準など、必要なときだけ読み込ませたい情報を日本語で記載して下さい。
"""

EXAMPLE_ASSET = """このファイルは assets/ の置き場所を示すサンプルです。
テンプレート、画像、フォント、雛形など、出力物で使う素材に置き換えて下さい。
"""


def normalize_skill_name(skill_name: str) -> str:
    """Skill 名を小文字の hyphen-case へ正規化する。"""

    normalized = skill_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def humanize_skill_name(skill_name: str) -> str:
    """サンプル表示用に、Skill 名のハイフンをスペースへ置き換える。"""

    return skill_name.replace("-", " ")


def parse_resources(raw_resources: str) -> list[str]:
    """`--resources` の値を検証しつつ一覧へ変換する。"""

    if not raw_resources:
        return []

    resources = [item.strip() for item in raw_resources.split(",") if item.strip()]
    invalid = sorted({item for item in resources if item not in ALLOWED_RESOURCES})
    if invalid:
        allowed = ", ".join(sorted(ALLOWED_RESOURCES))
        print(f"[ERROR] 未対応の resource 種別です: {', '.join(invalid)}")
        print(f"利用可能: {allowed}")
        sys.exit(1)

    deduped: list[str] = []
    seen: set[str] = set()
    for resource in resources:
        if resource not in seen:
            deduped.append(resource)
            seen.add(resource)
    return deduped


def create_resource_dirs(
    skill_dir: Path,
    skill_name: str,
    skill_title: str,
    resources: list[str],
    include_examples: bool,
) -> None:
    """必要な resource ディレクトリとサンプルを作成する。"""

    for resource in resources:
        resource_dir = skill_dir / resource
        resource_dir.mkdir(exist_ok=True)

        if resource == "scripts":
            if include_examples:
                example_script = resource_dir / "example.py"
                example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name))
                example_script.chmod(0o755)
                print("[OK] scripts/example.py を作成しました。")
            else:
                print("[OK] scripts/ を作成しました。")
        elif resource == "references":
            if include_examples:
                example_reference = resource_dir / "reference.md"
                example_reference.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title))
                print("[OK] references/reference.md を作成しました。")
            else:
                print("[OK] references/ を作成しました。")
        elif resource == "assets":
            if include_examples:
                example_asset = resource_dir / "example_asset.txt"
                example_asset.write_text(EXAMPLE_ASSET)
                print("[OK] assets/example_asset.txt を作成しました。")
            else:
                print("[OK] assets/ を作成しました。")


def init_skill(
    skill_name: str,
    path: str,
    resources: list[str],
    include_examples: bool,
    interface_overrides: list[str],
) -> Path | None:
    """Skill ディレクトリを初期化し、SKILL.md と openai.yaml を生成する。"""

    skill_dir = Path(path).resolve() / skill_name
    if skill_dir.exists():
        print(f"[ERROR] Skill ディレクトリは既に存在します: {skill_dir}")
        return None

    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"[OK] Skill ディレクトリを作成しました: {skill_dir}")
    except Exception as exc:
        print(f"[ERROR] ディレクトリ作成に失敗しました: {exc}")
        return None

    skill_title = humanize_skill_name(skill_name)
    skill_md_path = skill_dir / "SKILL.md"
    try:
        skill_md_path.write_text(
            SKILL_TEMPLATE.format(skill_name=skill_name)
        )
        print("[OK] SKILL.md を作成しました。")
    except Exception as exc:
        # 初期化に失敗したときは、作りかけの Skill ディレクトリを残さない。
        shutil.rmtree(skill_dir, ignore_errors=True)
        print(f"[ERROR] SKILL.md の作成に失敗しました: {exc}")
        return None

    try:
        result = write_openai_yaml(skill_dir, skill_name, interface_overrides)
        if not result:
            shutil.rmtree(skill_dir, ignore_errors=True)
            return None
    except Exception as exc:
        shutil.rmtree(skill_dir, ignore_errors=True)
        print(f"[ERROR] agents/openai.yaml の作成に失敗しました: {exc}")
        return None

    if resources:
        try:
            create_resource_dirs(skill_dir, skill_name, skill_title, resources, include_examples)
        except Exception as exc:
            shutil.rmtree(skill_dir, ignore_errors=True)
            print(f"[ERROR] resource ディレクトリ作成に失敗しました: {exc}")
            return None

    print(f"\n[OK] Skill '{skill_name}' を初期化しました: {skill_dir}")
    print("\n次の作業:")
    print("1. SKILL.md の TODO を日本語で埋め、frontmatter description は一覧発見向けの平文へ整える")
    if resources:
        if include_examples:
            print("2. サンプルファイルを実装に置き換えるか、不要なら削除する")
        else:
            print("2. 必要な resource を追加する")
    else:
        print("2. 必要になった resource ディレクトリだけ追加する")
    print("3. agents/openai.yaml の日本語 UI 文言を最終確認する")
    print("4. scripts/quick_validate.py で構造を検証する")
    print("5. 複雑な Skill なら実タスクに近い依頼で forward-test する")

    return skill_dir


def main() -> None:
    """CLI エントリーポイント。"""

    parser = argparse.ArgumentParser(
        description="新しい Skill ディレクトリを作成します。",
    )
    parser.add_argument("skill_name", help="Skill 名。自動で hyphen-case に正規化します。")
    parser.add_argument("--path", required=True, help="Skill を作成する親ディレクトリ")
    parser.add_argument(
        "--resources",
        default="",
        help="作成する resource。scripts,references,assets のカンマ区切り",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="選択した resource にサンプルファイルも作成する",
    )
    parser.add_argument(
        "--interface",
        action="append",
        default=[],
        help="openai.yaml 用の値。key=value 形式で複数回指定する",
    )
    args = parser.parse_args()

    raw_skill_name = args.skill_name
    skill_name = normalize_skill_name(raw_skill_name)
    if not skill_name:
        print("[ERROR] Skill 名には英字または数字を 1 文字以上含めて下さい。")
        sys.exit(1)
    if len(skill_name) > MAX_SKILL_NAME_LENGTH:
        print(
            f"[ERROR] Skill 名 '{skill_name}' は長すぎます。"
            f" 最大 {MAX_SKILL_NAME_LENGTH} 文字です。"
        )
        sys.exit(1)
    if skill_name != raw_skill_name:
        print(f"入力値を '{raw_skill_name}' から '{skill_name}' へ正規化しました。")

    resources = parse_resources(args.resources)
    if args.examples and not resources:
        print("[ERROR] --examples を使うときは --resources も指定して下さい。")
        sys.exit(1)

    print(f"初期化する Skill: {skill_name}")
    print(f"作成先: {args.path}")
    if resources:
        print(f"resource: {', '.join(resources)}")
        if args.examples:
            print("サンプルファイル: 作成する")
    else:
        print("resource: 必要になったものだけ後から作成する")
    print()

    result = init_skill(skill_name, args.path, resources, args.examples, args.interface)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()

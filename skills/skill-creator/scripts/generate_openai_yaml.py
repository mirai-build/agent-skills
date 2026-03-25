#!/usr/bin/env python3
"""Skill 用の `agents/openai.yaml` を生成する。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_INTERFACE_KEYS = {
    "display_name",
    "short_description",
    "default_prompt",
}
ALLOWED_INTERFACE_KEYS = REQUIRED_INTERFACE_KEYS | {
    "icon_small",
    "icon_large",
    "brand_color",
}
JAPANESE_PATTERN = re.compile(r"[ぁ-んァ-ン一-龯々ー]")


def yaml_quote(value: str) -> str:
    """YAML へ安全に書き込めるように文字列をエスケープする。"""

    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def parse_frontmatter(content: str) -> dict[str, str] | None:
    """単純な top-level frontmatter キーだけを辞書として抜き出す。"""

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
            value = value[1:-1]
        frontmatter[key] = value
    return frontmatter


def read_frontmatter_name(skill_dir: Path) -> str | None:
    """SKILL.md の frontmatter から Skill 名を読み取る。"""

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"[ERROR] SKILL.md が見つかりません: {skill_md}")
        return None

    content = skill_md.read_text()
    frontmatter = parse_frontmatter(content)
    if frontmatter is None:
        print("[ERROR] SKILL.md の frontmatter 形式が不正です。")
        return None

    name = frontmatter.get("name", "")
    if not name.strip():
        print("[ERROR] frontmatter の name が見つからないか、不正です。")
        return None
    return name.strip()


def parse_interface_overrides(raw_overrides: list[str]) -> tuple[dict[str, str] | None, list[str] | None]:
    """`--interface key=value` を辞書へ変換する。"""

    overrides: dict[str, str] = {}
    optional_order: list[str] = []

    for item in raw_overrides:
        if "=" not in item:
            print(f"[ERROR] interface 指定が不正です: {item}。key=value 形式で指定して下さい。")
            return None, None

        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            print(f"[ERROR] interface 指定の key が空です: {item}")
            return None, None
        if key not in ALLOWED_INTERFACE_KEYS:
            allowed = ", ".join(sorted(ALLOWED_INTERFACE_KEYS))
            print(f"[ERROR] 未対応の interface 項目です: {key}。利用可能: {allowed}")
            return None, None

        overrides[key] = value
        if key not in REQUIRED_INTERFACE_KEYS and key not in optional_order:
            optional_order.append(key)

    return overrides, optional_order


def contains_japanese(text: str) -> bool:
    """日本語文字を含むかどうかを返す。"""

    return bool(JAPANESE_PATTERN.search(text))


def validate_interface_values(skill_name: str, overrides: dict[str, str]) -> bool:
    """このリポジトリの運用ルールに沿って UI 文言を検証する。"""

    missing = sorted(REQUIRED_INTERFACE_KEYS - set(overrides))
    if missing:
        print(
            "[ERROR] このリポジトリでは次の interface 項目が必須です: "
            + ", ".join(missing)
        )
        return False

    for key in REQUIRED_INTERFACE_KEYS:
        value = overrides[key]
        if not contains_japanese(value):
            print(f"[ERROR] interface.{key} は日本語を含めて記載して下さい。")
            return False

    short_description = overrides["short_description"]
    if not (25 <= len(short_description) <= 64):
        print(
            "[ERROR] interface.short_description は 25〜64 文字で指定して下さい。"
        )
        return False

    default_prompt = overrides["default_prompt"]
    required_skill_reference = f"${skill_name}"
    if required_skill_reference not in default_prompt:
        print(
            "[ERROR] interface.default_prompt には "
            f"{required_skill_reference} を含めて下さい。"
        )
        return False

    return True


def write_openai_yaml(skill_dir: Path, skill_name: str, raw_overrides: list[str]) -> Path | None:
    """検証済みの interface 情報から `agents/openai.yaml` を生成する。"""

    overrides, optional_order = parse_interface_overrides(raw_overrides)
    if overrides is None or optional_order is None:
        return None
    if not validate_interface_values(skill_name, overrides):
        return None

    interface_lines = [
        "interface:",
        f"  display_name: {yaml_quote(overrides['display_name'])}",
        f"  short_description: {yaml_quote(overrides['short_description'])}",
        f"  default_prompt: {yaml_quote(overrides['default_prompt'])}",
    ]

    for key in optional_order:
        interface_lines.append(f"  {key}: {yaml_quote(overrides[key])}")

    agents_dir = skill_dir / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    output_path = agents_dir / "openai.yaml"
    output_path.write_text("\n".join(interface_lines) + "\n")
    print(f"[OK] agents/openai.yaml を作成しました: {output_path}")
    return output_path


def main() -> None:
    """CLI エントリーポイント。"""

    parser = argparse.ArgumentParser(
        description="Skill ディレクトリの agents/openai.yaml を生成します。",
    )
    parser.add_argument("skill_dir", help="Skill ディレクトリのパス")
    parser.add_argument(
        "--name",
        help="Skill 名の上書き。未指定時は SKILL.md の frontmatter から読み取ります。",
    )
    parser.add_argument(
        "--interface",
        action="append",
        default=[],
        help="interface の上書き。key=value 形式で複数回指定できます。",
    )
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    if not skill_dir.exists():
        print(f"[ERROR] Skill ディレクトリが見つかりません: {skill_dir}")
        sys.exit(1)
    if not skill_dir.is_dir():
        print(f"[ERROR] ディレクトリではありません: {skill_dir}")
        sys.exit(1)

    skill_name = args.name or read_frontmatter_name(skill_dir)
    if not skill_name:
        sys.exit(1)

    result = write_openai_yaml(skill_dir, skill_name, args.interface)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()

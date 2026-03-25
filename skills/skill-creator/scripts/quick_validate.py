#!/usr/bin/env python3
"""Skill 構造の基本チェックを行う。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

MAX_SKILL_NAME_LENGTH = 64


def parse_frontmatter(content: str) -> dict[str, str] | None:
    """単純な top-level frontmatter を辞書として取り出す。"""

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


def validate_skill(skill_path: str) -> tuple[bool, str]:
    """Skill ディレクトリの最小限の妥当性を検証する。"""

    target = Path(skill_path)
    skill_md = target / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md が見つかりません。"

    content = skill_md.read_text()
    if not content.startswith("---"):
        return False, "YAML frontmatter が見つかりません。"

    frontmatter = parse_frontmatter(content)
    if frontmatter is None:
        return False, "frontmatter の形式が不正です。"

    allowed_properties = {"name", "description", "license", "allowed-tools", "metadata"}
    unexpected_keys = set(frontmatter.keys()) - allowed_properties
    if unexpected_keys:
        allowed = ", ".join(sorted(allowed_properties))
        unexpected = ", ".join(sorted(unexpected_keys))
        return (
            False,
            f"frontmatter に未対応のキーがあります: {unexpected}。利用可能: {allowed}",
        )

    if "name" not in frontmatter:
        return False, "frontmatter に name がありません。"
    if "description" not in frontmatter:
        return False, "frontmatter に description がありません。"

    name = frontmatter.get("name", "")
    name = name.strip()
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            return False, "name は小文字、数字、ハイフンだけで記載して下さい。"
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return False, "name は先頭末尾のハイフンや連続ハイフンを含められません。"
        if len(name) > MAX_SKILL_NAME_LENGTH:
            return (
                False,
                f"name が長すぎます: {len(name)} 文字。最大は {MAX_SKILL_NAME_LENGTH} 文字です。",
            )

    description = frontmatter.get("description", "")
    description = description.strip()
    if description:
        if "<" in description or ">" in description:
            return False, "description に < または > を含めないで下さい。"
        if len(description) > 1024:
            return False, "description が長すぎます。最大 1024 文字です。"

    return True, "Skill は妥当です。"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使い方: python3 quick_validate.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)

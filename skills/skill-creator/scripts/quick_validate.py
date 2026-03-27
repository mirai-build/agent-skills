#!/usr/bin/env python3
"""Skill 構造の基本チェックを行う。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

MAX_SKILL_NAME_LENGTH = 64
DESCRIPTION_PATH_PREFIXES = (
    "skills/",
    "docs/",
    "ux/",
    ".agents/",
    "~/.agents/",
    "~/.codex/",
    "/",
)


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


def collect_description_warnings(description: str) -> list[str]:
    """discovery が不安定になりやすい description を警告として返す。"""

    warnings: list[str] = []
    stripped = description.strip()
    normalized_start = stripped.lstrip('\'"`[(')

    # 冒頭がコード参照やパス始まりだと、一覧発見用テキストとして不安定だった事例がある。
    if stripped.startswith(("`", "$", "[")):
        warnings.append(
            "description の冒頭が Markdown / 参照記法です。"
            " まず『何をする Skill か』を平文の日本語で書くのを推奨します。"
        )
    elif normalized_start.startswith(DESCRIPTION_PATH_PREFIXES):
        warnings.append(
            "description の冒頭がパスや配置名に寄っています。"
            " 他 Skill 名やファイルパスより先に、作業内容を平文で書くのを推奨します。"
        )

    if "](" in stripped or "[" in stripped and "]" in stripped:
        warnings.append(
            "description に Markdown リンク風の記法があります。"
            " frontmatter description は平文中心にして、詳細参照は本文へ移すのを推奨します。"
        )

    code_span_count = stripped.count("`") // 2
    if code_span_count >= 3:
        warnings.append(
            "description に inline code が多めです。"
            " 一覧 discovery を安定させたい場合は、コード風表記を減らして平文へ寄せるのを推奨します。"
        )

    return warnings


def validate_skill(skill_path: str) -> tuple[bool, str, list[str]]:
    """Skill ディレクトリの最小限の妥当性を検証する。"""

    target = Path(skill_path)
    skill_md = target / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md が見つかりません。", []

    content = skill_md.read_text()
    if not content.startswith("---"):
        return False, "YAML frontmatter が見つかりません。", []

    frontmatter = parse_frontmatter(content)
    if frontmatter is None:
        return False, "frontmatter の形式が不正です。", []

    allowed_properties = {"name", "description", "license", "allowed-tools", "metadata"}
    unexpected_keys = set(frontmatter.keys()) - allowed_properties
    if unexpected_keys:
        allowed = ", ".join(sorted(allowed_properties))
        unexpected = ", ".join(sorted(unexpected_keys))
        return (
            False,
            f"frontmatter に未対応のキーがあります: {unexpected}。利用可能: {allowed}",
            [],
        )

    if "name" not in frontmatter:
        return False, "frontmatter に name がありません。", []
    if "description" not in frontmatter:
        return False, "frontmatter に description がありません。", []

    name = frontmatter.get("name", "")
    name = name.strip()
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            return False, "name は小文字、数字、ハイフンだけで記載して下さい。", []
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return False, "name は先頭末尾のハイフンや連続ハイフンを含められません。", []
        if len(name) > MAX_SKILL_NAME_LENGTH:
            return (
                False,
                f"name が長すぎます: {len(name)} 文字。最大は {MAX_SKILL_NAME_LENGTH} 文字です。",
                [],
            )

    description = frontmatter.get("description", "")
    description = description.strip()
    if description:
        if "<" in description or ">" in description:
            return False, "description に < または > を含めないで下さい。", []
        if len(description) > 1024:
            return False, "description が長すぎます。最大 1024 文字です。", []

    warnings = collect_description_warnings(description)
    return True, "Skill は妥当です。", warnings


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使い方: python3 quick_validate.py <skill_directory>")
        sys.exit(1)

    valid, message, warnings = validate_skill(sys.argv[1])
    for warning in warnings:
        print(f"[WARN] {warning}")
    print(message)
    sys.exit(0 if valid else 1)

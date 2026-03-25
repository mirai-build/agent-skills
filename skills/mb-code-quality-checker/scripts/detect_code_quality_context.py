#!/usr/bin/env python3
"""コード品質チェッカー用に、言語別の実行コマンド候補を整理する。"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

IGNORED_DIRS = {
    ".git",
    ".next",
    ".turbo",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "out",
}

PACKAGE_MANAGER_LOCKFILES = {
    "pnpm": "pnpm-lock.yaml",
    "npm": "package-lock.json",
    "yarn": "yarn.lock",
    "bun": "bun.lockb",
}


@dataclass(frozen=True)
class LanguageRuleSet:
    """言語別に探索する script 名の優先順位をまとめる。"""

    format_candidates: tuple[str, ...]
    lint_candidates: tuple[str, ...]
    typecheck_candidates: tuple[str, ...]
    test_candidates: tuple[str, ...]


# 言語ごとの候補はここに寄せ、`references/languages/` の文書と合わせて増やしていく。
LANGUAGE_RULES: dict[str, LanguageRuleSet] = {
    "typescript": LanguageRuleSet(
        format_candidates=(
            "format",
            "fmt",
            "format:fix",
            "lint:fix",
            "check:fix",
            "biome:fix",
            "prettier:write",
            "eslint:fix",
        ),
        lint_candidates=(
            "lint",
            "lint:ci",
            "eslint",
            "biome",
        ),
        typecheck_candidates=(
            "typecheck",
            "type-check",
            "check-types",
            "check:types",
            "tsc",
            "types",
        ),
        test_candidates=(
            "test",
            "test:unit",
            "unit",
            "test:ci",
            "vitest",
            "jest",
        ),
    )
}

WRAPPER_SCRIPT_CANDIDATES = (
    "verify",
    "check",
    "validate",
    "ci",
    "qa",
    "precommit",
)


@dataclass(frozen=True)
class PackageManagerInfo:
    """検出した package manager と根拠を保持する。"""

    name: str
    source: str
    raw_value: str | None


@dataclass(frozen=True)
class CommandRecommendation:
    """各検証段階で最初に試すコマンド候補を表す。"""

    command: str
    source: str
    reason: str


@dataclass(frozen=True)
class DetectionResult:
    """Skill が初手を決めるための repo コンテキストを返す。"""

    repository: str
    language: str
    language_reference: str
    package_json_path: str | None
    package_json_candidates: list[str]
    package_manager: PackageManagerInfo
    workspace_hints: list[str]
    scripts: dict[str, str]
    wrapper_commands: list[CommandRecommendation]
    recommended_commands: dict[str, CommandRecommendation | None]
    notes: list[str]


def load_package_json(package_json_path: Path | None) -> dict[str, Any]:
    """package.json を辞書で返し、読み込めない場合は空辞書にする。"""

    if package_json_path is None:
        return {}

    try:
        return json.loads(package_json_path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def find_package_json_candidates(repo: Path, max_depth: int = 3) -> list[Path]:
    """root 優先で package.json 候補を集める。"""

    candidates: list[Path] = []
    for current_root, dirnames, filenames in os.walk(repo):
        current_path = Path(current_root)
        relative_parts = current_path.relative_to(repo).parts
        depth = len(relative_parts)

        # node_modules など重いディレクトリを先に除外し、探索コストを抑える。
        dirnames[:] = [
            dirname for dirname in dirnames if dirname not in IGNORED_DIRS and depth < max_depth
        ]
        if "package.json" in filenames:
            candidates.append(current_path / "package.json")
        if depth >= max_depth:
            dirnames[:] = []

    return sorted(candidates, key=lambda path: (len(path.relative_to(repo).parts), str(path)))


def choose_package_json(repo: Path, candidates: list[Path]) -> tuple[Path | None, list[str]]:
    """利用する package.json と補足メモを返す。"""

    notes: list[str] = []
    root_package_json = repo / "package.json"
    if root_package_json in candidates:
        return root_package_json, notes
    if len(candidates) == 1:
        notes.append("root package.json は無く、単一の下位 package.json を利用しています。")
        return candidates[0], notes
    if len(candidates) > 1:
        notes.append(
            "複数の package.json が見つかりました。対象 package を決めてからコマンドを確定して下さい。"
        )
    else:
        notes.append("package.json が見つかりません。対象言語の repo か手動確認して下さい。")
    return None, notes


def parse_package_manager_name(raw_value: str) -> str | None:
    """`pnpm@9.0.0` のような指定から manager 名だけを取り出す。"""

    value = raw_value.strip()
    if not value:
        return None
    if "@" in value and not value.startswith("@"):
        return value.split("@", 1)[0]
    return value


def detect_package_manager(repo: Path, package_json: dict[str, Any]) -> PackageManagerInfo:
    """packageManager フィールドと lockfile から package manager を決める。"""

    raw_package_manager = package_json.get("packageManager")
    if isinstance(raw_package_manager, str):
        parsed_name = parse_package_manager_name(raw_package_manager)
        if parsed_name in PACKAGE_MANAGER_LOCKFILES:
            return PackageManagerInfo(
                name=parsed_name,
                source="package.json#packageManager",
                raw_value=raw_package_manager,
            )

    for manager_name, lockfile_name in PACKAGE_MANAGER_LOCKFILES.items():
        if (repo / lockfile_name).exists():
            return PackageManagerInfo(
                name=manager_name,
                source=f"lockfile:{lockfile_name}",
                raw_value=lockfile_name,
            )

    return PackageManagerInfo(name="pnpm", source="default", raw_value=None)


def collect_workspace_hints(repo: Path, package_json: dict[str, Any]) -> list[str]:
    """monorepo や task runner を示すヒントを列挙する。"""

    hints: list[str] = []
    if (repo / "pnpm-workspace.yaml").exists():
        hints.append("pnpm-workspace.yaml")
    if (repo / "turbo.json").exists():
        hints.append("turbo.json")
    if (repo / "nx.json").exists():
        hints.append("nx.json")
    if (repo / "lerna.json").exists():
        hints.append("lerna.json")
    if (repo / ".moon" / "workspace.yml").exists():
        hints.append(".moon/workspace.yml")
    if isinstance(package_json.get("workspaces"), list):
        hints.append("package.json#workspaces")
    return hints


def collect_scripts(package_json: dict[str, Any]) -> dict[str, str]:
    """package.json scripts を文字列辞書として返す。"""

    raw_scripts = package_json.get("scripts")
    if not isinstance(raw_scripts, dict):
        return {}

    scripts: dict[str, str] = {}
    for name, command in raw_scripts.items():
        if isinstance(name, str) and isinstance(command, str):
            scripts[name] = command
    return scripts


def script_command(package_manager: str, script_name: str) -> str:
    """package manager ごとの script 実行形式へ変換する。"""

    if package_manager == "npm":
        return f"npm run {script_name}"
    if package_manager == "yarn":
        return f"yarn {script_name}"
    if package_manager == "bun":
        return f"bun run {script_name}"
    return f"pnpm {script_name}"


def default_stage_command(language: str, package_manager: str, stage: str) -> str | None:
    """repo 指定が無いときの初期コマンドを返す。"""

    defaults: dict[str, dict[str, dict[str, str]]] = {
        "typescript": {
            "pnpm": {
                "lint": "pnpm lint",
                "typecheck": "pnpm tsc",
                "test": "pnpm test",
            },
            "npm": {
                "lint": "npm run lint",
                "typecheck": "npm exec tsc -- --noEmit",
                "test": "npm test",
            },
            "yarn": {
                "lint": "yarn lint",
                "typecheck": "yarn tsc --noEmit",
                "test": "yarn test",
            },
            "bun": {
                "lint": "bun run lint",
                "typecheck": "bunx tsc --noEmit",
                "test": "bun test",
            },
        }
    }
    language_defaults = defaults.get(language, {})
    return language_defaults.get(package_manager, language_defaults.get("pnpm", {})).get(stage)


def choose_script_recommendation(
    scripts: dict[str, str],
    package_manager: str,
    stage: str,
    candidates: tuple[str, ...],
) -> CommandRecommendation | None:
    """候補 script 名から stage ごとの推奨コマンドを選ぶ。"""

    for script_name in candidates:
        if script_name in scripts:
            return CommandRecommendation(
                command=script_command(package_manager, script_name),
                source=f"package.json:scripts.{script_name}",
                reason=f"{stage} 用の script が定義されているため",
            )
    return None


def choose_wrapper_commands(
    scripts: dict[str, str],
    package_manager: str,
) -> list[CommandRecommendation]:
    """verify 系 wrapper command を候補として返す。"""

    wrappers: list[CommandRecommendation] = []
    for script_name in WRAPPER_SCRIPT_CANDIDATES:
        if script_name not in scripts:
            continue
        wrappers.append(
            CommandRecommendation(
                command=script_command(package_manager, script_name),
                source=f"package.json:scripts.{script_name}",
                reason="lint、型検査、テストをまとめて流す wrapper の可能性があるため",
            )
        )
    return wrappers


def choose_recommended_commands(
    language: str,
    scripts: dict[str, str],
    package_manager: str,
) -> dict[str, CommandRecommendation | None]:
    """整形、lint、型検査、テストの初期推奨コマンドを決める。"""

    rule_set = LANGUAGE_RULES[language]
    format_command = choose_script_recommendation(
        scripts,
        package_manager,
        "format",
        rule_set.format_candidates,
    )
    lint_command = choose_script_recommendation(
        scripts,
        package_manager,
        "lint",
        rule_set.lint_candidates,
    )
    typecheck_command = choose_script_recommendation(
        scripts,
        package_manager,
        "typecheck",
        rule_set.typecheck_candidates,
    )
    test_command = choose_script_recommendation(
        scripts,
        package_manager,
        "test",
        rule_set.test_candidates,
    )

    if lint_command is None:
        default_command = default_stage_command(language, package_manager, "lint")
        if default_command is not None:
            lint_command = CommandRecommendation(
                command=default_command,
                source="default",
                reason="lint script が見つからないため、package manager 既定コマンドを使うため",
            )

    if typecheck_command is None:
        default_command = default_stage_command(language, package_manager, "typecheck")
        if default_command is not None:
            typecheck_command = CommandRecommendation(
                command=default_command,
                source="default",
                reason="型検査 script が見つからないため、package manager 既定コマンドを使うため",
            )

    if test_command is None:
        default_command = default_stage_command(language, package_manager, "test")
        if default_command is not None:
            test_command = CommandRecommendation(
                command=default_command,
                source="default",
                reason="test script が見つからないため、package manager 既定コマンドを使うため",
            )

    return {
        "format": format_command,
        "lint": lint_command,
        "typecheck": typecheck_command,
        "test": test_command,
    }


def build_notes(
    language: str,
    package_json_path: Path | None,
    package_manager: PackageManagerInfo,
    workspace_hints: list[str],
    wrapper_commands: list[CommandRecommendation],
    recommended_commands: dict[str, CommandRecommendation | None],
    selection_notes: list[str],
) -> list[str]:
    """Skill 側で追加確認すべきポイントを日本語メモとして返す。"""

    notes = list(selection_notes)
    notes.append(f"言語ルールは references/languages/{language}.md を参照して下さい。")
    if package_json_path is not None:
        notes.append(f"package.json は {package_json_path} を参照しています。")
    if package_manager.source == "default":
        notes.append("package manager を明示できなかったため、既定値として pnpm を提案しています。")
    if workspace_hints:
        notes.append(
            "workspace / task runner のヒントがあります。root wrapper の採用可否を確認して下さい。"
        )
    if wrapper_commands:
        notes.append("verify 系 wrapper command が見つかりました。中身を確認して採用を判断して下さい。")
    if recommended_commands["format"] is None:
        notes.append("整形専用 script は見つかりませんでした。必要な範囲だけ手修正して下さい。")
    return notes


def inspect_repository(repo: Path, language: str) -> DetectionResult:
    """repo 全体を見て、Skill が最初に使う判断材料をまとめる。"""

    candidates = find_package_json_candidates(repo)
    package_json_path, selection_notes = choose_package_json(repo, candidates)
    package_json = load_package_json(package_json_path)
    package_manager = detect_package_manager(repo, package_json)
    workspace_hints = collect_workspace_hints(repo, package_json)
    scripts = collect_scripts(package_json)
    wrapper_commands = choose_wrapper_commands(scripts, package_manager.name)
    recommended_commands = choose_recommended_commands(language, scripts, package_manager.name)
    notes = build_notes(
        language=language,
        package_json_path=package_json_path,
        package_manager=package_manager,
        workspace_hints=workspace_hints,
        wrapper_commands=wrapper_commands,
        recommended_commands=recommended_commands,
        selection_notes=selection_notes,
    )

    return DetectionResult(
        repository=str(repo.resolve()),
        language=language,
        language_reference=f"references/languages/{language}.md",
        package_json_path=str(package_json_path.resolve()) if package_json_path else None,
        package_json_candidates=[str(path.resolve()) for path in candidates],
        package_manager=package_manager,
        workspace_hints=workspace_hints,
        scripts=scripts,
        wrapper_commands=wrapper_commands,
        recommended_commands=recommended_commands,
        notes=notes,
    )


def format_text(result: DetectionResult) -> str:
    """人が読みやすい簡易テキストへ整形する。"""

    lines = [
        f"repository: {result.repository}",
        f"language: {result.language}",
        f"language_reference: {result.language_reference}",
        f"package_json_path: {result.package_json_path or 'not found'}",
        f"package_manager: {result.package_manager.name} ({result.package_manager.source})",
    ]

    if result.workspace_hints:
        lines.append(f"workspace_hints: {', '.join(result.workspace_hints)}")
    if result.package_json_candidates:
        lines.append("package_json_candidates:")
        lines.extend(f"  - {candidate}" for candidate in result.package_json_candidates)

    if result.wrapper_commands:
        lines.append("wrapper_commands:")
        for wrapper in result.wrapper_commands:
            lines.append(f"  - {wrapper.command} [{wrapper.source}]")

    lines.append("recommended_commands:")
    for stage, recommendation in result.recommended_commands.items():
        if recommendation is None:
            lines.append(f"  - {stage}: none")
            continue
        lines.append(f"  - {stage}: {recommendation.command} [{recommendation.source}]")

    if result.notes:
        lines.append("notes:")
        lines.extend(f"  - {note}" for note in result.notes)

    return "\n".join(lines)


def main() -> None:
    """CLI エントリーポイント。"""

    parser = argparse.ArgumentParser(
        description="コード品質チェッカー用の初期コマンド候補を検出します。",
    )
    parser.add_argument("--repo", required=True, help="対象リポジトリのパス")
    parser.add_argument("--language", required=True, help="対象言語。初版は typescript のみ対応")
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="出力形式",
    )
    args = parser.parse_args()

    language = args.language.strip().lower()
    if language not in LANGUAGE_RULES:
        supported = ", ".join(sorted(LANGUAGE_RULES))
        raise SystemExit(
            f"[ERROR] 未対応の言語です: {language}. 現在サポートしているのは {supported} です。"
        )

    repo = Path(args.repo).resolve()
    if not repo.exists():
        raise SystemExit(f"[ERROR] 対象ディレクトリが見つかりません: {repo}")
    if not repo.is_dir():
        raise SystemExit(f"[ERROR] 対象パスはディレクトリではありません: {repo}")

    result = inspect_repository(repo, language)
    if args.format == "json":
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
        return

    print(format_text(result))


if __name__ == "__main__":
    main()

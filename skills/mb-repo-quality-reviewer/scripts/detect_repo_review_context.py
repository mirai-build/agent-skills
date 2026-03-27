#!/usr/bin/env python3
"""リポジトリ品質レビューの初動で使う軽量棚卸し情報を返す。"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
IGNORED_DIRS = {
    ".git",
    ".next",
    ".turbo",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "site-packages",
}

TYPE_SCRIPT_PATTERNS = {
    "package.json",
    "tsconfig.json",
    "pnpm-lock.yaml",
    "package-lock.json",
    "yarn.lock",
    "bun.lockb",
}

PYTHON_PATTERNS = {
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "Pipfile",
    "poetry.lock",
}

FRAMEWORK_FILES = {
    "next.config.js": "Next.js",
    "next.config.mjs": "Next.js",
    "next.config.ts": "Next.js",
    "turbo.json": "Turborepo",
    "nx.json": "Nx",
    "manage.py": "Django",
    "alembic.ini": "Alembic",
}

CI_PATTERNS = (
    ".github/workflows",
    ".gitlab-ci.yml",
    "circle.yml",
    ".circleci/config.yml",
)

PACKAGE_MANAGER_LOCKFILES = {
    "pnpm-lock.yaml": "pnpm",
    "package-lock.json": "npm",
    "yarn.lock": "yarn",
    "bun.lockb": "bun",
    "poetry.lock": "poetry",
    "Pipfile": "pipenv",
}


@dataclass(frozen=True)
class ReviewContext:
    """レビュー初動で参照する repo コンテキストをまとめる。"""

    repo_root: str
    detected_languages: list[str]
    selected_language_hints: list[str]
    manifests: list[str]
    package_manager_hints: list[str]
    framework_hints: list[str]
    source_roots: list[str]
    test_roots: list[str]
    module_boundary_hints: list[str]
    ci_hints: list[str]
    notes: list[str]


def normalize_path(path: Path, repo: Path) -> str:
    """出力用に repo 相対パスへ正規化する。"""

    try:
        return str(path.relative_to(repo))
    except ValueError:
        return str(path)


def is_code_file(filename: str) -> bool:
    """レビュー対象の主要言語に関係するコードファイルかを返す。"""

    return filename.endswith((".ts", ".tsx", ".js", ".jsx", ".py"))


def walk_limited(repo: Path, max_depth: int = 4) -> tuple[list[str], list[str]]:
    """manifest とコードを含むディレクトリ候補を軽量に拾う。"""

    manifests: list[str] = []
    code_dirs: list[str] = []

    for current_root, dirnames, filenames in os.walk(repo):
        current_path = Path(current_root)
        depth = len(current_path.relative_to(repo).parts)

        # 重いディレクトリを早めに除外し、read-only の棚卸しを軽く保つ。
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in IGNORED_DIRS and depth < max_depth
        ]

        for filename in filenames:
            file_path = current_path / filename
            relative_path = normalize_path(file_path, repo)

            if filename in TYPE_SCRIPT_PATTERNS or filename in PYTHON_PATTERNS:
                manifests.append(relative_path)

            if is_code_file(filename):
                code_dirs.append(normalize_path(current_path, repo))

        if depth >= max_depth:
            dirnames[:] = []

    return sorted(set(manifests)), sorted(set(code_dirs))


def classify_code_dirs(repo: Path, code_dirs: list[str]) -> tuple[list[str], list[str]]:
    """コードを含むディレクトリ群から source/test root を整理する。"""

    source_roots: set[str] = set()
    test_roots: set[str] = set()

    for relative_dir in code_dirs:
        path = repo / relative_dir
        parts = path.relative_to(repo).parts
        if not parts:
            continue

        lowered_parts = [part.lower() for part in parts]
        if any(part in {"tests", "test", "__tests__"} for part in lowered_parts):
            test_index = next(
                index
                for index, part in enumerate(lowered_parts)
                if part in {"tests", "test", "__tests__"}
            )
            test_roots.add(str(Path(*parts[: test_index + 1])))
            continue

        # top-level / 2 階層目までのコード配置を拾い、feature や package の入口を見つけやすくする。
        if parts[0].lower() in {"apps", "packages", "services", "libs", "modules"} and len(parts) >= 2:
            source_roots.add(str(Path(parts[0]) / parts[1]))
            continue

        source_roots.add(parts[0])

    return sorted(source_roots), sorted(test_roots)


def detect_languages(repo: Path, manifests: list[str]) -> tuple[list[str], list[str]]:
    """manifest とファイル拡張子から言語候補を返す。"""

    detected_languages: set[str] = set()
    notes: list[str] = []

    manifest_names = {Path(item).name for item in manifests}
    if manifest_names & TYPE_SCRIPT_PATTERNS:
        detected_languages.add("typescript")
    if manifest_names & PYTHON_PATTERNS:
        detected_languages.add("python")

    if not detected_languages:
        for current_root, dirnames, filenames in os.walk(repo):
            current_path = Path(current_root)
            depth = len(current_path.relative_to(repo).parts)
            dirnames[:] = [
                dirname
                for dirname in dirnames
                if dirname not in IGNORED_DIRS and depth < 3
            ]

            for filename in filenames:
                if filename.endswith((".ts", ".tsx", ".js", ".jsx")):
                    detected_languages.add("typescript")
                if filename.endswith(".py"):
                    detected_languages.add("python")

            if depth >= 3 or detected_languages == {"typescript", "python"}:
                dirnames[:] = []

    if not detected_languages:
        notes.append("TypeScript と Python の明確な痕跡が見つかりませんでした。一般則でレビューして下さい。")

    return sorted(detected_languages), notes


def detect_package_managers(manifests: list[str]) -> list[str]:
    """lockfile や manifest から package manager の手がかりを返す。"""

    hints: list[str] = []
    for manifest in manifests:
        file_name = Path(manifest).name
        if file_name in PACKAGE_MANAGER_LOCKFILES:
            hints.append(f"{PACKAGE_MANAGER_LOCKFILES[file_name]} ({manifest})")
    return sorted(set(hints))


def detect_frameworks(repo: Path) -> list[str]:
    """代表的な framework や task runner の手がかりを返す。"""

    hints: list[str] = []

    for relative_path, framework_name in FRAMEWORK_FILES.items():
        if (repo / relative_path).exists():
            hints.append(f"{framework_name} ({relative_path})")

    pyproject_path = repo / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text(errors="ignore")
        if "fastapi" in content.lower():
            hints.append("FastAPI (pyproject.toml)")
        if "flask" in content.lower():
            hints.append("Flask (pyproject.toml)")
        if "django" in content.lower():
            hints.append("Django (pyproject.toml)")

    return sorted(set(hints))


def detect_ci(repo: Path) -> list[str]:
    """CI の設定ファイルやディレクトリを返す。"""

    hints: list[str] = []
    for relative_path in CI_PATTERNS:
        if (repo / relative_path).exists():
            hints.append(relative_path)
    return sorted(hints)


def detect_module_boundaries(repo: Path) -> list[str]:
    """責務分離の当たりを付けるための主要ディレクトリを返す。"""

    candidates = (
        "apps",
        "packages",
        "services",
        "libs",
        "modules",
        "src",
        "backend",
        "frontend",
        "api",
        "domain",
        "tests",
    )

    hints: list[str] = []
    for candidate in candidates:
        path = repo / candidate
        if path.exists() and path.is_dir():
            hints.append(candidate)

    for child in sorted(repo.iterdir()):
        if not child.is_dir() or child.name in IGNORED_DIRS or child.name.startswith("."):
            continue
        if child.name not in hints:
            inner_files = list(child.glob("*.py")) + list(child.glob("*.ts")) + list(child.glob("*.tsx"))
            has_subdirs = any(grandchild.is_dir() for grandchild in child.iterdir())
            if inner_files or has_subdirs:
                hints.append(child.name)
    return hints


def build_selected_language_hints(detected_languages: list[str]) -> list[str]:
    """読み込むべき言語別 reference の候補を返す。"""

    hints: list[str] = []
    if "typescript" in detected_languages:
        hints.append("references/languages/typescript.md")
    if "python" in detected_languages:
        hints.append("references/languages/python.md")
    if not hints:
        hints.append("言語共通の review_methodology を使い、未対応言語は一般則で評価する")
    return hints


def detect_review_context(repo: Path) -> ReviewContext:
    """repo の軽量棚卸し結果を構造化して返す。"""

    manifests, code_dirs = walk_limited(repo)
    source_roots, test_roots = classify_code_dirs(repo, code_dirs)
    detected_languages, notes = detect_languages(repo, manifests)

    if not source_roots:
        notes.append("典型的な source root が自動検出できなかったため、主要ディレクトリを手動確認して下さい。")
    if not test_roots:
        notes.append("典型的な test root が自動検出できなかったため、テスト配置を追加で確認して下さい。")

    return ReviewContext(
        repo_root=str(repo.resolve()),
        detected_languages=detected_languages,
        selected_language_hints=build_selected_language_hints(detected_languages),
        manifests=manifests,
        package_manager_hints=detect_package_managers(manifests),
        framework_hints=detect_frameworks(repo),
        source_roots=source_roots,
        test_roots=test_roots,
        module_boundary_hints=detect_module_boundaries(repo),
        ci_hints=detect_ci(repo),
        notes=notes,
    )


def print_text(context: ReviewContext) -> None:
    """人が読みやすい text 形式で棚卸し結果を出す。"""

    print(f"repo_root: {context.repo_root}")
    print(f"detected_languages: {', '.join(context.detected_languages) or '(none)'}")
    print(
        "selected_language_hints: "
        + (", ".join(context.selected_language_hints) or "(none)")
    )
    print(f"manifests: {', '.join(context.manifests) or '(none)'}")
    print(
        "package_manager_hints: "
        + (", ".join(context.package_manager_hints) or "(none)")
    )
    print(f"framework_hints: {', '.join(context.framework_hints) or '(none)'}")
    print(f"source_roots: {', '.join(context.source_roots) or '(none)'}")
    print(f"test_roots: {', '.join(context.test_roots) or '(none)'}")
    print(
        "module_boundary_hints: "
        + (", ".join(context.module_boundary_hints) or "(none)")
    )
    print(f"ci_hints: {', '.join(context.ci_hints) or '(none)'}")
    print(f"notes: {', '.join(context.notes) or '(none)'}")


def main() -> None:
    """CLI エントリーポイント。"""

    parser = argparse.ArgumentParser(
        description="リポジトリ品質レビュー用の軽量棚卸し情報を返します。",
    )
    parser.add_argument("--repo", required=True, help="対象リポジトリのパス")
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="出力形式",
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        raise SystemExit(f"対象リポジトリが見つかりません: {repo}")
    if not repo.is_dir():
        raise SystemExit(f"対象パスはディレクトリではありません: {repo}")

    context = detect_review_context(repo)

    if args.format == "json":
        print(json.dumps(asdict(context), ensure_ascii=False, indent=2))
        return

    print_text(context)


if __name__ == "__main__":
    main()

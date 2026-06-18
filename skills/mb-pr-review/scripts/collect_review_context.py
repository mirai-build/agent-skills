#!/usr/bin/env python3
"""PR/ブランチ差分レビューの初動で使う read-only コンテキストを集める。"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

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
GUIDE_FILENAMES = {"agents.md", "contributing.md", "readme.md", "copilot-instructions.md"}
GUIDE_KEYWORDS = ("coding", "style", "guide", "guideline", "規約", "開発")


def run_command(args: list[str], cwd: Path) -> tuple[int, str, str]:
    """外部コマンドを実行し、失敗時も呼び出し側で判断できる形で返す。"""

    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def require_repo_root(repo: Path) -> Path:
    """任意のパスから Git repo root を解決する。"""

    code, stdout, stderr = run_command(["git", "rev-parse", "--show-toplevel"], repo)
    if code != 0:
        raise SystemExit(f"[ERROR] Git repo ではありません: {repo}\n{stderr}")
    return Path(stdout)


def ref_exists(repo: Path, ref: str) -> bool:
    """base/head 候補がローカル Git で解決できるかを確認する。"""

    code, _, _ = run_command(["git", "rev-parse", "--verify", "--quiet", ref], repo)
    return code == 0


def infer_default_base(repo: Path, notes: list[str]) -> str:
    """base 未指定時に remote default branch を推定する。"""

    code, stdout, _ = run_command(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], repo)
    if code == 0 and stdout:
        return stdout

    for candidate in ("origin/main", "origin/develop", "main", "develop"):
        if ref_exists(repo, candidate):
            notes.append("origin/HEAD が未設定のため、存在する branch から base を推定しました。")
            return candidate

    notes.append("base を推定できませんでした。必要なら --base を指定して下さい。")
    return "origin/main"


def parse_changed_files(raw_output: str) -> list[dict[str, str]]:
    """`git diff --name-status` の出力を JSON 化しやすい配列へ変換する。"""

    changed_files: list[dict[str, str]] = []
    for line in raw_output.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0]
        path = parts[-1] if not status.startswith(("R", "C")) else f"{parts[1]} -> {parts[-1]}"
        changed_files.append({"status": status, "path": path})
    return changed_files


def collect_coding_guides(repo: Path, max_depth: int = 5) -> list[str]:
    """プロジェクト固有ルールやコーディングガイドらしい文書を path 昇順で返す。"""

    candidates: set[str] = set()
    for current_root, dirnames, filenames in os.walk(repo):
        current_path = Path(current_root)
        depth = len(current_path.relative_to(repo).parts)
        dirnames[:] = [
            dirname for dirname in dirnames if dirname not in IGNORED_DIRS and depth < max_depth
        ]

        for filename in filenames:
            file_path = current_path / filename
            relative_path = file_path.relative_to(repo)
            lower_name = filename.lower()
            lower_path = str(relative_path).lower()
            is_doc = file_path.suffix.lower() in {".md", ".mdx", ".txt"}

            if lower_name in GUIDE_FILENAMES or lower_path.startswith((".cursor/rules", ".github/")):
                candidates.add(str(relative_path))
            elif is_doc and "docs/" in lower_path and any(key in lower_path for key in GUIDE_KEYWORDS):
                candidates.add(str(relative_path))

        if depth >= max_depth:
            dirnames[:] = []

    return sorted(candidates)


def build_context(args: argparse.Namespace) -> dict[str, Any]:
    """CLI 引数からレビュー対象の差分情報を組み立てる。"""

    repo = require_repo_root(Path(args.repo).resolve())
    notes: list[str] = []
    base_ref = args.base
    head_ref = args.head or "HEAD"
    if not base_ref:
        base_ref = infer_default_base(repo, notes)

    code, merge_base, stderr = run_command(["git", "merge-base", base_ref, head_ref], repo)
    if code != 0:
        notes.append(f"merge-base を取得できませんでした: {stderr}")
        merge_base = None

    diff_range = f"{base_ref}...{head_ref}"
    code, name_status, stderr = run_command(
        ["git", "diff", "--name-status", "--find-renames", diff_range],
        repo,
    )
    changed_files = parse_changed_files(name_status) if code == 0 else []
    if code != 0:
        notes.append(f"差分ファイルを取得できませんでした: {stderr}")

    code, log_output, _ = run_command(
        ["git", "log", "--oneline", "--decorate", "--no-merges", f"{base_ref}..{head_ref}"],
        repo,
    )

    return {
        "repo_root": str(repo),
        "base_ref": base_ref,
        "head_ref": head_ref,
        "merge_base": merge_base,
        "diff_range": diff_range,
        "commits": log_output.splitlines() if code == 0 and log_output else [],
        "changed_files": changed_files,
        "coding_guide_candidates": collect_coding_guides(repo),
        "notes": notes,
    }


def render_markdown(context: dict[str, Any]) -> str:
    """人が読みやすい Markdown 形式でレビュー初動情報を出力する。"""

    lines = [
        "# Review Context",
        "",
        f"- repo: `{context['repo_root']}`",
        f"- base: `{context['base_ref']}`",
        f"- head: `{context['head_ref']}`",
        f"- diff: `{context['diff_range']}`",
        f"- merge-base: `{context['merge_base'] or 'unresolved'}`",
    ]

    sections = (
        ("Coding Guide Candidates", context["coding_guide_candidates"], lambda item: f"- `{item}`"),
        ("Changed Files", context["changed_files"], lambda item: f"- `{item['status']}` `{item['path']}`"),
        ("Commits", context["commits"], lambda item: f"- {item}"),
        ("Notes", context["notes"], lambda item: f"- {item}"),
    )
    for title, items, formatter in sections:
        lines.extend(["", f"## {title}"])
        lines.extend(formatter(item) for item in items)
        if not items:
            lines.append("- なし")

    return "\n".join(lines) + "\n"


def main() -> None:
    """CLI エントリーポイント。"""

    parser = argparse.ArgumentParser(description="PR/ブランチ差分レビューの初動情報を集めます。")
    parser.add_argument("--repo", default=".", help="対象 Git repository")
    parser.add_argument("--base", help="比較元 branch/ref。未指定なら remote default を使う")
    parser.add_argument("--head", help="比較先 branch/ref。未指定なら HEAD を使う")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args()

    context = build_context(args)
    print(render_markdown(context) if args.format == "markdown" else json.dumps(context, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

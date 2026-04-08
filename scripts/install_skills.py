#!/usr/bin/env python3
"""このリポジトリの Skill を home または他リポジトリへコピーインストールする。"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
# 現行の Codex は user / repo ともに `.agents/skills` を探索する。
# 旧来の `.codex/skills` や `repo/skills` は互換運用の名残として残りうるが、
# 新規インストール先の正本はこの定数でそろえる。
USER_SKILLS_DIR = Path.home() / ".agents" / "skills"
RENAMED_SKILL_DIRECTORIES: dict[str, tuple[str, ...]] = {
    "mb-ddd-architect": ("mb-domain-driven-design",),
    # React FDA Skill は旧名称からの置き換えで 1 つにそろえる。
    "mb-react-fda-engineer": ("mb-fda-frontend-engineer",),
}


class InstallError(RuntimeError):
    """インストール手順中にユーザーへ説明すべき失敗を表す。"""


def list_available_skills() -> list[str]:
    """配布対象として扱う Skill 名だけを一覧化する。"""

    if not SKILLS_DIR.exists():
        return []

    skills: list[str] = []
    for path in sorted(SKILLS_DIR.iterdir()):
        if path.is_dir() and (path / "SKILL.md").exists():
            skills.append(path.name)
    return skills


def resolve_home_directory() -> Path:
    """Codex が自動検出する標準の Skill 配置先を返す。"""

    return USER_SKILLS_DIR.resolve()


def resolve_target_directory(mode: str, repo_path: str | None) -> Path:
    """インストール先ディレクトリを mode に応じて決定する。"""

    if mode == "home":
        return resolve_home_directory()

    if not repo_path:
        raise InstallError("--mode repo のときは --repo-path を指定して下さい。")

    target_repo = Path(repo_path).expanduser().resolve()
    if not target_repo.exists() or not target_repo.is_dir():
        raise InstallError(f"対象リポジトリのディレクトリが見つかりません: {target_repo}")

    return target_repo / ".agents" / "skills"


def select_skills(requested_skills: list[str], install_all: bool) -> list[str]:
    """`--skill` と `--all` を解釈して実際の対象 Skill 一覧を返す。"""

    available = list_available_skills()
    if not available:
        raise InstallError(f"Skill が見つかりません: {SKILLS_DIR}")

    if install_all:
        return available

    if not requested_skills:
        raise InstallError("--skill を指定するか --all を付けて下さい。")

    unknown = sorted(set(requested_skills) - set(available))
    if unknown:
        raise InstallError(
            "存在しない Skill が指定されました: " + ", ".join(unknown)
        )

    selected: list[str] = []
    seen: set[str] = set()
    for skill_name in requested_skills:
        if skill_name not in seen:
            selected.append(skill_name)
            seen.add(skill_name)
    return selected


def remove_replaced_skill_directories(
    skill_name: str,
    target_root: Path,
    dry_run: bool,
) -> None:
    """改名した Skill の旧ディレクトリが残らないように置換対象を片付ける。"""

    for legacy_name in RENAMED_SKILL_DIRECTORIES.get(skill_name, ()):
        legacy_dir = target_root / legacy_name
        if not legacy_dir.exists():
            continue

        if not dry_run:
            shutil.rmtree(legacy_dir)


def install_skill(
    skill_name: str,
    target_root: Path,
    overwrite: bool,
    dry_run: bool,
) -> Path:
    """1 つの Skill をコピーしてインストールする。"""

    source_dir = SKILLS_DIR / skill_name
    destination_dir = target_root / skill_name

    if not source_dir.exists():
        raise InstallError(f"Skill のソースが見つかりません: {source_dir}")

    if destination_dir.exists():
        if not overwrite:
            raise InstallError(
                f"既に同名 Skill が存在します: {destination_dir}。上書きする場合は --force を使って下さい。"
            )
        if not dry_run:
            # 上書き時に古いファイルを残さないよう、対象 Skill ディレクトリだけを置き換える。
            shutil.rmtree(destination_dir)

    # 改名した Skill は旧ディレクトリも同時に片付け、インストール先を 1 つにそろえる。
    remove_replaced_skill_directories(
        skill_name=skill_name,
        target_root=target_root,
        dry_run=dry_run,
    )

    if not dry_run:
        target_root.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            source_dir,
            destination_dir,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )

    return destination_dir


def build_parser() -> argparse.ArgumentParser:
    """CLI 引数定義をまとめる。"""

    parser = argparse.ArgumentParser(
        description="このリポジトリ内の Codex Skill をインストールします。",
    )
    parser.add_argument(
        "--mode",
        choices=["home", "repo"],
        default="home",
        help="インストール先の種別。home は ~/.agents/skills、repo は対象リポジトリ配下の .agents/skills です。",
    )
    parser.add_argument(
        "--repo-path",
        help="--mode repo のときに使う対象リポジトリのパス",
    )
    parser.add_argument(
        "--skill",
        action="append",
        default=[],
        help="インストールする Skill 名。複数指定できます。",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="このリポジトリにある Skill をすべてインストールします。",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="同名 Skill が存在するときに置き換えます。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="実際にはコピーせず、実行内容だけを表示します。",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="インストール可能な Skill を一覧表示します。",
    )
    return parser


def main() -> int:
    """CLI エントリーポイント。"""

    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.list:
            skills = list_available_skills()
            if not skills:
                print("利用可能な Skill はありません。")
                return 0
            print("利用可能な Skill:")
            for skill_name in skills:
                print(f"- {skill_name}")
            return 0

        selected_skills = select_skills(args.skill, args.all)
        target_root = resolve_target_directory(args.mode, args.repo_path)

        print(f"インストール先: {target_root}")
        for skill_name in selected_skills:
            destination = install_skill(
                skill_name=skill_name,
                target_root=target_root,
                overwrite=args.force,
                dry_run=args.dry_run,
            )
            action = "予定" if args.dry_run else "完了"
            print(f"[{action}] {skill_name} -> {destination}")

        if args.mode == "home" and not args.dry_run:
            print("Codex App を再起動すると新しい Skill が読み込まれます。")
        return 0
    except InstallError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

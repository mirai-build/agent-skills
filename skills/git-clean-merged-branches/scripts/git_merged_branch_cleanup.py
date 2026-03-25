#!/usr/bin/env python3
"""マージ済み Git ブランチの削除候補を調べ、安全に削除するユーティリティ。"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

EXACT_PROTECTED_BRANCHES = {
    "main",
    "master",
    "staging",
    "stage",
    "stg",
    "develop",
    "dev",
}


@dataclass(frozen=True)
class GitHubRemoteInfo:
    """GitHub リモートを識別するための owner/repository を保持する。"""

    owner: str
    repository: str


@dataclass
class BranchEntry:
    """1 ブランチぶんの判定結果を保持する。"""

    name: str
    scope: str
    status: str
    reasons: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class InspectionResult:
    """候補一覧、プロバイダ由来の補足情報、警告をまとめて返す。"""

    repository: str
    remote: str
    scope: str
    local_base: str | None
    remote_base: str | None
    provider_default_branch: str | None
    provider_default_branch_status: str
    provider_protected_branches: list[str]
    provider_protection_status: str
    provider_merged_pr_branches: list[str]
    provider_pr_status: str
    candidates: list[BranchEntry]
    excluded: list[BranchEntry]
    warnings: list[str]


class CleanupError(RuntimeError):
    """ユーザー向けに説明可能な失敗を表す。"""


def run_git(repo: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    """対象リポジトリで Git コマンドを実行する。"""

    command = ["git", *args]
    completed = subprocess.run(
        command,
        cwd=repo,
        check=False,
        text=True,
        capture_output=True,
    )
    if check and completed.returncode != 0:
        stderr = completed.stderr.strip()
        stdout = completed.stdout.strip()
        details = stderr or stdout or "出力なし"
        raise CleanupError(f"Git コマンドに失敗しました: {' '.join(command)}\n{details}")
    return completed


def run_gh(repo: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    """gh CLI を実行し、GitHub API 由来の情報取得に使う。"""

    return subprocess.run(
        ["gh", *args],
        cwd=repo,
        check=False,
        text=True,
        capture_output=True,
    )


def ensure_git_repository(repo: Path) -> None:
    """指定パスが Git リポジトリかを確認する。"""

    result = run_git(repo, ["rev-parse", "--is-inside-work-tree"])
    if result.stdout.strip() != "true":
        raise CleanupError(f"Git リポジトリではありません: {repo}")


def current_local_branch(repo: Path) -> str | None:
    """HEAD がブランチ上にあるときだけ名前を返す。"""

    result = run_git(repo, ["branch", "--show-current"], check=False)
    branch = result.stdout.strip()
    return branch or None


def list_local_branch_refs(repo: Path) -> dict[str, str]:
    """ローカルブランチ名と先端 SHA の対応を返す。"""

    result = run_git(repo, ["for-each-ref", "--format=%(refname:short)\t%(objectname)", "refs/heads"])
    refs: dict[str, str] = {}
    for line in result.stdout.splitlines():
        short_name, _, sha = line.partition("\t")
        if short_name and sha:
            refs[short_name.strip()] = sha.strip()
    return refs


def list_remote_branch_refs(repo: Path, remote: str) -> dict[str, str]:
    """指定リモート配下のブランチ名と先端 SHA の対応を返す。"""

    result = run_git(
        repo,
        ["for-each-ref", "--format=%(refname:short)\t%(objectname)", f"refs/remotes/{remote}"],
        check=False,
    )
    refs: dict[str, str] = {}
    if result.returncode != 0:
        return refs

    prefix = f"{remote}/"
    for line in result.stdout.splitlines():
        short_name, _, sha = line.partition("\t")
        short_name = short_name.strip()
        sha = sha.strip()
        if not short_name or not sha or short_name == f"{remote}/HEAD" or not short_name.startswith(prefix):
            continue
        refs[short_name.removeprefix(prefix)] = sha
    return refs


def parse_remote_url(url: str) -> tuple[str, str] | None:
    """GitHub URL から owner/repo を抜き出す。対応外なら None を返す。"""

    normalized = url.strip()
    if normalized.endswith(".git"):
        normalized = normalized[:-4]

    if normalized.startswith("git@github.com:"):
        path = normalized.removeprefix("git@github.com:")
    elif normalized.startswith("ssh://git@github.com/"):
        path = normalized.removeprefix("ssh://git@github.com/")
    elif normalized.startswith("https://github.com/"):
        path = normalized.removeprefix("https://github.com/")
    else:
        return None

    parts = [part for part in path.split("/") if part]
    if len(parts) != 2:
        return None
    return parts[0], parts[1]


def resolve_github_remote_info(repo: Path, remote: str, purpose: str) -> tuple[GitHubRemoteInfo | None, str, list[str]]:
    """GitHub リモートかどうかを確認し、API 呼び出しに必要な識別子を返す。"""

    warnings: list[str] = []
    remote_url = run_git(repo, ["remote", "get-url", remote], check=False)
    if remote_url.returncode != 0:
        warnings.append(f"リモート '{remote}' の URL を取得できなかったため、{purpose}をスキップしました。")
        return None, "skipped", warnings

    github_repo = parse_remote_url(remote_url.stdout.strip())
    if github_repo is None:
        warnings.append(f"GitHub リモートではないため、{purpose}をスキップしました。")
        return None, "unsupported", warnings

    if shutil.which("gh") is None:
        warnings.append(f"gh CLI が見つからないため、{purpose}をスキップしました。")
        return None, "unavailable", warnings

    owner, repository = github_repo
    return GitHubRemoteInfo(owner=owner, repository=repository), "detected", warnings


def fetch_provider_default_branch(repo: Path, remote: str) -> tuple[str | None, str, list[str]]:
    """GitHub リポジトリのデフォルトブランチを取得する。"""

    remote_info, status, warnings = resolve_github_remote_info(repo, remote, "GitHub のデフォルトブランチ取得")
    if remote_info is None:
        return None, status, warnings

    completed = run_gh(
        repo,
        [
            "api",
            f"repos/{remote_info.owner}/{remote_info.repository}",
            "--jq",
            ".default_branch",
        ],
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip() or "出力なし"
        warnings.append("gh CLI によるデフォルトブランチ取得に失敗しました。認証やネットワーク制約を確認してください。")
        warnings.append(f"gh エラー: {stderr}")
        return None, "failed", warnings

    branch = completed.stdout.strip()
    if not branch:
        warnings.append("GitHub のデフォルトブランチ名が空だったため、自動判定を継続します。")
        return None, "failed", warnings
    return branch, "detected", warnings


def fetch_provider_protected_branches(repo: Path, remote: str) -> tuple[list[str], str, list[str]]:
    """GitHub の保護ブランチ一覧を取得する。"""

    remote_info, status, warnings = resolve_github_remote_info(repo, remote, "保護ブランチの自動検出")
    if remote_info is None:
        return [], status, warnings

    completed = run_gh(
        repo,
        [
            "api",
            f"repos/{remote_info.owner}/{remote_info.repository}/branches",
            "--paginate",
            "--jq",
            ".[] | select(.protected == true) | .name",
        ],
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip() or "出力なし"
        warnings.append("gh CLI による保護ブランチ取得に失敗しました。認証やネットワーク制約を確認してください。")
        warnings.append(f"gh エラー: {stderr}")
        return [], "failed", warnings

    branches = sorted({line.strip() for line in completed.stdout.splitlines() if line.strip()})
    return branches, "detected", warnings


def fetch_provider_merged_pr_heads(
    repo: Path,
    remote: str,
    base_branch: str | None,
) -> tuple[dict[str, set[str]], str, list[str]]:
    """GitHub 上で merged 済み PR の head ブランチ名と SHA を取得する。"""

    warnings: list[str] = []
    if not base_branch:
        warnings.append("GitHub PR の merged 状態を確認するための基準ブランチを解決できなかったため、PR 判定をスキップしました。")
        return {}, "skipped", warnings

    remote_info, status, remote_warnings = resolve_github_remote_info(repo, remote, "GitHub PR の merged 状態確認")
    warnings.extend(remote_warnings)
    if remote_info is None:
        return {}, status, warnings

    same_repo = f"{remote_info.owner}/{remote_info.repository}"
    completed = run_gh(
        repo,
        [
            "api",
            f"repos/{remote_info.owner}/{remote_info.repository}/pulls",
            "-X",
            "GET",
            "--paginate",
            "-f",
            "state=closed",
            "-f",
            f"base={base_branch}",
            "-f",
            "per_page=100",
            "--jq",
            (
                ".[] | select(.merged_at != null and .head.repo != null and .head.repo.full_name == "
                f"\"{same_repo}\") | [.head.ref, .head.sha] | @tsv"
            ),
        ],
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip() or "出力なし"
        warnings.append("gh CLI による merged PR 取得に失敗しました。認証やネットワーク制約を確認してください。")
        warnings.append(f"gh エラー: {stderr}")
        return {}, "failed", warnings

    merged_pr_heads: dict[str, set[str]] = {}
    for line in completed.stdout.splitlines():
        branch_name, _, sha = line.partition("\t")
        branch_name = branch_name.strip()
        sha = sha.strip()
        if not branch_name or not sha:
            continue
        merged_pr_heads.setdefault(branch_name, set()).add(sha)
    return merged_pr_heads, "detected", warnings


def resolve_base_branches(
    repo: Path,
    remote: str,
    explicit_base: str | None,
    provider_default_branch: str | None,
    local_branch_refs: dict[str, str],
    remote_branch_refs: dict[str, str],
) -> tuple[str | None, str | None, str | None, list[str]]:
    """ローカル判定用とリモート判定用の基準ブランチを決める。"""

    warnings: list[str] = []
    if explicit_base:
        local_base = explicit_base if explicit_base in local_branch_refs else None
        remote_base = explicit_base if explicit_base in remote_branch_refs else None
        if local_base is None:
            warnings.append(f"ローカル基準ブランチ '{explicit_base}' が見つかりませんでした。")
        if remote_base is None:
            warnings.append(f"リモート基準ブランチ '{remote}/{explicit_base}' が見つかりませんでした。")
        return explicit_base, local_base, remote_base, warnings

    if provider_default_branch:
        local_base = provider_default_branch if provider_default_branch in local_branch_refs else None
        remote_base = provider_default_branch if provider_default_branch in remote_branch_refs else None
        if local_base is None:
            warnings.append(
                f"GitHub のデフォルトブランチ '{provider_default_branch}' はローカルに存在しません。"
            )
        if remote_base is None:
            warnings.append(
                f"GitHub のデフォルトブランチ '{remote}/{provider_default_branch}' はローカルの追跡参照に存在しません。"
            )
        return provider_default_branch, local_base, remote_base, warnings

    origin_head = run_git(
        repo,
        ["symbolic-ref", "--quiet", f"refs/remotes/{remote}/HEAD"],
        check=False,
    )
    if origin_head.returncode == 0:
        full_ref = origin_head.stdout.strip()
        base_name = full_ref.removeprefix(f"refs/remotes/{remote}/")
        return (
            base_name,
            base_name if base_name in local_branch_refs else None,
            base_name if base_name in remote_branch_refs else None,
            warnings,
        )

    current_branch = current_local_branch(repo)
    if current_branch:
        warnings.append(
            f"GitHub のデフォルトブランチと {remote}/HEAD を解決できなかったため、現在のローカルブランチ '{current_branch}' を基準にします。"
        )
        return (
            current_branch,
            current_branch if current_branch in local_branch_refs else None,
            current_branch if current_branch in remote_branch_refs else None,
            warnings,
        )

    warnings.append("基準ブランチを自動判定できませんでした。--base を指定してください。")
    return None, None, None, warnings


def is_merged(repo: Path, branch_ref: str, base_ref: str) -> bool:
    """branch_ref が base_ref に取り込まれているかを判定する。"""

    result = run_git(repo, ["merge-base", "--is-ancestor", branch_ref, base_ref], check=False)
    return result.returncode == 0


def is_merged_via_pr(branch_name: str, branch_sha: str, merged_pr_heads: dict[str, set[str]]) -> bool:
    """PR merged 判定では、現在のブランチ先端 SHA が merged PR の head SHA と一致するものだけを認める。"""

    return branch_sha in merged_pr_heads.get(branch_name, set())


def classify_branches(
    repo: Path,
    branch_refs: dict[str, str],
    scope: str,
    base_branch: str | None,
    base_ref: str | None,
    protected_branches: set[str],
    current_branch_name: str | None,
    remote: str,
    merged_pr_heads: dict[str, set[str]],
) -> tuple[list[BranchEntry], list[BranchEntry]]:
    """候補と除外を理由付きで分類する。"""

    candidates: list[BranchEntry] = []
    excluded: list[BranchEntry] = []

    for name, sha in sorted(branch_refs.items()):
        reasons: list[str] = []
        notes: list[str] = []
        branch_ref = f"refs/heads/{name}" if scope == "local" else f"refs/remotes/{remote}/{name}"

        if name in EXACT_PROTECTED_BRANCHES:
            reasons.append("完全一致の除外対象ブランチです。")
        if name in protected_branches:
            reasons.append("保護対象ブランチです。")
        if base_branch and name == base_branch:
            reasons.append("基準ブランチです。")
        if scope == "local" and current_branch_name and name == current_branch_name:
            reasons.append("現在チェックアウト中のブランチです。")

        if base_ref is None:
            reasons.append("基準ブランチを解決できませんでした。")
        else:
            merged_by_git = is_merged(repo, branch_ref, base_ref)
            merged_by_pr = is_merged_via_pr(name, sha, merged_pr_heads)
            if not merged_by_git and not merged_by_pr:
                reasons.append("基準ブランチへ未マージです。")
            elif merged_by_pr and not merged_by_git:
                # squash merge / rebase merge 済みでも、同じ head SHA が merged PR に対応していれば候補へ含める。
                notes.append("GitHub の merged PR の head SHA 一致を根拠に削除候補へ含めました。")

        entry = BranchEntry(
            name=name,
            scope=scope,
            status="excluded" if reasons else "candidate",
            reasons=reasons,
            notes=notes,
        )
        if reasons:
            excluded.append(entry)
        else:
            candidates.append(entry)

    return candidates, excluded


def inspect_repository(
    repo: Path,
    scope: str,
    remote: str,
    base: str | None,
    protected_branches: Iterable[str],
    detect_provider_protection: bool,
) -> InspectionResult:
    """削除候補と除外対象を一覧化する。"""

    ensure_git_repository(repo)
    local_branch_refs = list_local_branch_refs(repo)
    remote_branch_refs = list_remote_branch_refs(repo, remote)

    provider_default_branch, provider_default_status, warnings = fetch_provider_default_branch(repo, remote)
    resolved_base_name, local_base, remote_base, base_warnings = resolve_base_branches(
        repo=repo,
        remote=remote,
        explicit_base=base,
        provider_default_branch=provider_default_branch,
        local_branch_refs=local_branch_refs,
        remote_branch_refs=remote_branch_refs,
    )
    warnings.extend(base_warnings)

    provider_protected: list[str] = []
    provider_protection_status = "disabled"
    if detect_provider_protection:
        provider_protected, provider_protection_status, provider_warnings = fetch_provider_protected_branches(repo, remote)
        warnings.extend(provider_warnings)

    merged_pr_heads, provider_pr_status, provider_pr_warnings = fetch_provider_merged_pr_heads(
        repo=repo,
        remote=remote,
        base_branch=resolved_base_name,
    )
    warnings.extend(provider_pr_warnings)

    protected = set(protected_branches) | set(provider_protected)
    current_branch_name = current_local_branch(repo)

    local_base_ref: str | None = None
    if local_base:
        local_base_ref = f"refs/heads/{local_base}"
    elif remote_base and remote_base in remote_branch_refs:
        # ローカルに基準ブランチがなくても、追跡中のリモート基準ブランチで安全判定できる。
        local_base_ref = f"refs/remotes/{remote}/{remote_base}"
        warnings.append(
            f"ローカル基準ブランチが無いため、'{remote}/{remote_base}' をローカル判定の基準に使います。"
        )

    remote_base_ref = f"refs/remotes/{remote}/{remote_base}" if remote_base else None

    candidates: list[BranchEntry] = []
    excluded: list[BranchEntry] = []

    if scope in {"local", "both"}:
        local_candidates, local_excluded = classify_branches(
            repo=repo,
            branch_refs=local_branch_refs,
            scope="local",
            base_branch=resolved_base_name,
            base_ref=local_base_ref,
            protected_branches=protected,
            current_branch_name=current_branch_name,
            remote=remote,
            merged_pr_heads=merged_pr_heads,
        )
        candidates.extend(local_candidates)
        excluded.extend(local_excluded)

    if scope in {"remote", "both"}:
        remote_candidates, remote_excluded = classify_branches(
            repo=repo,
            branch_refs=remote_branch_refs,
            scope="remote",
            base_branch=resolved_base_name,
            base_ref=remote_base_ref,
            protected_branches=protected,
            current_branch_name=None,
            remote=remote,
            merged_pr_heads=merged_pr_heads,
        )
        candidates.extend(remote_candidates)
        excluded.extend(remote_excluded)

    return InspectionResult(
        repository=str(repo),
        remote=remote,
        scope=scope,
        local_base=local_base,
        remote_base=remote_base,
        provider_default_branch=provider_default_branch,
        provider_default_branch_status=provider_default_status,
        provider_protected_branches=sorted(provider_protected),
        provider_protection_status=provider_protection_status,
        provider_merged_pr_branches=sorted(merged_pr_heads),
        provider_pr_status=provider_pr_status,
        candidates=sorted(candidates, key=lambda item: (item.scope, item.name)),
        excluded=sorted(excluded, key=lambda item: (item.scope, item.name)),
        warnings=warnings,
    )


def find_branch_entry(entries: Iterable[BranchEntry], branch_name: str, scope: str) -> BranchEntry | None:
    """削除対象の妥当性確認に使う。"""

    for entry in entries:
        if entry.name == branch_name and entry.scope == scope:
            return entry
    return None


def delete_local_branch(repo: Path, branch_name: str) -> None:
    """ローカルのマージ済みブランチを通常削除する。"""

    run_git(repo, ["branch", "-d", branch_name])


def delete_remote_branch(repo: Path, remote: str, branch_name: str) -> None:
    """指定リモートからブランチを削除する。"""

    run_git(repo, ["push", remote, "--delete", branch_name])


def delete_branches(
    repo: Path,
    scope: str,
    remote: str,
    base: str | None,
    protected_branches: Iterable[str],
    detect_provider_protection: bool,
    branches: Iterable[str],
) -> dict[str, list[dict[str, str]]]:
    """inspect の結果に含まれる候補だけを削除する。"""

    inspection = inspect_repository(
        repo=repo,
        scope=scope,
        remote=remote,
        base=base,
        protected_branches=protected_branches,
        detect_provider_protection=detect_provider_protection,
    )

    requested = [item.strip() for item in branches if item.strip()]
    if not requested:
        raise CleanupError("削除対象ブランチが指定されていません。")

    deletions: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []

    for item in requested:
        if ":" not in item:
            raise CleanupError(
                "削除対象は 'scope:branch-name' 形式で指定してください。例: local:feature/foo"
            )
        target_scope, branch_name = item.split(":", 1)
        target_scope = target_scope.strip()
        branch_name = branch_name.strip()
        if target_scope not in {"local", "remote"}:
            raise CleanupError(f"未知の対象種別です: {target_scope}")

        candidate = find_branch_entry(inspection.candidates, branch_name, target_scope)
        if candidate is None:
            excluded = find_branch_entry(inspection.excluded, branch_name, target_scope)
            reason = ", ".join(excluded.reasons) if excluded else "inspect 結果の候補に存在しません。"
            skipped.append({"scope": target_scope, "name": branch_name, "reason": reason})
            continue

        if target_scope == "local":
            delete_local_branch(repo, branch_name)
        else:
            delete_remote_branch(repo, remote, branch_name)
        deletions.append({"scope": target_scope, "name": branch_name})

    return {
        "deleted": deletions,
        "skipped": skipped,
        "warnings": inspection.warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    """CLI 引数定義をまとめる。"""

    parser = argparse.ArgumentParser(
        description="マージ済み Git ブランチを一覧化し、保護条件を守って削除する。",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_shared_arguments(target: argparse.ArgumentParser) -> None:
        target.add_argument("--repo", default=".", help="対象リポジトリのパス")
        target.add_argument("--scope", choices=["local", "remote", "both"], default="both")
        target.add_argument("--remote", default="origin", help="対象リモート名")
        target.add_argument(
            "--base",
            help="基準ブランチ名。未指定時は GitHub のデフォルトブランチ、次に origin/HEAD を優先して自動判定します。",
        )
        target.add_argument(
            "--protected-branch",
            action="append",
            default=[],
            help="追加の保護対象ブランチ名。複数回指定できます。",
        )
        target.add_argument(
            "--detect-provider-protection",
            action="store_true",
            help="GitHub と gh CLI を使えるとき、保護ブランチも追加取得します。",
        )
        target.add_argument(
            "--format",
            choices=["json", "text"],
            default="json",
            help="出力形式",
        )

    inspect_parser = subparsers.add_parser("inspect", help="削除候補と除外対象を列挙する")
    add_shared_arguments(inspect_parser)

    delete_parser = subparsers.add_parser("delete", help="inspect 済みの候補から削除する")
    add_shared_arguments(delete_parser)
    delete_parser.add_argument(
        "--branch",
        action="append",
        default=[],
        help="削除対象。'local:foo' または 'remote:foo' 形式で複数回指定します。",
    )

    return parser


def print_text_inspection(result: InspectionResult) -> None:
    """人間向けの簡易表示。主用途はデバッグ。"""

    print(f"リポジトリ: {result.repository}")
    print(f"対象範囲: {result.scope}")
    print(f"リモート: {result.remote}")
    print(f"ローカル基準ブランチ: {result.local_base}")
    print(f"リモート基準ブランチ: {result.remote_base}")
    print(f"GitHub デフォルトブランチ: {result.provider_default_branch}")
    print(f"GitHub デフォルトブランチ取得状態: {result.provider_default_branch_status}")
    print(f"保護ブランチ自動検出状態: {result.provider_protection_status}")
    print(f"merged PR 判定状態: {result.provider_pr_status}")
    if result.provider_protected_branches:
        print("自動検出した保護ブランチ:")
        for name in result.provider_protected_branches:
            print(f"  - {name}")
    if result.provider_merged_pr_branches:
        print("merged PR を検出したブランチ:")
        for name in result.provider_merged_pr_branches:
            print(f"  - {name}")
    print("削除候補:")
    for entry in result.candidates:
        suffix = f" ({', '.join(entry.notes)})" if entry.notes else ""
        print(f"  - [{entry.scope}] {entry.name}{suffix}")
    print("除外対象:")
    for entry in result.excluded:
        print(f"  - [{entry.scope}] {entry.name}: {', '.join(entry.reasons)}")
    if result.warnings:
        print("警告:")
        for warning in result.warnings:
            print(f"  - {warning}")


def main() -> int:
    """CLI エントリーポイント。"""

    parser = build_parser()
    args = parser.parse_args()
    repo = Path(args.repo).expanduser().resolve()

    try:
        if args.command == "inspect":
            result = inspect_repository(
                repo=repo,
                scope=args.scope,
                remote=args.remote,
                base=args.base,
                protected_branches=args.protected_branch,
                detect_provider_protection=args.detect_provider_protection,
            )
            if args.format == "text":
                print_text_inspection(result)
            else:
                print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
            return 0

        result = delete_branches(
            repo=repo,
            scope=args.scope,
            remote=args.remote,
            base=args.base,
            protected_branches=args.protected_branch,
            detect_provider_protection=args.detect_provider_protection,
            branches=args.branch,
        )
        if args.format == "text":
            for deleted in result["deleted"]:
                print(f"削除: [{deleted['scope']}] {deleted['name']}")
            for skipped in result["skipped"]:
                print(f"スキップ: [{skipped['scope']}] {skipped['name']} ({skipped['reason']})")
            for warning in result["warnings"]:
                print(f"警告: {warning}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except CleanupError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

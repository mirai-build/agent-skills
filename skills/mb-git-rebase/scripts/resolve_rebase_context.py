#!/usr/bin/env python3
"""Git rebase を始める前の前提情報を整理するユーティリティ。"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

KNOWN_BASE_BRANCHES = (
    "main",
    "master",
    "develop",
    "dev",
    "staging",
    "stage",
    "release",
)


@dataclass(frozen=True)
class PullRequestInfo:
    """rebase 先解決に使う PR の要約を保持する。"""

    number: int
    title: str
    url: str
    source_branch: str
    destination_branch: str


@dataclass(frozen=True)
class ComparisonCandidate:
    """PR を解決できないときに提示する比較候補ブランチを表す。"""

    branch: str
    ahead_of_candidate: int
    behind_candidate: int
    is_remote_head: bool


@dataclass
class WorktreeStatus:
    """作業ツリーの汚れ具合をまとめる。"""

    staged_files: list[str] = field(default_factory=list)
    unstaged_files: list[str] = field(default_factory=list)
    untracked_files: list[str] = field(default_factory=list)

    @property
    def is_dirty(self) -> bool:
        """コミット前の変更があるかどうかを返す。"""

        return bool(self.staged_files or self.unstaged_files or self.untracked_files)


@dataclass
class InspectionResult:
    """Skill が rebase の進め方を判断するためのコンテキストを返す。"""

    repository: str
    remote: str
    remote_url: str | None
    provider: str
    current_branch: str | None
    branch_to_rebase: str
    explicit_base: str | None
    resolved_base: str | None
    preferred_base_ref: str | None
    base_resolution: str
    pull_request: PullRequestInfo | None
    comparison_candidates: list[ComparisonCandidate]
    rebase_in_progress: bool
    conflicted_files: list[str]
    checkout_required: bool
    worktree_dirty: bool
    staged_files: list[str]
    unstaged_files: list[str]
    untracked_files: list[str]
    warnings: list[str]


class ContextError(RuntimeError):
    """ユーザーへそのまま説明できる失敗を表す。"""


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
        raise ContextError(f"Git コマンドに失敗しました: {' '.join(command)}\n{details}")
    return completed


def ensure_git_repository(repo: Path) -> None:
    """指定ディレクトリが Git リポジトリかどうかを確認する。"""

    result = run_git(repo, ["rev-parse", "--is-inside-work-tree"])
    if result.stdout.strip() != "true":
        raise ContextError(f"Git リポジトリではありません: {repo}")


def current_branch(repo: Path) -> str | None:
    """HEAD がブランチ上にあるときだけブランチ名を返す。"""

    result = run_git(repo, ["branch", "--show-current"], check=False)
    branch = result.stdout.strip()
    return branch or None


def collect_worktree_status(repo: Path) -> WorktreeStatus:
    """`git status --porcelain` を解釈して dirty 状態を返す。"""

    result = run_git(repo, ["status", "--porcelain"])
    status = WorktreeStatus()

    for line in result.stdout.splitlines():
        if len(line) < 3:
            continue
        code = line[:2]
        path = line[3:].strip()
        if not path:
            continue

        # rename は `old -> new` の形式になるので、見た目に分かりやすい新しい名前を優先する。
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()

        if code == "??":
            status.untracked_files.append(path)
            continue
        if code[0] not in {" ", "?"}:
            status.staged_files.append(path)
        if code[1] != " ":
            status.unstaged_files.append(path)

    return status


def conflicted_files(repo: Path) -> list[str]:
    """未解決コンフリクトのファイル一覧を返す。"""

    result = run_git(repo, ["diff", "--name-only", "--diff-filter=U"], check=False)
    return sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})


def rebase_in_progress(repo: Path) -> bool:
    """`git rebase` の途中かどうかを判定する。"""

    for state_dir in ("rebase-merge", "rebase-apply"):
        git_path = run_git(repo, ["rev-parse", "--git-path", state_dir]).stdout.strip()
        if not git_path:
            continue
        resolved_path = Path(git_path)
        if not resolved_path.is_absolute():
            resolved_path = repo / resolved_path
        if resolved_path.exists():
            return True
    return False


def remote_url(repo: Path, remote: str) -> str | None:
    """対象リモートの URL を返す。"""

    result = run_git(repo, ["remote", "get-url", remote], check=False)
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def detect_provider(url: str | None) -> str:
    """リモート URL からプロバイダ種別をざっくり判定する。"""

    if not url:
        return "unknown"
    normalized = url.lower()
    if "github" in normalized:
        return "github"
    if "bitbucket" in normalized:
        return "bitbucket"
    return "unknown"


def remote_head_branch(repo: Path, remote: str) -> str | None:
    """`origin/HEAD` 相当の既定ブランチ名を返す。"""

    result = run_git(
        repo,
        ["symbolic-ref", "--quiet", f"refs/remotes/{remote}/HEAD"],
        check=False,
    )
    if result.returncode != 0:
        return None
    full_ref = result.stdout.strip()
    if not full_ref:
        return None
    prefix = f"refs/remotes/{remote}/"
    if not full_ref.startswith(prefix):
        return None
    return full_ref.removeprefix(prefix)


def remote_branches(repo: Path, remote: str) -> list[str]:
    """リモート追跡ブランチを一覧化する。"""

    result = run_git(
        repo,
        ["for-each-ref", "--format=%(refname:short)", f"refs/remotes/{remote}"],
        check=False,
    )
    if result.returncode != 0:
        return []

    prefix = f"{remote}/"
    branches: list[str] = []
    for line in result.stdout.splitlines():
        name = line.strip()
        if not name or name == f"{remote}/HEAD" or not name.startswith(prefix):
            continue
        branches.append(name.removeprefix(prefix))
    return sorted(set(branches))


def local_branch_exists(repo: Path, branch: str) -> bool:
    """ローカルブランチの存在を確認する。"""

    result = run_git(repo, ["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], check=False)
    return result.returncode == 0


def remote_branch_exists(repo: Path, remote: str, branch: str) -> bool:
    """ローカルの追跡参照に対象ブランチがあるか確認する。"""

    result = run_git(
        repo,
        ["show-ref", "--verify", "--quiet", f"refs/remotes/{remote}/{branch}"],
        check=False,
    )
    return result.returncode == 0


def resolve_branch_ref(repo: Path, remote: str, branch: str) -> str:
    """比較対象として使う branch ref を決める。"""

    if local_branch_exists(repo, branch):
        return f"refs/heads/{branch}"
    if remote_branch_exists(repo, remote, branch):
        return f"refs/remotes/{remote}/{branch}"
    raise ContextError(
        f"rebase 対象ブランチ '{branch}' がローカルにも追跡参照にも見つかりません。"
    )


def comparison_candidate_names(
    repo: Path,
    remote: str,
    branch_to_rebase: str,
    head_branch: str | None,
) -> list[str]:
    """比較で見せる候補ブランチ名を優先度付きで絞り込む。"""

    branch_names = remote_branches(repo, remote)
    filtered = [name for name in branch_names if name != branch_to_rebase]

    preferred: list[str] = []
    if head_branch and head_branch in filtered:
        preferred.append(head_branch)
    for name in filtered:
        if name in KNOWN_BASE_BRANCHES or any(name.startswith(f"{base}/") for base in KNOWN_BASE_BRANCHES):
            preferred.append(name)

    deduped: list[str] = []
    seen: set[str] = set()
    for name in preferred + filtered:
        if name not in seen:
            deduped.append(name)
            seen.add(name)

    return deduped[:8]


def compare_branch_distance(
    repo: Path,
    branch_ref: str,
    candidate_ref: str,
) -> tuple[int, int]:
    """対象ブランチと候補ブランチの ahead / behind を返す。"""

    result = run_git(
        repo,
        ["rev-list", "--left-right", "--count", f"{candidate_ref}...{branch_ref}"],
    )
    left, _, right = result.stdout.strip().partition("\t")
    return int(right or "0"), int(left or "0")


def build_comparison_candidates(
    repo: Path,
    remote: str,
    branch_to_rebase: str,
    head_branch: str | None,
) -> list[ComparisonCandidate]:
    """PR を見つけられないときの比較候補を ahead / behind 付きで返す。"""

    branch_ref = resolve_branch_ref(repo, remote, branch_to_rebase)
    candidates: list[ComparisonCandidate] = []

    for name in comparison_candidate_names(repo, remote, branch_to_rebase, head_branch):
        candidate_ref = f"refs/remotes/{remote}/{name}"
        if not remote_branch_exists(repo, remote, name):
            continue
        ahead, behind = compare_branch_distance(repo, branch_ref, candidate_ref)
        candidates.append(
            ComparisonCandidate(
                branch=name,
                ahead_of_candidate=ahead,
                behind_candidate=behind,
                is_remote_head=(name == head_branch),
            )
        )

    # remote HEAD を最優先に見せつつ、差分が近いブランチも続けて確認できる順へ並べる。
    return sorted(
        candidates,
        key=lambda item: (
            0 if item.is_remote_head else 1,
            item.ahead_of_candidate + item.behind_candidate,
            item.ahead_of_candidate,
            item.branch,
        ),
    )


def github_repository(url: str | None) -> tuple[str, str] | None:
    """GitHub リモートなら owner / repository を抜き出す。"""

    if not url:
        return None

    normalized = url.strip()
    if normalized.endswith(".git"):
        normalized = normalized[:-4]

    patterns = (
        r"^git@github\.com:/*(?P<owner>[^/]+)/(?P<repo>[^/]+)$",
        r"^ssh://git@github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)$",
        r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)$",
    )
    for pattern in patterns:
        match = re.match(pattern, normalized)
        if match:
            return match.group("owner"), match.group("repo")
    return None


def resolve_github_pull_request(
    repo: Path,
    remote_url_value: str | None,
    branch_to_rebase: str,
) -> tuple[PullRequestInfo | None, list[str], str]:
    """GitHub の open PR から rebase 先ブランチを解決する。"""

    warnings: list[str] = []
    github_repo = github_repository(remote_url_value)
    if github_repo is None:
        warnings.append("GitHub リモートを解析できなかったため、PR 先の自動判定をスキップしました。")
        return None, warnings, "provider_parse_failed"

    if shutil.which("gh") is None:
        warnings.append("gh CLI が見つからないため、GitHub PR 先の自動判定をスキップしました。")
        return None, warnings, "gh_unavailable"

    owner, repository = github_repo
    completed = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            f"{owner}/{repository}",
            "--state",
            "open",
            "--head",
            branch_to_rebase,
            "--json",
            "number,title,url,headRefName,baseRefName",
        ],
        cwd=repo,
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip() or "出力なし"
        warnings.append("gh CLI による GitHub PR 取得に失敗しました。認証やネットワーク制約を確認して下さい。")
        warnings.append(f"gh エラー: {stderr}")
        return None, warnings, "gh_failed"

    try:
        payload = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError:
        warnings.append("gh CLI の JSON 出力を解釈できなかったため、PR 先の自動判定をスキップしました。")
        return None, warnings, "invalid_json"

    matched = [
        item for item in payload
        if item.get("headRefName") == branch_to_rebase and item.get("baseRefName")
    ]
    if not matched:
        warnings.append("対象ブランチに対応する open PR は見つかりませんでした。")
        return None, warnings, "not_found"
    if len(matched) > 1:
        warnings.append("同じ head ブランチに対する open PR が複数あるため、自動で rebase 先を決めません。")
        return None, warnings, "ambiguous"

    item = matched[0]
    return (
        PullRequestInfo(
            number=int(item["number"]),
            title=str(item["title"]),
            url=str(item["url"]),
            source_branch=str(item["headRefName"]),
            destination_branch=str(item["baseRefName"]),
        ),
        warnings,
        "github_pr",
    )


def inspect_repository(
    repo: Path,
    remote: str,
    branch: str | None,
    explicit_base: str | None,
) -> InspectionResult:
    """rebase 開始前の状況と候補ブランチをまとめる。"""

    ensure_git_repository(repo)

    current = current_branch(repo)
    branch_to_rebase = branch or current
    if not branch_to_rebase:
        raise ContextError(
            "現在のブランチ名を解決できませんでした。対象ブランチを明示して下さい。"
        )

    status = collect_worktree_status(repo)
    remote_url_value = remote_url(repo, remote)
    provider = detect_provider(remote_url_value)
    head_branch = remote_head_branch(repo, remote)
    warnings: list[str] = []

    if remote_url_value is None:
        warnings.append(f"リモート '{remote}' の URL を取得できませんでした。")
    if head_branch is None:
        warnings.append(
            f"{remote}/HEAD を解決できなかったため、PR を見つけられない場合は比較候補を確認して下さい。"
        )

    resolved_base: str | None = None
    base_resolution = "unresolved"
    pull_request: PullRequestInfo | None = None

    if explicit_base:
        resolved_base = explicit_base
        base_resolution = "explicit"
    elif provider == "github":
        pull_request, pr_warnings, base_resolution = resolve_github_pull_request(
            repo=repo,
            remote_url_value=remote_url_value,
            branch_to_rebase=branch_to_rebase,
        )
        warnings.extend(pr_warnings)
        if pull_request is not None:
            resolved_base = pull_request.destination_branch
        elif head_branch:
            resolved_base = head_branch
            base_resolution = "remote_head_fallback"
    elif provider == "bitbucket":
        warnings.append("Bitbucket は PR 自動取得に依存せず、origin/HEAD と比較候補で rebase 先を絞り込みます。")
        if head_branch:
            resolved_base = head_branch
            base_resolution = "remote_head_fallback"
    elif head_branch:
        resolved_base = head_branch
        base_resolution = "remote_head_fallback"

    comparison_candidates = build_comparison_candidates(
        repo=repo,
        remote=remote,
        branch_to_rebase=branch_to_rebase,
        head_branch=head_branch,
    )
    if not comparison_candidates:
        warnings.append("比較候補に使えるリモート追跡ブランチが見つかりませんでした。")

    preferred_base_ref = f"{remote}/{resolved_base}" if resolved_base else None
    if resolved_base and not remote_branch_exists(repo, remote, resolved_base):
        warnings.append(
            f"ローカルの追跡参照に {remote}/{resolved_base} が無いため、rebase 前に `git fetch {remote} {resolved_base}` が必要です。"
        )

    active_rebase = rebase_in_progress(repo)
    unmerged = conflicted_files(repo)
    if active_rebase and not unmerged:
        warnings.append("rebase は進行中ですが、未解決コンフリクトは見つかりませんでした。")

    return InspectionResult(
        repository=str(repo),
        remote=remote,
        remote_url=remote_url_value,
        provider=provider,
        current_branch=current,
        branch_to_rebase=branch_to_rebase,
        explicit_base=explicit_base,
        resolved_base=resolved_base,
        preferred_base_ref=preferred_base_ref,
        base_resolution=base_resolution,
        pull_request=pull_request,
        comparison_candidates=comparison_candidates,
        rebase_in_progress=active_rebase,
        conflicted_files=unmerged,
        checkout_required=(current != branch_to_rebase),
        worktree_dirty=status.is_dirty,
        staged_files=status.staged_files,
        unstaged_files=status.unstaged_files,
        untracked_files=status.untracked_files,
        warnings=warnings,
    )


def format_text(result: InspectionResult) -> str:
    """人が読みやすい形で inspect 結果を整形する。"""

    lines = [
        f"repository: {result.repository}",
        f"remote: {result.remote}",
        f"provider: {result.provider}",
        f"current_branch: {result.current_branch or '(detached HEAD)'}",
        f"branch_to_rebase: {result.branch_to_rebase}",
        f"resolved_base: {result.resolved_base or '(未解決)'}",
        f"preferred_base_ref: {result.preferred_base_ref or '(未解決)'}",
        f"base_resolution: {result.base_resolution}",
        f"checkout_required: {'yes' if result.checkout_required else 'no'}",
        f"rebase_in_progress: {'yes' if result.rebase_in_progress else 'no'}",
        f"worktree_dirty: {'yes' if result.worktree_dirty else 'no'}",
    ]

    if result.pull_request is not None:
        lines.extend(
            [
                "pull_request:",
                f"  number: {result.pull_request.number}",
                f"  title: {result.pull_request.title}",
                f"  url: {result.pull_request.url}",
                f"  source_branch: {result.pull_request.source_branch}",
                f"  destination_branch: {result.pull_request.destination_branch}",
            ]
        )

    if result.conflicted_files:
        lines.append("conflicted_files:")
        for path in result.conflicted_files:
            lines.append(f"  - {path}")

    if result.comparison_candidates:
        lines.append("comparison_candidates:")
        for candidate in result.comparison_candidates:
            head_marker = " (remote HEAD)" if candidate.is_remote_head else ""
            lines.append(
                "  - "
                f"{candidate.branch}: ahead={candidate.ahead_of_candidate}, "
                f"behind={candidate.behind_candidate}{head_marker}"
            )

    if result.warnings:
        lines.append("warnings:")
        for message in result.warnings:
            lines.append(f"  - {message}")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """CLI 引数定義を組み立てる。"""

    parser = argparse.ArgumentParser(
        description="Git rebase 前に、PR 先や比較候補を整理して返します。",
    )
    parser.add_argument("--repo", default=".", help="対象リポジトリのパス")
    parser.add_argument("--remote", default="origin", help="対象リモート名")
    parser.add_argument("--branch", help="rebase 対象ブランチ。未指定時は現在ブランチ")
    parser.add_argument("--base", help="rebase 先ブランチ。指定時は PR 判定より優先")
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="出力形式",
    )
    return parser


def main() -> int:
    """CLI エントリーポイント。"""

    parser = build_parser()
    args = parser.parse_args()

    try:
        result = inspect_repository(
            repo=Path(args.repo).expanduser().resolve(),
            remote=args.remote,
            branch=args.branch,
            explicit_base=args.base,
        )
    except ContextError as error:
        print(str(error), file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(format_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())

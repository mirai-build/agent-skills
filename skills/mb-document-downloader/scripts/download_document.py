#!/usr/bin/env python3
"""指定 SaaS の文書を Markdown へ変換して保存する。"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from providers import DownloadError, DownloadedDocument, ProviderSpec
from providers.confluence import PROVIDER_SPEC as CONFLUENCE_PROVIDER


def build_provider_registry() -> dict[str, ProviderSpec]:
    """現在サポートする provider 一覧を返す。"""

    # provider を増やすときは、このレジストリへ追加すると CLI の選択肢へ反映される。
    return {
        CONFLUENCE_PROVIDER.name: CONFLUENCE_PROVIDER,
    }


def parse_provider_selection(
    argv: Sequence[str],
    provider_names: Sequence[str],
) -> tuple[str, bool]:
    """provider と一覧表示モードだけを先に確定する。"""

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--provider",
        choices=provider_names,
        default="confluence",
    )
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="利用可能な provider 一覧を表示して終了します。",
    )
    args, _ = parser.parse_known_args(list(argv))
    return args.provider, args.list_providers


def build_parser(
    provider_spec: ProviderSpec,
    provider_names: Sequence[str],
) -> argparse.ArgumentParser:
    """選択済み provider に合わせた完全な CLI を組み立てる。"""

    parser = argparse.ArgumentParser(
        description="指定 SaaS の文書を Markdown へ変換して保存します。",
    )
    parser.add_argument(
        "--provider",
        choices=provider_names,
        default=provider_spec.name,
        help="文書取得に使う SaaS provider。",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="保存先の Markdown パス。",
    )
    parser.add_argument(
        "--skip-metadata",
        action="store_true",
        help="タイトル直下のメタデータ行を省略します。",
    )
    provider_spec.configure_arguments(parser)
    return parser


def print_available_providers(provider_registry: dict[str, ProviderSpec]) -> None:
    """CLI で選べる provider を一覧表示する。"""

    print("利用可能な provider:")
    for provider_name in sorted(provider_registry):
        spec = provider_registry[provider_name]
        print(f"- {spec.name}: {spec.help_text}")


def build_markdown_document(
    document: DownloadedDocument,
    include_metadata: bool,
) -> str:
    """保存用 Markdown 全文を provider 非依存の形で構築する。"""

    lines = [f"# {document.title}", ""]

    if include_metadata:
        for label, value in document.metadata_items:
            stripped_value = value.strip()
            if stripped_value:
                lines.append(f"> {label}: {stripped_value}")
        if document.source_url:
            lines.append(f"> Source: {document.source_url}")
        exported_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        lines.append(f"> Exported At: {exported_at}")
        lines.append("")

    body = document.body_markdown.strip()
    if body:
        lines.append(body)

    return "\n".join(lines).rstrip() + "\n"


def write_document(output_path: Path, document_text: str) -> Path:
    """Markdown を目的の保存先へ書き込む。"""

    resolved = output_path.resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(document_text, encoding="utf-8")
    return resolved


def print_result(
    provider_spec: ProviderSpec,
    output_path: Path,
    document: DownloadedDocument,
) -> None:
    """CLI 実行結果を短く共有する。"""

    print(f"[OK] Provider: {provider_spec.display_name}")
    print(f"[OK] 保存しました: {output_path}")
    print(f"[OK] タイトル: {document.title}")
    for label, value in document.metadata_items:
        stripped_value = value.strip()
        if stripped_value:
            print(f"[OK] {label}: {stripped_value}")


def main(argv: Sequence[str] | None = None) -> int:
    """CLI のエントリーポイント。"""

    argv = list(sys.argv[1:] if argv is None else argv)
    provider_registry = build_provider_registry()
    provider_names = tuple(sorted(provider_registry))
    provider_name, list_providers = parse_provider_selection(argv, provider_names)

    if list_providers:
        print_available_providers(provider_registry)
        return 0

    provider_spec = provider_registry[provider_name]
    parser = build_parser(provider_spec, provider_names)
    args = parser.parse_args(argv)

    try:
        document = provider_spec.download(args)
        document_text = build_markdown_document(
            document=document,
            include_metadata=not args.skip_metadata,
        )
        output_path = write_document(Path(args.output), document_text)
        print_result(provider_spec, output_path, document)
        return 0
    except DownloadError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

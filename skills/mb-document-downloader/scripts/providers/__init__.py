"""文書ダウンロード provider 共通の型定義。"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from typing import Callable


class DownloadError(RuntimeError):
    """provider 実装から呼び出し元へ伝える業務エラー。"""


@dataclass(frozen=True)
class DownloadedDocument:
    """provider が返す保存前の文書データ。"""

    title: str
    body_markdown: str
    metadata_items: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    source_url: str | None = None


@dataclass(frozen=True)
class ProviderSpec:
    """CLI から切り替え可能な SaaS provider 定義。"""

    name: str
    display_name: str
    help_text: str
    configure_arguments: Callable[[argparse.ArgumentParser], None]
    download: Callable[[argparse.Namespace], DownloadedDocument]

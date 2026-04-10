"""Confluence provider の API 呼び出しと Markdown 変換をまとめる。"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import time
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

from providers import DownloadError, DownloadedDocument, ProviderSpec

DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_POLL_INTERVAL_SECONDS = 1.0
DEFAULT_POLL_TIMEOUT_SECONDS = 60.0
VOID_TAGS = {"br", "hr", "img", "input", "meta", "link"}
BLOCK_TAGS = {
    "article",
    "aside",
    "blockquote",
    "div",
    "dl",
    "fieldset",
    "figure",
    "figcaption",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hr",
    "li",
    "main",
    "nav",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "tbody",
    "thead",
    "tfoot",
    "tr",
    "ul",
}
INLINE_CONTAINER_TAGS = {
    "body",
    "document",
    "html",
    "section",
    "article",
    "header",
    "footer",
    "main",
    "span",
    "div",
}
IGNORED_TAGS = {"script", "style", "head", "meta", "link", "iframe"}
WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class PageReference:
    """ページ解決に必要な最小情報。"""

    page_id: str
    page_url: str | None
    site_base_url: str | None


@dataclass(frozen=True)
class ApiRoots:
    """Confluence API の v2 / v1 ルート URL 群。"""

    site_base_url: str | None
    v2_root: str
    rest_root: str


@dataclass(frozen=True)
class AuthConfig:
    """API 呼び出し時の認証設定。"""

    mode: str
    token: str
    email: str | None

    def authorization_header(self) -> str:
        """Atlassian API 向けの Authorization ヘッダー値を返す。"""

        if self.mode == "basic":
            if not self.email:
                raise DownloadError(
                    "basic 認証を使うには ATLASSIAN_EMAIL か --user-email が必要です。"
                )
            credentials = f"{self.email}:{self.token}".encode("utf-8")
            encoded = base64.b64encode(credentials).decode("ascii")
            return f"Basic {encoded}"

        return f"Bearer {self.token}"


@dataclass
class HtmlNode:
    """HTML を Markdown へ落とすための簡易 DOM ノード。"""

    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["HtmlChild"] = field(default_factory=list)


HtmlChild = HtmlNode | str


class HtmlTreeBuilder(HTMLParser):
    """HTML を扱いやすい木構造へ変換する。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.root = HtmlNode("document")
        self.stack: list[HtmlNode] = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = HtmlNode(tag=tag.lower(), attrs=_attrs_to_dict(attrs))
        self.stack[-1].children.append(node)
        if node.tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = HtmlNode(tag=tag.lower(), attrs=_attrs_to_dict(attrs))
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == normalized:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if data:
            self.stack[-1].children.append(data)

    def handle_entityref(self, name: str) -> None:
        self.handle_data(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.handle_data(f"&#{name};")


class MarkdownRenderer:
    """Confluence の view HTML を実用的な Markdown へ寄せて整形する。"""

    def __init__(self, link_base_url: str | None) -> None:
        self.link_base_url = link_base_url

    def render(self, html_text: str) -> str:
        """HTML 文字列全体を Markdown へ変換する。"""

        builder = HtmlTreeBuilder()
        builder.feed(html_text)
        builder.close()
        return cleanup_markdown(self._render_children(builder.root.children))

    def _render_children(self, children: list[HtmlChild], depth: int = 0) -> str:
        return "".join(self._render_node(child, depth=depth) for child in children)

    def _render_node(self, child: HtmlChild, depth: int = 0) -> str:
        if isinstance(child, str):
            return normalize_inline_text(child)

        tag = child.tag
        if tag in IGNORED_TAGS:
            return ""

        if tag in INLINE_CONTAINER_TAGS:
            if has_block_children(child):
                return self._render_children(child.children, depth=depth)
            text = self._render_inline_children(child.children).strip()
            return block(text) if text else ""

        if tag in {"strong", "b"}:
            return wrap_inline("**", self._render_inline_children(child.children))
        if tag in {"em", "i"}:
            return wrap_inline("_", self._render_inline_children(child.children))
        if tag == "code":
            if child.attrs.get("data-code-block") == "true":
                return self._render_children(child.children, depth=depth)
            text = extract_text(child).strip()
            return f"`{text}`" if text else ""
        if tag == "a":
            return self._render_link(child)
        if tag == "img":
            return self._render_image(child)
        if tag == "br":
            return "  \n"
        if tag == "hr":
            return "\n---\n\n"
        if tag in {"p", "figcaption"}:
            text = self._render_inline_children(child.children).strip()
            return block(text) if text else ""
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            text = self._render_inline_children(child.children).strip()
            return block(f"{'#' * level} {text}") if text else ""
        if tag == "blockquote":
            body = cleanup_markdown(self._render_children(child.children)).strip()
            return block(prefix_lines(body, "> ")) if body else ""
        if tag == "pre":
            return self._render_code_block(child)
        if tag == "ul":
            return self._render_list(child, ordered=False, depth=depth)
        if tag == "ol":
            return self._render_list(child, ordered=True, depth=depth)
        if tag == "table":
            return self._render_table(child)
        if tag == "input":
            return self._render_input(child)
        if tag in {"thead", "tbody", "tfoot", "tr"}:
            return self._render_children(child.children, depth=depth)
        if tag in {"th", "td"}:
            return self._render_inline_children(child.children)

        return self._render_children(child.children, depth=depth)

    def _render_inline_children(self, children: list[HtmlChild]) -> str:
        parts: list[str] = []
        for child in children:
            if isinstance(child, str):
                parts.append(normalize_inline_text(child))
                continue

            if child.tag in IGNORED_TAGS:
                continue
            if child.tag in {"p", "div"} and has_block_children(child):
                rendered = cleanup_markdown(self._render_children(child.children)).strip()
                if rendered:
                    parts.append(rendered)
                continue

            parts.append(self._render_node(child))

        return "".join(parts)

    def _render_link(self, node: HtmlNode) -> str:
        href = absolutize_url(node.attrs.get("href"), self.link_base_url)
        label = self._render_inline_children(node.children).strip() or href or ""
        if not href:
            return label
        return f"[{label}]({href})"

    def _render_image(self, node: HtmlNode) -> str:
        src = absolutize_url(node.attrs.get("src"), self.link_base_url)
        alt = node.attrs.get("alt", "").strip() or "image"
        if not src:
            return alt
        return f"![{alt}]({src})"

    def _render_input(self, node: HtmlNode) -> str:
        if node.attrs.get("type") != "checkbox":
            return ""
        return "[x] " if "checked" in node.attrs else "[ ] "

    def _render_code_block(self, node: HtmlNode) -> str:
        # code/panel マクロの中身を崩さないよう、pre 配下は空白を保ったまま扱う。
        code = extract_text(node, preserve_whitespace=True).strip("\n")
        if not code:
            return ""
        language = detect_code_language(node)
        fence = f"```{language}".rstrip()
        return f"\n{fence}\n{code}\n```\n\n"

    def _render_list(self, node: HtmlNode, ordered: bool, depth: int) -> str:
        items: list[str] = []
        item_number = 1

        for child in node.children:
            if not isinstance(child, HtmlNode) or child.tag != "li":
                continue

            prefix = f"{item_number}. " if ordered else "- "
            indent = "  " * depth
            continuation = " " * len(prefix)
            lead_parts: list[str] = []
            nested_parts: list[str] = []

            for grandchild in child.children:
                if isinstance(grandchild, HtmlNode) and grandchild.tag in {"ul", "ol"}:
                    nested_parts.append(self._render_list(
                        grandchild,
                        ordered=grandchild.tag == "ol",
                        depth=depth + 1,
                    ).rstrip())
                    continue

                if isinstance(grandchild, HtmlNode) and grandchild.tag in BLOCK_TAGS:
                    rendered = cleanup_markdown(self._render_node(grandchild, depth=depth + 1)).strip()
                    if rendered:
                        lead_parts.append(rendered)
                    continue

                lead_parts.append(self._render_node(grandchild, depth=depth + 1))

            lead = cleanup_markdown("".join(lead_parts)).strip()
            if not lead:
                lead = "[ ]"

            item_lines = lead.splitlines() or [lead]
            first_line = f"{indent}{prefix}{item_lines[0]}".rstrip()
            lines = [first_line]
            for extra_line in item_lines[1:]:
                lines.append(f"{indent}{continuation}{extra_line}".rstrip())
            for nested in nested_parts:
                lines.append(nested)

            items.append("\n".join(lines))
            item_number += 1

        if not items:
            return ""

        return "\n".join(items).rstrip() + "\n\n"

    def _render_table(self, node: HtmlNode) -> str:
        rows = collect_table_rows(node, self)
        if not rows:
            return ""

        header_index = next((index for index, (_, is_header) in enumerate(rows) if is_header), 0)
        header_cells = rows[header_index][0]
        data_rows = [cells for index, (cells, _) in enumerate(rows) if index != header_index]
        column_count = max(len(header_cells), *(len(row) for row in data_rows)) if data_rows else len(header_cells)
        padded_header = pad_cells(header_cells, column_count)
        padded_rows = [pad_cells(row, column_count) for row in data_rows]

        lines = [
            table_line(padded_header),
            table_line(["---"] * column_count),
        ]
        lines.extend(table_line(row) for row in padded_rows)
        return "\n".join(lines) + "\n\n"


class ConfluenceClient:
    """Confluence API を最小限の依存で叩くクライアント。"""

    def __init__(
        self,
        api_roots: ApiRoots,
        auth: AuthConfig,
        timeout_seconds: int,
        poll_interval_seconds: float,
        poll_timeout_seconds: float,
    ) -> None:
        self.api_roots = api_roots
        self.auth = auth
        self.timeout_seconds = timeout_seconds
        self.poll_interval_seconds = poll_interval_seconds
        self.poll_timeout_seconds = poll_timeout_seconds

    def fetch_page_markdown(self, page_id: str, page_url: str | None) -> tuple[dict[str, object], str]:
        """ページ本体を取得し、必要なら storage -> view 変換して Markdown 化する。"""

        page: dict[str, object] = {}
        html_value = ""
        try:
            page = self._get_page(page_id, body_format="view")
            html_value = extract_body_value(page.get("body"), "view")
        except DownloadError:
            # 一部環境では body-format=view が通らないため、storage + async convert へ退避する。
            page = {}

        if not html_value:
            storage_page = self._get_page(page_id, body_format="storage")
            storage_value = extract_body_value(storage_page.get("body"), "storage")
            if not storage_value:
                raise DownloadError("Confluence ページ本文を取得できませんでした。")
            html_value = self._convert_storage_to_view(storage_value, page_id)
            page = storage_page

        link_base_url = page_url or self.api_roots.site_base_url
        renderer = MarkdownRenderer(link_base_url=link_base_url)
        return page, renderer.render(html_value)

    def _get_page(self, page_id: str, body_format: str) -> dict[str, object]:
        params = urlencode({
            "body-format": body_format,
            "include-version": "true",
        })
        url = f"{self.api_roots.v2_root}/pages/{quote(page_id)}?{params}"
        return self._request_json("GET", url)

    def _convert_storage_to_view(self, storage_value: str, page_id: str) -> str:
        # body-format=view が使えないケースを吸収するため、公式の async convert API へ退避する。
        params = urlencode({"contentIdContext": page_id})
        payload = {
            "representation": "storage",
            "value": storage_value,
        }
        queued = self._request_json(
            "POST",
            f"{self.api_roots.rest_root}/contentbody/convert/async/view?{params}",
            payload=payload,
        )
        async_id = str(queued.get("asyncId", "")).strip()
        if not async_id:
            raise DownloadError("content body 変換ジョブの起動に失敗しました。")

        deadline = time.monotonic() + self.poll_timeout_seconds
        status_url = f"{self.api_roots.rest_root}/contentbody/convert/async/{quote(async_id)}"
        while time.monotonic() < deadline:
            result = self._request_json("GET", status_url)
            value = str(result.get("value", "")).strip()
            if value:
                return value

            status = str(result.get("status", "")).upper()
            if status in {"WORKING", "PENDING", "QUEUED", "RUNNING"}:
                time.sleep(self.poll_interval_seconds)
                continue

            error = str(result.get("error", "")).strip() or status or "UNKNOWN"
            raise DownloadError(f"content body 変換に失敗しました: {error}")

        raise DownloadError("content body 変換の完了待ちでタイムアウトしました。")

    def _request_json(
        self,
        method: str,
        url: str,
        payload: dict[str, object] | None = None,
    ) -> dict[str, object]:
        data = None
        headers = {
            "Accept": "application/json",
            "Authorization": self.auth.authorization_header(),
            "User-Agent": "mb-document-downloader/confluence/1.0",
        }
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except HTTPError as exc:
            message = exc.read().decode("utf-8", errors="replace")
            raise DownloadError(build_http_error_message(exc.code, url, message)) from exc
        except URLError as exc:
            raise DownloadError(f"Confluence API へ接続できませんでした: {exc}") from exc


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Confluence provider 固有の CLI 引数を追加する。"""

    parser.add_argument("--page-id", help="対象ページ ID。")
    parser.add_argument(
        "--page-url",
        help="対象ページ URL。pageId または /pages/<id>/ 形式を解釈します。",
    )
    parser.add_argument(
        "--base-url",
        help="Confluence サイトのベース URL。例: https://example.atlassian.net/wiki",
    )
    parser.add_argument(
        "--cloud-id",
        help="scoped API token を使う場合の Atlassian Cloud ID。",
    )
    parser.add_argument(
        "--site-base-url",
        help="相対リンクを絶対 URL 化するための公開ベース URL。scoped token でもサイト URL が分かる場合に指定します。",
    )
    parser.add_argument(
        "--user-email",
        help="basic 認証に使う Atlassian アカウントのメールアドレス。",
    )
    parser.add_argument(
        "--auth-mode",
        choices=("auto", "basic", "bearer"),
        default="auto",
        help="認証方式。auto は ATLASSIAN_EMAIL / ATLASSIAN_USER_EMAIL があれば basic、それ以外は bearer を使います。",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"HTTP タイムアウト秒数。既定: {DEFAULT_TIMEOUT_SECONDS}",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=float,
        default=DEFAULT_POLL_INTERVAL_SECONDS,
        help=f"非同期変換 API のポーリング間隔。既定: {DEFAULT_POLL_INTERVAL_SECONDS}",
    )
    parser.add_argument(
        "--poll-timeout-seconds",
        type=float,
        default=DEFAULT_POLL_TIMEOUT_SECONDS,
        help=f"非同期変換 API の待ち時間上限。既定: {DEFAULT_POLL_TIMEOUT_SECONDS}",
    )


def download_document(args: argparse.Namespace) -> DownloadedDocument:
    """Confluence のページを取得し、共通出力用の文書データへ変換する。"""

    page_reference = resolve_page_reference(args.page_id, args.page_url)
    site_base_url = (
        normalize_site_base_url(args.site_base_url)
        or normalize_site_base_url(args.base_url)
        or page_reference.site_base_url
    )
    api_roots = resolve_api_roots(
        cloud_id=args.cloud_id,
        base_url=args.base_url,
        site_base_url=site_base_url,
        page_reference=page_reference,
    )
    auth = resolve_auth_config(
        auth_mode=args.auth_mode,
        user_email=args.user_email,
    )
    client = ConfluenceClient(
        api_roots=api_roots,
        auth=auth,
        timeout_seconds=args.timeout_seconds,
        poll_interval_seconds=args.poll_interval_seconds,
        poll_timeout_seconds=args.poll_timeout_seconds,
    )
    page, markdown_body = client.fetch_page_markdown(
        page_id=page_reference.page_id,
        page_url=page_reference.page_url,
    )

    metadata_items = [("Page ID", page_reference.page_id)]
    version = extract_version_number(page.get("version"))
    if version:
        metadata_items.append(("Version", version))

    title = str(page.get("title", "")).strip() or f"Confluence Page {page_reference.page_id}"
    return DownloadedDocument(
        title=title,
        body_markdown=markdown_body,
        metadata_items=tuple(metadata_items),
        source_url=build_source_url(
            page=page,
            explicit_page_url=page_reference.page_url,
            site_base_url=site_base_url,
        ),
    )


def resolve_page_reference(page_id: str | None, page_url: str | None) -> PageReference:
    """ページ ID / URL の組み合わせから参照情報を確定する。"""

    if page_url:
        parsed = parse_page_url(page_url)
        if page_id and parsed.page_id != page_id:
            raise DownloadError("--page-id と --page-url が別のページを指しています。")
        return PageReference(
            page_id=parsed.page_id,
            page_url=page_url,
            site_base_url=parsed.site_base_url,
        )

    if not page_id:
        raise DownloadError("--page-id か --page-url のどちらかを指定して下さい。")

    return PageReference(page_id=str(page_id), page_url=None, site_base_url=None)


def resolve_api_roots(
    cloud_id: str | None,
    base_url: str | None,
    site_base_url: str | None,
    page_reference: PageReference,
) -> ApiRoots:
    """Cloud ID またはサイト URL から API ルートを構築する。"""

    if cloud_id:
        api_base = f"https://api.atlassian.com/ex/confluence/{cloud_id.strip()}/wiki"
        return ApiRoots(
            site_base_url=site_base_url or page_reference.site_base_url,
            v2_root=f"{api_base}/api/v2",
            rest_root=f"{api_base}/rest/api",
        )

    normalized_base = (
        normalize_site_base_url(base_url)
        or site_base_url
        or page_reference.site_base_url
    )
    if not normalized_base:
        raise DownloadError(
            "--cloud-id を使わない場合は --base-url か --page-url で Confluence のサイト URL を特定して下さい。"
        )

    return ApiRoots(
        site_base_url=normalized_base,
        v2_root=f"{normalized_base}/api/v2",
        rest_root=f"{normalized_base}/rest/api",
    )


def resolve_auth_config(auth_mode: str, user_email: str | None) -> AuthConfig:
    """環境変数と引数から認証方式を決める。"""

    token = os.environ.get("ATLASSIAN_TOKEN", "").strip()
    if not token:
        raise DownloadError(
            "ATLASSIAN_TOKEN が見つかりません。必要なら `set -a; source ./.envrc; set +a` を先に実行して下さい。"
        )

    email = (
        user_email
        or os.environ.get("ATLASSIAN_EMAIL")
        or os.environ.get("ATLASSIAN_USER_EMAIL")
        or None
    )

    if auth_mode == "auto":
        resolved_mode = "basic" if email else "bearer"
    else:
        resolved_mode = auth_mode

    return AuthConfig(mode=resolved_mode, token=token, email=email)


def parse_page_url(page_url: str) -> PageReference:
    """Confluence のページ URL から pageId とサイト URL を抜き出す。"""

    parsed = urlparse(page_url)
    if not parsed.scheme or not parsed.netloc:
        raise DownloadError("page-url は完全な URL で指定して下さい。")

    query = parse_qs(parsed.query)
    if query.get("pageId"):
        page_id = query["pageId"][0]
    else:
        match = re.search(r"/pages/(\d+)(?:/|$)", parsed.path)
        if not match:
            raise DownloadError(
                "page-url から pageId を解釈できませんでした。`?pageId=` または `/pages/<id>/` を含む URL を指定して下さい。"
            )
        page_id = match.group(1)

    base_path = "/wiki" if parsed.path.startswith("/wiki/") or parsed.path == "/wiki" else ""
    site_base_url = f"{parsed.scheme}://{parsed.netloc}{base_path}"
    return PageReference(page_id=page_id, page_url=page_url, site_base_url=site_base_url)


def normalize_site_base_url(url: str | None) -> str | None:
    """受け取った URL を Confluence サイトのベース URL へ正規化する。"""

    if not url:
        return None

    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise DownloadError("base-url / site-base-url は完全な URL で指定して下さい。")

    path = parsed.path.rstrip("/")
    if path.endswith("/api/v2"):
        path = path[: -len("/api/v2")]
    if path.endswith("/rest/api"):
        path = path[: -len("/rest/api")]
    if path.endswith("/wiki/rest/api"):
        path = path[: -len("/wiki/rest/api")]
    if not path and parsed.netloc.endswith("atlassian.net"):
        path = "/wiki"

    return f"{parsed.scheme}://{parsed.netloc}{path}"


def extract_body_value(body: object, representation: str) -> str:
    """Confluence の body 形式差を吸収して本文文字列だけを取り出す。"""

    if not isinstance(body, dict):
        return ""

    candidate = body.get(representation)
    if isinstance(candidate, dict):
        return str(candidate.get("value", "")).strip()

    if body.get("representation") == representation:
        return str(body.get("value", "")).strip()

    return ""


def build_source_url(
    page: dict[str, object],
    explicit_page_url: str | None,
    site_base_url: str | None,
) -> str | None:
    """元ページへの URL を組み立てる。"""

    if explicit_page_url:
        return explicit_page_url

    links = page.get("_links")
    if isinstance(links, dict):
        base = str(links.get("base", "")).strip() or site_base_url or ""
        webui = str(links.get("webui", "")).strip()
        if base and webui:
            return urljoin(base.rstrip("/") + "/", webui.lstrip("/"))

    if site_base_url and page.get("id"):
        return f"{site_base_url}/pages/viewpage.action?pageId={page['id']}"
    return None


def extract_version_number(version: object) -> str:
    """レスポンスからバージョン番号だけを安全に抜き出す。"""

    if isinstance(version, dict) and "number" in version:
        return str(version["number"])
    return ""


def build_http_error_message(status_code: int, url: str, message: str) -> str:
    """HTTP エラー時に次の調査へ進みやすい文面を返す。"""

    compact_message = WHITESPACE_RE.sub(" ", message).strip()
    if status_code == 401:
        return (
            "Confluence API が 401 Unauthorized を返しました。"
            " basic 認証が必要なら ATLASSIAN_EMAIL / --user-email を設定し、"
            " scoped token の場合は --cloud-id と api.atlassian.com 経由の URL 構成を確認して下さい。"
            f" url={url} body={compact_message}"
        )
    return f"Confluence API が HTTP {status_code} を返しました: url={url} body={compact_message}"


def _attrs_to_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    """HTMLParser の attrs を扱いやすい辞書へ変換する。"""

    normalized: dict[str, str] = {}
    for key, value in attrs:
        normalized[key.lower()] = "" if value is None else value
    return normalized


def has_block_children(node: HtmlNode) -> bool:
    """直下の子に block 要素が含まれるかをざっくり判定する。"""

    for child in node.children:
        if isinstance(child, HtmlNode) and child.tag in BLOCK_TAGS:
            return True
    return False


def normalize_inline_text(text: str) -> str:
    """inline 用に空白を潰しつつ HTML 実体参照を戻す。"""

    return WHITESPACE_RE.sub(" ", unescape(text))


def extract_text(node: HtmlNode, preserve_whitespace: bool = False) -> str:
    """ノード配下のプレーンテキストを再帰的に連結する。"""

    fragments: list[str] = []
    for child in node.children:
        if isinstance(child, str):
            fragments.append(unescape(child) if preserve_whitespace else normalize_inline_text(child))
            continue
        if child.tag in IGNORED_TAGS:
            continue
        fragments.append(extract_text(child, preserve_whitespace=preserve_whitespace))
    return "".join(fragments)


def wrap_inline(marker: str, text: str) -> str:
    """空文字を避けながら inline 装飾を付ける。"""

    stripped = text.strip()
    return f"{marker}{stripped}{marker}" if stripped else ""


def block(text: str) -> str:
    """block 要素として 1 段落ぶんの改行を付ける。"""

    stripped = text.strip()
    return f"{stripped}\n\n" if stripped else ""


def prefix_lines(text: str, prefix: str) -> str:
    """各行へ同じ接頭辞を付ける。"""

    return "\n".join(f"{prefix}{line}" if line else prefix.rstrip() for line in text.splitlines())


def detect_code_language(node: HtmlNode) -> str:
    """class 名から fenced code block の言語ヒントを拾う。"""

    classes = " ".join(filter(None, [
        node.attrs.get("class"),
        node.attrs.get("data-language"),
    ]))
    match = re.search(r"(?:language|lang)[-: ]([a-zA-Z0-9_+-]+)", classes)
    return match.group(1) if match else ""


def collect_table_rows(node: HtmlNode, renderer: MarkdownRenderer) -> list[tuple[list[str], bool]]:
    """table 配下の tr/th/td を Markdown 表へ落とすために抽出する。"""

    rows: list[tuple[list[str], bool]] = []

    def walk(current: HtmlNode) -> None:
        if current.tag == "tr":
            cells: list[str] = []
            is_header = False
            for child in current.children:
                if not isinstance(child, HtmlNode) or child.tag not in {"th", "td"}:
                    continue
                rendered = cleanup_markdown(renderer._render_inline_children(child.children)).strip()
                cells.append(escape_table_cell(rendered or " "))
                is_header = is_header or child.tag == "th"
            if cells:
                rows.append((cells, is_header))
            return

        for child in current.children:
            if isinstance(child, HtmlNode):
                walk(child)

    walk(node)
    return rows


def pad_cells(cells: list[str], count: int) -> list[str]:
    """行ごとの列数をそろえる。"""

    return cells + [" "] * max(0, count - len(cells))


def table_line(cells: list[str]) -> str:
    """Markdown table の 1 行を組み立てる。"""

    return "| " + " | ".join(cells) + " |"


def escape_table_cell(text: str) -> str:
    """表セル内で解釈が崩れやすい文字をエスケープする。"""

    normalized = WHITESPACE_RE.sub(" ", text).strip()
    return normalized.replace("|", r"\|")


def cleanup_markdown(text: str) -> str:
    """変換後の改行を読みやすい範囲へ整える。"""

    lines = text.splitlines()
    cleaned: list[str] = []
    blank_count = 0
    for raw_line in lines:
        line = raw_line.rstrip()
        if not line:
            blank_count += 1
            if blank_count <= 1:
                cleaned.append("")
            continue
        blank_count = 0
        cleaned.append(line)

    return "\n".join(cleaned).strip() + ("\n" if cleaned else "")


def absolutize_url(url: str | None, link_base_url: str | None) -> str:
    """相対リンクを元ページ基準の絶対 URL へ寄せる。"""

    if not url:
        return ""
    if not link_base_url:
        return url
    return urljoin(link_base_url, url)


PROVIDER_SPEC = ProviderSpec(
    name="confluence",
    display_name="Confluence",
    help_text="Confluence ページを Atlassian API で取得して Markdown 化します。",
    configure_arguments=add_arguments,
    download=download_document,
)

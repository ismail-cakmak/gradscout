#!/usr/bin/env python3
"""
Crawl a page with Crawl4AI and print extracted content for agent use.

Usage:
  python3 fetch_page.py <url> [--max-chars=4000]
  python3 fetch_page.py <url> --json [--max-links=200] [--session=name]

Exit code 0: success
Exit code 1: crawl failed or returned insufficient content
"""

import argparse
import asyncio
import inspect
import json
import re
import sys
from html import unescape
from typing import Any


INSTALL_HINT = "pip install crawl4ai && crawl4ai-setup"

try:
    from crawl4ai import AsyncWebCrawler
    try:
        from crawl4ai import BrowserConfig, CrawlerRunConfig
    except ImportError:
        from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
except ImportError:
    AsyncWebCrawler = None
    BrowserConfig = None
    CrawlerRunConfig = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--max-chars", type=int, default=4000)
    parser.add_argument("--max-links", type=int, default=200)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--links-only", action="store_true")
    parser.add_argument("--session")
    parser.add_argument("--wait-for")
    parser.add_argument("--css-selector")
    parser.add_argument("--page-timeout-ms", type=int, default=30000)
    parser.add_argument("--no-wait", action="store_true", help="Skip waiting for networkidle")
    return parser.parse_args()


def build_kwargs(factory: Any, values: dict[str, Any]) -> dict[str, Any]:
    signature = inspect.signature(factory)
    return {
        key: value
        for key, value in values.items()
        if value is not None and key in signature.parameters
    }


def truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... truncated for token efficiency ...]"


def normalize_markdown(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def extract_markdown(result: Any) -> str:
    markdown_v2 = getattr(result, "markdown_v2", None)
    candidates = [
        getattr(result, "fit_markdown", None),
        getattr(markdown_v2, "fit_markdown", None) if markdown_v2 else None,
        getattr(markdown_v2, "raw_markdown", None) if markdown_v2 else None,
        getattr(result, "markdown", None),
        getattr(result, "cleaned_html", None),
        getattr(result, "html", None),
    ]

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return normalize_markdown(candidate)
    return ""


def extract_title(result: Any) -> str:
    metadata = getattr(result, "metadata", None) or {}
    if isinstance(metadata, dict):
        for key in ("title", "og:title", "twitter:title"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    html = getattr(result, "cleaned_html", None) or getattr(result, "html", None) or ""
    match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return unescape(re.sub(r"\s+", " ", match.group(1))).strip()
    return ""


def normalize_links(result_links: Any, bucket: str, max_links: int) -> list[dict[str, str]]:
    if not isinstance(result_links, dict):
        return []

    seen: set[str] = set()
    items: list[dict[str, str]] = []
    for raw_link in result_links.get(bucket, []):
        if not isinstance(raw_link, dict):
            continue
        href = (raw_link.get("href") or "").strip()
        if not href or href in seen:
            continue
        seen.add(href)
        items.append(
            {
                "href": href,
                "text": (raw_link.get("text") or "").strip(),
                "title": (raw_link.get("title") or "").strip(),
                "base_domain": (raw_link.get("base_domain") or "").strip(),
            }
        )
        if len(items) >= max_links:
            break
    return items


async def run_crawl(args: argparse.Namespace) -> dict[str, Any]:
    if AsyncWebCrawler is None or BrowserConfig is None or CrawlerRunConfig is None:
        raise RuntimeError(f"Crawl4AI is not installed. Run: {INSTALL_HINT}")

    browser_config = BrowserConfig(
        **build_kwargs(
            BrowserConfig,
            {
                "headless": True,
                "verbose": False,
            },
        )
    )
    run_config = CrawlerRunConfig(
        **build_kwargs(
            CrawlerRunConfig,
            {
                "cache_mode": "bypass",
                "session_id": args.session,
                "wait_for": args.wait_for,
                "css_selector": args.css_selector,
                "wait_until": None if args.no_wait else "networkidle",
                "page_timeout": args.page_timeout_ms,
                "scan_full_page": True,
                "process_iframes": True,
                "remove_overlay_elements": True,
                "delay_before_return_html": 0.75,
                "word_count_threshold": 1,
            },
        )
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=args.url, config=run_config)

    if not getattr(result, "success", False):
        error_message = getattr(result, "error_message", None) or "unknown Crawl4AI failure"
        raise RuntimeError(error_message)

    markdown = truncate(extract_markdown(result), args.max_chars)
    links = getattr(result, "links", {}) or {}
    return {
        "success": True,
        "url": getattr(result, "url", None) or args.url,
        "title": extract_title(result),
        "markdown": markdown,
        "internal_links": normalize_links(links, "internal", args.max_links),
        "external_links": normalize_links(links, "external", args.max_links),
    }


def main() -> None:
    args = parse_args()

    try:
        payload = asyncio.run(run_crawl(args))
        text_output = payload["markdown"].strip()
        if args.links_only:
            print(
                json.dumps(
                    {
                        "url": payload["url"],
                        "title": payload["title"],
                        "internal_links": payload["internal_links"],
                        "external_links": payload["external_links"],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return

        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return

        if not text_output:
            print("FETCH_FAILED: Crawl returned no usable text.", file=sys.stderr)
            sys.exit(1)

        if len(text_output) < 100:
            print(
                f"FETCH_FAILED: Page returned insufficient text ({len(text_output)} chars).",
                file=sys.stderr,
            )
            sys.exit(1)

        print(text_output)
    except Exception as exc:
        print(f"FETCH_FAILED: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

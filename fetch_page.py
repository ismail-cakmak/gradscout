#!/usr/bin/env python3
"""
Fetches a URL and extracts clean text content for LLM processing.
Usage: python3 fetch_page.py <url> [--max-chars=4000]
Exit code 0: success (text on stdout)
Exit code 1: fetch failed (agent should fall back to browser)
"""
import sys
import re
import requests
from bs4 import BeautifulSoup


def fetch_and_extract(url, max_chars=4000):
    """Fetch URL and return clean main-content text."""
    resp = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml",
        },
        timeout=20,
        allow_redirects=True,
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove noise elements
    for tag in soup.find_all(
        ["script", "style", "nav", "footer", "header", "noscript", "svg", "iframe", "form"]
    ):
        tag.decompose()

    # Remove common noisy classes/ids
    for selector in [
        "[class*='cookie']", "[class*='banner']", "[class*='popup']",
        "[class*='sidebar']", "[class*='menu']", "[class*='breadcrumb']",
        "[id*='cookie']", "[id*='banner']", "[id*='popup']",
        "[id*='sidebar']", "[id*='menu']",
    ]:
        for el in soup.select(selector):
            el.decompose()

    # Find main content area
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id="content")
        or soup.find(id="main-content")
        or soup.find(class_="content")
        or soup.find(attrs={"role": "main"})
    )

    if main:
        text = main.get_text(separator="\n", strip=True)
    else:
        text = soup.body.get_text(separator="\n", strip=True) if soup.body else ""

    # Clean up
    text = re.sub(r"\n{3,}", "\n\n", text)  # collapse blank lines
    text = re.sub(r"[ \t]{2,}", " ", text)  # collapse spaces
    text = "\n".join(line for line in text.split("\n") if len(line.strip()) > 1)  # remove single-char lines

    # Truncate if too long
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[... truncated for token efficiency ...]"

    return text


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_page.py <url> [--max-chars=4000]", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    max_chars = 4000
    for arg in sys.argv[2:]:
        if arg.startswith("--max-chars="):
            max_chars = int(arg.split("=")[1])

    try:
        text = fetch_and_extract(url, max_chars)
        if len(text.strip()) < 100:
            print(f"FETCH_FAILED: Page returned insufficient text ({len(text.strip())} chars). Site may require JavaScript.", file=sys.stderr)
            sys.exit(1)
        print(text)
    except requests.exceptions.RequestException as e:
        print(f"FETCH_FAILED: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"FETCH_FAILED: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

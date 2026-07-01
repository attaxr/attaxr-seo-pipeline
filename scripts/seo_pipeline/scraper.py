#!/usr/bin/env python3
"""Scrape competitor articles for SEO pipeline keywords.

Usage:
    python -m seo_pipeline <keyword> [<keyword>...] [--outdir <path>]
    python -m seo_pipeline --from-json keywords.json [--outdir <path>]

Primary: Browser Use Cloud SDK v3
  (https://docs.browser-use.com/cloud/quickstart)
  AI agent searches Google, navigates results, extracts full article text.
  Requires BROWSER_USE_API_KEY env var (set in .env via python scripts/setup.py).

Fallback: DuckDuckGo HTML search (URL discovery only)
  If Browser Use is unavailable, searches DuckDuckGo and logs found URLs.
  Does NOT fetch article content via HTTP — modern sites block plain requests.
  If DuckDuckGo search itself fails, the pipeline stops immediately.

Both methods failed -> exits code 1.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _proxy_kwargs() -> dict:
    """Read Browser Use proxy config from env vars. Returns kwargs for client.run()."""
    country = os.environ.get("BROWSER_USE_PROXY_COUNTRY", "").strip().lower() or None
    if country == "none":
        country = None
        disable_proxy = True
    else:
        disable_proxy = False

    host = os.environ.get("BROWSER_USE_CUSTOM_PROXY_HOST", "").strip()
    kwargs: dict = {}
    if host:
        kwargs["proxy_country_code"] = None  # custom proxy overrides residential
        custom: dict = {"host": host}
        port = os.environ.get("BROWSER_USE_CUSTOM_PROXY_PORT", "").strip()
        if port:
            custom["port"] = int(port)
        user = os.environ.get("BROWSER_USE_CUSTOM_PROXY_USERNAME", "").strip()
        if user:
            custom["username"] = user
        pw = os.environ.get("BROWSER_USE_CUSTOM_PROXY_PASSWORD", "").strip()
        if pw:
            custom["password"] = pw
        # ponytail: custom_proxy goes via **extra; SDK passes it to sessions.create()
        kwargs["custom_proxy"] = custom
    elif disable_proxy:
        kwargs["proxy_country_code"] = None
    elif country:
        kwargs["proxy_country_code"] = country
    # else: no proxy configured at all — SDK default (US residential)
    return kwargs


def _slugify(text: str) -> str:
    """Strip URL scheme, replace non-word chars with hyphens, truncate to 80 chars."""
    s = re.sub(r"^https?://", "", text)
    s = re.sub(r"[^\w/]", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:80].replace("/", "_")


def _search_duckduckgo(query: str, limit: int = 5) -> list[str]:
    """Search DuckDuckGo HTML, return up to *limit* result URLs."""
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8", errors="replace")
    except Exception as exc:
        sys.stderr.write(f"  DuckDuckGo search error: {exc}\n")
        return []
    urls = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"', data)
    return urls[:limit]


async def _browser_use_articles(keyword: str, api_key: str) -> list[dict]:
    """Use Browser Use Cloud SDK v3 to search + extract articles.

    Returns list of {title, url, content} dicts, or empty list.
    Raises ImportError if browser-use-sdk is not installed.
    """
    from browser_use_sdk.v3 import AsyncBrowserUse  # noqa: PLC0415

    client = AsyncBrowserUse(api_key=api_key)
    task = (
        f"Search Google for '{keyword}'. From the results, find the 5 most relevant "
        f"informational articles — skip ads, shopping pages, forums, and videos. "
        f"Visit each article and read the full text. "
        f"Return ONLY a JSON array of objects with these exact keys: "
        f"title (string), url (string), content (full article text as string). "
        f"Do not wrap in markdown fences. "
        'Example: [{"title":"Example","url":"https://...","content":"Full text..."}]'
    )

    result = await client.run(task, **_proxy_kwargs())
    if not result or not result.output:
        return []

    raw = result.output.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    try:
        articles_raw: list[dict] = json.loads(raw)
    except json.JSONDecodeError:
        return []

    validated: list[dict] = []
    for a in articles_raw:
        title = (a.get("title") or "").strip()
        content = (a.get("content") or "").strip()
        url = (a.get("url") or "").strip()
        if content and len(content.split()) >= 100:
            validated.append({"title": title or keyword, "url": url, "content": content})
    return validated


def _save_articles(articles: list[dict], outdir: str) -> int:
    """Write articles to outdir as markdown files. Returns count saved."""
    saved = 0
    for art in articles:
        title = art["title"]
        url = art["url"]
        content = art["content"]
        fname = f"{_slugify(title)}.md"
        fpath = os.path.join(outdir, fname)
        base, ext = os.path.splitext(fpath)
        counter = 1
        while os.path.exists(fpath):
            fpath = f"{base}_{counter}{ext}"
            counter += 1
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n> Source: {url}\n\n{content}\n")
        saved += 1
        sys.stdout.write(f"  OK: {len(content.split())}w - {title[:60]}\n")
        sys.stdout.flush()
    return saved


def _save_urls(urls: list[str], keyword: str, outdir: str) -> None:
    """Write discovered URLs to a JSON file for the user."""
    path = os.path.join(outdir, f"_duckduckgo_urls_{_slugify(keyword)}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"keyword": keyword, "urls": urls}, f, indent=2)
    sys.stdout.write(f"  URLs saved to {path}\n")
    sys.stdout.flush()


def scrape_keyword(keyword: str, api_key: str, outdir: str) -> bool:
    """Scrape articles for one keyword. Returns True if at least one saved.

    Primary: Browser Use Cloud SDK (full AI-powered extraction).
    Fallback: DuckDuckGo search (URL discovery only — no content fetch).

    If DuckDuckGo search fails, the pipeline stops immediately.
    """
    sys.stdout.write(f"\n=== Scraping: {keyword} ===\n")
    sys.stdout.flush()

    if api_key:
        sys.stdout.write("  Trying Browser Use Cloud...\n")
        sys.stdout.flush()
        try:
            articles = asyncio.run(_browser_use_articles(keyword, api_key))
        except ImportError:
            sys.stdout.write("  browser-use-sdk not installed. Skipping.\n")
            articles = None
        except Exception as exc:
            sys.stdout.write(f"  Browser Use error: {exc}\n")
            articles = None
        sys.stdout.flush()

        if articles:
            saved = _save_articles(articles, outdir)
            if saved > 0:
                return True

    # ponytail: DDG HTML endpoint works; fetching article content via HTTP does not.
    # We discover URLs so the agent can feed them to Browser Use on the next run.
    sys.stdout.write("  Falling back to DuckDuckGo search...\n")
    sys.stdout.flush()
    urls = _search_duckduckgo(keyword)
    if not urls:
        sys.stderr.write(f"  FAILED: DuckDuckGo returned no results for '{keyword}'. Stopping.\n")
        return False

    sys.stdout.write(f"  DuckDuckGo found {len(urls)} URLs:\n")
    for u in urls:
        sys.stdout.write(f"    - {u}\n")
    sys.stdout.write("  (Content not fetched via HTTP — modern sites block plain requests.\n")
    sys.stdout.write("   Set BROWSER_USE_API_KEY to extract full articles.)\n")
    sys.stdout.flush()
    _save_urls(urls, keyword, outdir)
    return False


def _auto_load_dotenv() -> None:
    """Load .env from repo root (walks up from scripts/seo_pipeline/scraper.py → repo root)."""
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())


def main() -> None:
    """CLI entry: scrape articles for given keywords, writing to pipeline_data/articles."""
    _auto_load_dotenv()

    import argparse

    parser = argparse.ArgumentParser(description="Scrape competitor articles for SEO keywords.")
    parser.add_argument("keywords", nargs="*", help="Keywords to scrape")
    parser.add_argument("--outdir", help="Output directory for articles")
    parser.add_argument("--from-json", help="JSON file with keyword objects")
    args = parser.parse_args()

    keywords: list[str] = list(args.keywords)

    if args.from_json:
        with open(args.from_json) as f:
            data = json.load(f)
        keywords.extend(
            item.get("term", "").strip() for item in data if item.get("term")
        )

    if not keywords:
        print("ERROR: No keywords provided.", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("BROWSER_USE_API_KEY", "")
    base_dir = os.environ.get(
        "SEO_PIPELINE_DIR", os.path.join(os.getcwd(), "pipeline_data"),
    )
    articles_dir = os.path.join(args.outdir or base_dir, "articles")
    os.makedirs(articles_dir, exist_ok=True)

    success = 0
    failed = 0

    for kw in keywords:
        if scrape_keyword(kw, api_key, articles_dir):
            success += 1
        else:
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Scraping complete: {success} OK, {failed} failed")

    if failed > 0 and success == 0:
        print(
            "ERROR: No articles scraped for any keyword. "
            "Check BROWSER_USE_API_KEY or internet connection.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Interactive setup for SEO Pipeline with Browser Use Cloud SDK.

Usage:
    python scripts/setup.py

Guides through:
  1. Obtaining and setting BROWSER_USE_API_KEY (required for scraping)
  2. Installing browser-use-sdk
  3. Creating .env configuration
"""
from __future__ import annotations

import getpass
import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    print("=" * 60)
    print("SEO Pipeline \u2014 Setup")
    print("=" * 60)

    repo_root = Path(__file__).resolve().parent.parent
    env_path = repo_root / ".env"
    env_vars: dict[str, str] = {}

    if env_path.exists():
        print(f"\nFound existing {env_path}")
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()

    # Browser Use API Key (REQUIRED for scraping)
    print("\n--- Browser Use API Key (REQUIRED for scraping) ---")
    print("  The scraper uses Browser Use Cloud SDK to search Google and")
    print("  extract full article text. Without this key, only URL discovery")
    print("  via DuckDuckGo works (no article content).")
    print()
    print("  Get one free at: https://cloud.browser-use.com/settings?tab=api-keys")
    print("  Your key starts with 'bu_'")

    current_key = env_vars.get("BROWSER_USE_API_KEY", "")
    if current_key:
        masked = current_key[:8] + "..." + current_key[-4:]
        print(f"  Current: {masked}")
        change = input("  Change it? [y/N]: ").strip().lower()
        if change == "y":
            current_key = getpass.getpass("  Enter new API key: ").strip()
    else:
        print("  ! No API key found \u2014 the pipeline will prompt you for it when running.")
        current_key = getpass.getpass(
            "  Enter your Browser Use API key (leave empty to set later): "
        ).strip()

    env_vars["BROWSER_USE_API_KEY"] = current_key

    # Install browser-use-sdk
    print("\n--- Browser Use SDK ---")
    try:
        import browser_use_sdk  # noqa: F401

        print("  browser-use-sdk is already installed.")
    except ImportError:
        print("  Installing browser-use-sdk...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "browser-use-sdk"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            print("  Installed successfully.")
        else:
            print(f"  Install failed: {result.stderr.strip()}")
            print("  Retry manually: pip install browser-use-sdk")

    # Optional proxy config
    print("\n--- Browser Use Proxy (optional) ---")
    print("  A US residential proxy is active by default. You can change")
    print("  the country or provide a custom proxy (HTTP/SOCKS5).")
    print("  Leave everything empty to keep defaults.")
    print()

    current_proxy_country = env_vars.get("BROWSER_USE_PROXY_COUNTRY", "")
    if current_proxy_country:
        print(f"  Current country: {current_proxy_country}")

    change_proxy = input("  Configure proxy? [y/N]: ").strip().lower()
    if change_proxy == "y":
        country = input("  Country code (ISO 3166-1 alpha-2, e.g. de, gb, jp) [us]: ").strip()
        if country:
            env_vars["BROWSER_USE_PROXY_COUNTRY"] = country

        custom_proxy = input("  Use custom proxy instead of residential? [y/N]: ").strip().lower()
        if custom_proxy == "y":
            env_vars.pop("BROWSER_USE_PROXY_COUNTRY", None)
            env_vars["BROWSER_USE_CUSTOM_PROXY_HOST"] = input("  Proxy host: ").strip()
            env_vars["BROWSER_USE_CUSTOM_PROXY_PORT"] = input("  Proxy port [8080]: ").strip() or "8080"
            user = input("  Username (leave empty if none): ").strip()
            if user:
                env_vars["BROWSER_USE_CUSTOM_PROXY_USERNAME"] = user
                # ponytail: password lives in .env, no redaction needed unless user asks
                pw = input("  Password: ").strip()
                if pw:
                    env_vars["BROWSER_USE_CUSTOM_PROXY_PASSWORD"] = pw

    # Persist to .env — preserves existing vars, overwrites what we touched
    lines = [
        "# SEO Pipeline Configuration",
        "# Get a free API key at: https://cloud.browser-use.com/settings?tab=api-keys",
    ]
    for key, val in env_vars.items():
        if val:
            lines.append(f"{key}={val}")
    lines.append("")
    env_path.write_text("\n".join(lines))
    os.chmod(env_path, 0o600)  # ponytail: readable by owner only

    print(f"\n  Saved configuration to {env_path}")
    print("\n" + "=" * 60)
    print("Setup complete!")
    print()
    print("  Next steps:")
    print("  1. Run: python -m seo_pipeline --from-json keywords.json")
    print("  2. Or run the full pipeline per AGENTS.md")
    print("=" * 60)


if __name__ == "__main__":
    main()

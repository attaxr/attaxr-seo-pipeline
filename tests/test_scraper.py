"""Unit tests for the SEO pipeline scraper module.

Tests pure functions in scoper.py that are isolatable (no network).
"""
from __future__ import annotations

import json

import pytest

from seo_pipeline.scraper import (
    _proxy_kwargs,
    _save_articles,
    _save_urls,
    _slugify,
)


# ── _slugify ──

_SLUGIFY_CASES = [
    ("https://example.com/page", "example-com_page"),
    ("foo bar baz", "foo-bar-baz"),
    ("a!!b??c", "a-b-c"),
    ("hello...world", "hello-world"),
    ("", ""),
    ("---hello---", "hello"),
    ("  hello  ", "hello"),
    ("a/b/c", "a_b_c"),
    ("x" * 100, "x" * 80),
    ("https://", ""),
]


@pytest.mark.parametrize("raw,expected", _SLUGIFY_CASES)
def test_slugify(raw, expected):
    assert _slugify(raw) == expected


# ── _proxy_kwargs ──

def test_proxy_kwargs_no_env(monkeypatch):
    monkeypatch.delenv("BROWSER_USE_PROXY_COUNTRY", raising=False)
    monkeypatch.delenv("BROWSER_USE_CUSTOM_PROXY_HOST", raising=False)
    assert _proxy_kwargs() == {}


def test_proxy_kwargs_country_set(monkeypatch):
    monkeypatch.setenv("BROWSER_USE_PROXY_COUNTRY", "de")
    monkeypatch.delenv("BROWSER_USE_CUSTOM_PROXY_HOST", raising=False)
    result = _proxy_kwargs()
    assert result == {"proxy_country_code": "de"}


def test_proxy_kwargs_country_none(monkeypatch):
    monkeypatch.setenv("BROWSER_USE_PROXY_COUNTRY", "none")
    monkeypatch.delenv("BROWSER_USE_CUSTOM_PROXY_HOST", raising=False)
    result = _proxy_kwargs()
    assert result == {"proxy_country_code": None}


def test_proxy_kwargs_custom_host(monkeypatch):
    monkeypatch.delenv("BROWSER_USE_PROXY_COUNTRY", raising=False)
    monkeypatch.setenv("BROWSER_USE_CUSTOM_PROXY_HOST", "proxy.example.com")
    monkeypatch.delenv("BROWSER_USE_CUSTOM_PROXY_PORT", raising=False)
    monkeypatch.delenv("BROWSER_USE_CUSTOM_PROXY_USERNAME", raising=False)
    monkeypatch.delenv("BROWSER_USE_CUSTOM_PROXY_PASSWORD", raising=False)
    result = _proxy_kwargs()
    assert result == {
        "proxy_country_code": None,
        "custom_proxy": {"host": "proxy.example.com"},
    }


def test_proxy_kwargs_custom_with_all_fields(monkeypatch):
    monkeypatch.delenv("BROWSER_USE_PROXY_COUNTRY", raising=False)
    monkeypatch.setenv("BROWSER_USE_CUSTOM_PROXY_HOST", "proxy.example.com")
    monkeypatch.setenv("BROWSER_USE_CUSTOM_PROXY_PORT", "3128")
    monkeypatch.setenv("BROWSER_USE_CUSTOM_PROXY_USERNAME", "user1")
    monkeypatch.setenv("BROWSER_USE_CUSTOM_PROXY_PASSWORD", "pass1")
    result = _proxy_kwargs()
    assert result == {
        "proxy_country_code": None,
        "custom_proxy": {
            "host": "proxy.example.com",
            "port": 3128,
            "username": "user1",
            "password": "pass1",
        },
    }


def test_proxy_kwargs_custom_overrides_country(monkeypatch):
    monkeypatch.setenv("BROWSER_USE_PROXY_COUNTRY", "gb")
    monkeypatch.setenv("BROWSER_USE_CUSTOM_PROXY_HOST", "custom.proxy")
    monkeypatch.delenv("BROWSER_USE_CUSTOM_PROXY_PORT", raising=False)
    monkeypatch.delenv("BROWSER_USE_CUSTOM_PROXY_USERNAME", raising=False)
    monkeypatch.delenv("BROWSER_USE_CUSTOM_PROXY_PASSWORD", raising=False)
    result = _proxy_kwargs()
    # custom host should override country — residential country set to None
    assert result["proxy_country_code"] is None
    assert result["custom_proxy"]["host"] == "custom.proxy"


# ── _save_articles ──

def test_save_articles_single(tmp_path):
    articles = [
        {"title": "Test Article", "url": "https://example.com", "content": "word " * 150},
    ]
    count = _save_articles(articles, str(tmp_path))
    assert count == 1
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8")
    assert "# Test Article" in content
    assert "> Source: https://example.com" in content
    assert "word " * 150 in content


def test_save_articles_multiple(tmp_path):
    articles = [
        {"title": "First", "url": "https://a.com", "content": "word " * 200},
        {"title": "Second", "url": "https://b.com", "content": "word " * 200},
    ]
    count = _save_articles(articles, str(tmp_path))
    assert count == 2
    assert len(list(tmp_path.iterdir())) == 2


def test_save_articles_deduplicates_filenames(tmp_path):
    articles = [
        {"title": "Same Title", "url": "https://a.com", "content": "word " * 200},
        {"title": "Same Title", "url": "https://b.com", "content": "word " * 200},
    ]
    count = _save_articles(articles, str(tmp_path))
    assert count == 2
    names = sorted(f.name for f in tmp_path.iterdir())
    # _slugify preserves case, duplicates get _N suffix
    assert names == ["Same-Title.md", "Same-Title_1.md"]


def test_save_articles_empty_list(tmp_path):
    count = _save_articles([], str(tmp_path))
    assert count == 0
    assert len(list(tmp_path.iterdir())) == 0


# ── _save_urls ──

def test_save_urls_creates_json(tmp_path):
    urls = ["https://a.com", "https://b.com"]
    _save_urls(urls, "test keyword", str(tmp_path))
    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text(encoding="utf-8"))
    assert data["keyword"] == "test keyword"
    assert data["urls"] == ["https://a.com", "https://b.com"]


def test_save_urls_empty(tmp_path):
    _save_urls([], "empty kw", str(tmp_path))
    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text(encoding="utf-8"))
    assert data["urls"] == []



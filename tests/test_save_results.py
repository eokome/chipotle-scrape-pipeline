import re
import pytest
from pathlib import Path


# --- helpers that mirror the inline logic in scrape_pipeline.py ---

def _slug(url: str) -> str:
    """Same regex as used inline in scrape_pipeline.py."""
    return re.sub(r"[^a-zA-Z0-9.\-]", "_", url.replace("https://", "").replace("http://", "")).rstrip("_")


def _content(url: str, title: str, run_date: str, markdown: str | None) -> str:
    """Same f-string as used inline in scrape_pipeline.py."""
    return f"---\nurl: {url}\ntitle: {title}\ndate: {run_date}\n---\n\n{markdown or ''}"


# --- slug tests ---

def test_slug_strips_scheme_and_replaces_slashes():
    assert _slug("https://ir.chipotle.com/news-releases") == "ir.chipotle.com_news-releases"


def test_slug_handles_http():
    assert _slug("http://example.com/foo/bar") == "example.com_foo_bar"


def test_slug_strips_trailing_underscore():
    # URL with trailing slash would otherwise leave a trailing _
    assert _slug("https://ir.chipotle.com/") == "ir.chipotle.com"


def test_slug_preserves_dots_and_hyphens():
    assert _slug("https://newsroom.chipotle.com/press-releases") == "newsroom.chipotle.com_press-releases"


# --- file content tests ---

def test_content_has_front_matter():
    c = _content("https://ir.chipotle.com/news-releases", "News Releases", "2026-04-15", "# Hello")
    assert c.startswith("---\nurl: https://ir.chipotle.com/news-releases\n")
    assert "title: News Releases\n" in c
    assert "date: 2026-04-15\n" in c
    assert c.endswith("# Hello")


def test_content_blank_markdown_does_not_crash():
    c = _content("https://example.com", "Example", "2026-04-15", None)
    assert c.endswith("---\n\n")


# --- overwrite behavior tests ---

def test_saved_label_for_new_file(tmp_path):
    filepath = tmp_path / "result.md"
    assert not filepath.exists()
    label = "[overwrite]" if filepath.exists() else "[saved]"
    filepath.write_text("content", encoding="utf-8")
    assert label == "[saved]"
    assert filepath.read_text() == "content"


def test_overwrite_label_for_existing_file(tmp_path):
    filepath = tmp_path / "result.md"
    filepath.write_text("old content", encoding="utf-8")
    label = "[overwrite]" if filepath.exists() else "[saved]"
    filepath.write_text("new content", encoding="utf-8")
    assert label == "[overwrite]"
    assert filepath.read_text() == "new content"

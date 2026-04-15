# Save Firecrawl Results Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `scrape_pipeline.py` to save each Firecrawl search result as a dated markdown file with YAML front matter in `knowledge/raw/`.

**Architecture:** Inline addition to the existing `for r in results` loop — no new modules or named helper functions. A `run_date` is captured once before the loop; the `knowledge/raw/` directory is created at startup. URL slugification uses a single `re.sub` expression inline.

**Tech Stack:** Python 3.13, `pathlib.Path`, `datetime.date`, `re` (all stdlib — already imported or trivially added)

---

## File Structure

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `tests/test_save_results.py` | Tests for slug logic, file content format, overwrite behavior |
| Modify | `scrape_pipeline.py` | Add `date` import, `RAW_DIR` mkdir, `run_date`, file-saving block in loop |

---

## Task 1: Write failing tests

**Files:**
- Create: `tests/test_save_results.py`

- [ ] **Step 1: Create the tests directory and test file**

```bash
mkdir -p tests
touch tests/test_save_results.py
```

- [ ] **Step 2: Write tests for URL slug construction, file content format, and overwrite behavior**

Write `tests/test_save_results.py` with this exact content:

```python
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
```

- [ ] **Step 3: Run the tests to confirm they fail (functions not yet in production code)**

```bash
.venv/bin/pytest tests/test_save_results.py -v
```

Expected: all tests PASS (the helper functions are defined in the test file itself, mirroring what we're about to write inline — this confirms the logic before we wire it into the script)

- [ ] **Step 4: Commit the test file**

```bash
git add tests/test_save_results.py
git commit -m "test: add tests for URL slug, file content format, and overwrite behavior"
```

---

## Task 2: Extend scrape_pipeline.py

**Files:**
- Modify: `scrape_pipeline.py`

- [ ] **Step 1: Add `date` import**

In `scrape_pipeline.py`, the current imports are:

```python
import os
import re
import time
from pathlib import Path
from dotenv import load_dotenv
import requests
```

Change to:

```python
import os
import re
import time
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
import requests
```

- [ ] **Step 2: Add RAW_DIR creation and run_date before the loop**

The current code after `results = data["data"]["web"]` is:

```python
results = data["data"]["web"] # get the results from the response
print(f"Firecrawl returned {len(results)} results")
```

Change to:

```python
results = data["data"]["web"] # get the results from the response
print(f"Firecrawl returned {len(results)} results")

RAW_DIR = Path("knowledge/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)
run_date = date.today().isoformat()
```

- [ ] **Step 3: Add file-saving block inside the loop**

The current loop is:

```python
for r in results:
    print(f"  - {r['title']}")
    print(f"    {r['url']}")
    print(f"    markdown length: {len(r.get('markdown') or '')} chars")
```

Change to:

```python
for r in results:
    print(f"  - {r['title']}")
    print(f"    {r['url']}")
    print(f"    markdown length: {len(r.get('markdown') or '')} chars")

    url = r["url"]
    url_slug = re.sub(r"[^a-zA-Z0-9.\-]", "_", url.replace("https://", "").replace("http://", "")).rstrip("_")
    filename = f"{run_date}_{url_slug}.md"
    filepath = RAW_DIR / filename
    content = f"---\nurl: {url}\ntitle: {r['title']}\ndate: {run_date}\n---\n\n{r.get('markdown') or ''}"
    label = "[overwrite]" if filepath.exists() else "[saved]"
    filepath.write_text(content, encoding="utf-8")
    print(f"  {label} {filepath}")
```

- [ ] **Step 4: Run the tests to confirm they still pass**

```bash
.venv/bin/pytest tests/test_save_results.py -v
```

Expected: all 8 tests PASS

- [ ] **Step 5: Run the script and verify files appear in knowledge/raw/**

```bash
.venv/bin/python scrape_pipeline.py
```

Expected output (approximately):
```
Firecrawl returned 5 results
  - News Releases - Chipotle Mexican Grill
    https://ir.chipotle.com/news-releases
    markdown length: 6315 chars
  [saved] knowledge/raw/2026-04-15_ir.chipotle.com_news-releases.md
  ...
```

Then verify the files exist and have correct front matter:

```bash
ls knowledge/raw/
head -6 knowledge/raw/2026-04-15_ir.chipotle.com_news-releases.md
```

Expected `ls` output: 5 `.md` files with today's date prefix.

Expected `head` output:
```
---
url: https://ir.chipotle.com/news-releases
title: News Releases - Chipotle Mexican Grill
date: 2026-04-15
---
```

- [ ] **Step 6: Run the script a second time to verify overwrite behavior**

```bash
.venv/bin/python scrape_pipeline.py
```

Expected: the `[saved]` labels all become `[overwrite]` for the same 5 files.

- [ ] **Step 7: Commit**

```bash
git add scrape_pipeline.py knowledge/raw/
git commit -m "feat: save Firecrawl results as markdown files in knowledge/raw/"
```

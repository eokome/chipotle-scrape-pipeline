# Design: Save Firecrawl Results to knowledge/raw/

**Date:** 2026-04-15

## Overview

Extend `scrape_pipeline.py` to persist each Firecrawl search result as a
markdown file in `knowledge/raw/` after the existing fetch-and-print loop.

## Architecture

Inline addition to `scrape_pipeline.py` — no new files, no helper functions.
Changes are confined to the bottom of the existing `for r in results` loop.

A single `run_date = date.today().isoformat()` is computed once before the loop.
`knowledge/raw/` is created at startup with `Path.mkdir(parents=True, exist_ok=True)`.

## Filename Construction

The result URL is sanitized into a safe filename segment:

1. Strip the scheme (`https://`)
2. Replace `/` and any non-alphanumeric characters (except `.` and `-`) with `_`
3. Strip trailing `_`

Example:
```
https://ir.chipotle.com/news-releases  →  ir.chipotle.com_news-releases
```

Final filename pattern: `{run_date}_{url_slug}.md`
Example: `2026-04-15_ir.chipotle.com_news-releases.md`

## File Content

Each file contains a YAML front matter block followed by the scraped markdown:

```markdown
---
url: https://ir.chipotle.com/news-releases
title: News Releases - Chipotle Mexican Grill
date: 2026-04-15
---

<scraped markdown content>
```

If a result has no `markdown` field, the content section is left blank (no crash).

## Overwrite Behavior

Files are always written (overwrite on re-run). Console output distinguishes
new vs. overwritten files:

- New file: `  [saved] knowledge/raw/2026-04-15_ir.chipotle.com_news-releases.md`
- Overwrite: `  [overwrite] knowledge/raw/2026-04-15_ir.chipotle.com_news-releases.md`

## Out of Scope

- Deduplication across dates
- Incremental / delta runs
- Any downstream processing of saved files

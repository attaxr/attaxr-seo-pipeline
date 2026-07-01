---
name: seo-pipeline-bash
description: "One-shot SEO content pipeline: scrape keywords from SERP and produce article markdown files via Browser Use SDK or DuckDuckGo fallback."
tags:
  - seo
  - content-pipeline
  - scraping
  - keyword-research
  - bash
triggers:
  - "run the bash pipeline"
  - "run seo pipeline"
summary: "Run `python -m seo_pipeline --from-json keywords.json` from the repo root."
---

# SEO Pipeline (bash)

Runs a 3-stage pipeline:

1. **Scrape** — `python -m seo_pipeline --from-json keywords.json`
   - Browser Use SDK primary (AI-driven article extraction)
   - DuckDuckGo search fallback (URL discovery only)
2. **Analyze** — review scraped content manually or via agent
3. **Create** — write article draft to `pipeline_data/drafts/`

## Setup

```bash
python scripts/setup.py              # interactive (installs browser-use-sdk, sets .env, redacted key input)
# or:
export BROWSER_USE_API_KEY=bu_...
```

## Run

```bash
python -m seo_pipeline --from-json keywords.json
python -m seo_pipeline "your search keyword"
```

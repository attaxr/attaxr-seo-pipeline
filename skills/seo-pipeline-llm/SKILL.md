---
name: seo-pipeline-llm
description: "4-stage SEO content pipeline: keyword research → competitor scraping → SEO analysis → content creation. Outputs local files, no CMS integration."
tags:
  - seo
  - content-pipeline
  - keyword-research
  - competitor-analysis
  - content-creation
triggers:
  - "run the seo pipeline"
  - "run seo pipeline for [keyword]"
  - "create blog content for SEO"
  - "run keyword research"
  - "analyze competitor content"
summary: "Systematic 4-stage SEO content pipeline from keyword research to local file output."
---

# SEO Content Pipeline (LLM)

## How to Run

1. **Say it** — *"run the SEO pipeline for [keyword]"*
2. **Schedule it** — as a recurring cron job
3. **Script it** — `python -m seo_pipeline` for the scraping portion

## Skills to Load

- **`browser-use`** — for web research and article scraping
- Research priority: browser-use MCP → browser-use CLI → web_search API

## Configuration

```bash
export SEO_PIPELINE_DIR=./pipeline_data
```

## Stage 1 — Keyword Research

Search for domain-relevant keywords. Capture phrase, volume, relevance, intent, cluster. Save to `keywords.json`.

## Stage 2 — Content Collection

For each keyword: search SERP, extract competitor articles. Save to `articles/`.

### Fallback
If browser tools unavailable: `python -m seo_pipeline --from-json keywords.json`
DuckDuckGo search is used for URL discovery only — set BROWSER_USE_API_KEY for full article extraction.

### If zero articles extracted
Stop. Do not proceed.

## Stage 3 — SEO Analysis

Analyze each article for keyword usage, gaps, depth, readability, structure, improvements.

**Critical:** Identify the unique angle none of the competitors cover.

## Stage 4 — Content Creation

Per cluster: 1,500+ words, unique angle, H2/H3 hierarchy, lists, case studies, CTA, image suggestions, humanization pass. Save to `drafts/`.

### Post-Creation — Humanization

Read the draft, strip AI-isms, adjust tone, vary rhythm. Sound like an expert explaining to a colleague.

## Output

```
pipeline_data/
├── articles/       # Scraped competitor content
├── analysis/       # SEO metadata
└── drafts/         # Generated articles
```

## Quality Checklist

- [ ] All 4 stages completed
- [ ] Each article ≥ 1,500 words
- [ ] Unique angle vs top 3 competitors
- [ ] SEO metadata complete
- [ ] ≥ 2 image suggestions per article
- [ ] Humanization pass applied
- [ ] Run report written

## Error Handling

- Fail-stop pipeline: `set -euo pipefail` in shell scripts
- Empty keywords: broaden search, try once, then report
- All scrapers fail: Stop

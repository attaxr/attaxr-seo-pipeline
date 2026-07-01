# SEO Content Pipeline — Copilot Instructions

> **Canonical source:** `AGENTS.md` (project root) — this file summarizes; the full pipeline lives there.

## Pipeline Overview

4 stages, sequential, fail-stop. Each feeds the next. Runs entirely on local files — no CMS.

```
Keyword Research → Content Collection → SEO Analysis → Content Creation
```

## Stage 1 — Keyword Research

- Search for domain-relevant keywords using web search.
- Capture: term, search volume, difficulty (1-100), relevance (1-5), intent (informational/commercial/navigational), cluster name.
- Prioritize long-tail keywords with commercial intent.
- Save to `keywords.json`.

## Stage 2 — Content Collection

**CREDENTIAL CHECK (required before any scraping):**
1. Check `BROWSER_USE_API_KEY` env var → if missing, source `.env` → if still missing, prompt user with redacted input.
2. Never echo the key in tool output, terminal, or conversation history.
3. Do not proceed without a valid key.

**Primary:** `python -m seo_pipeline --from-json keywords.json` (Browser Use Cloud SDK v3).
**Fallback:** DuckDuckGo HTML search (URL discovery only — no article body).
**If both yield zero articles:** Stop. Do not proceed to Stage 3.

## Stage 3 — SEO Analysis

Per article, analyze: keyword usage (title, H1, first 100 words, density), keyword gaps, content depth/missing subtopics, readability (jargon, paragraph length), structure (H2/H3 hierarchy, lists, tables), 3-5 actionable improvements.

**Critical:** Identify the unique angle none of the top competitors cover.

Save to `pipeline_data/analysis/`.

## Stage 4 — Content Creation

Per keyword cluster: 1,500+ words, original insight in first 200 words, H2/H3 hierarchy targeting primary + secondary keywords, at least one bullet/numbered list, concrete example or case study, CTA paragraph, 2-3 image suggestions.

**Post-creation:** Humanization pass — strip AI-isms, adjust tone, vary sentence rhythm, active voice.

Save to `pipeline_data/drafts/`.

## Quality Checklist

- [ ] All 4 stages completed or explicitly skipped
- [ ] Each article ≥ 1,500 words
- [ ] Each article has a unique angle vs top 3 competitors
- [ ] SEO metadata complete (title, description, headings, keyword gaps)
- [ ] At least 2 image suggestions per article
- [ ] Humanization pass applied
- [ ] Run report written

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SEO_PIPELINE_DIR` | `./pipeline_data/` | Pipeline artifact directory |
| `BROWSER_USE_API_KEY` | — | Browser Use Cloud API key |
| `AUTHOR_NAME` | `Author Name` | Default article author |

Set via `.env` or export. Run `python scripts/setup.py` for interactive setup.

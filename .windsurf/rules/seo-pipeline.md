# SEO Content Pipeline — Windsurf Rules

> **Canonical source:** `AGENTS.md` (project root) — full pipeline details live there.

## Pipeline (sequential, fail-stop)

4 stages, each feeds the next. If a stage fails on an item, log and continue.

```
Keyword Research → Content Collection → SEO Analysis → Content Creation
```

## Stage 1 — Keyword Research

Search domain keywords. Capture: term, search volume, difficulty, relevance (1-5), intent (commercial/informational/navigational), cluster. Prioritize long-tail commercial terms. Save to `keywords.json`.

## Stage 2 — Content Collection

**Credential check (REQUIRED):**
1. Check `BROWSER_USE_API_KEY` → source `.env` → prompt user (redacted input via `getpass.getpass()`).
2. Never echo the key in any output.
3. Do not proceed without a valid key.

**Primary:** `python -m seo_pipeline --from-json keywords.json`
**Fallback:** DuckDuckGo HTML (URLs only)
**Both fail:** Stop. No Stage 3.

## Stage 3 — SEO Analysis

Per article: keyword usage (title, H1, first 100 words, density), gaps, missing subtopics, readability, structure (H2/H3, lists, tables), 3-5 actionable improvements.

**Must find:** unique angle no competitor covers. Save to `pipeline_data/analysis/`.

## Stage 4 — Content Creation

Per cluster: 1,500+ words, original insight in first 200 words, H2/H3 hierarchy, lists, case study, CTA, 2-3 image suggestions.

**Humanization:** strip AI-isms, adjust tone, vary rhythm, active voice. Save to `pipeline_data/drafts/`.

## Quality Checklist

- [ ] All 4 stages completed or explicitly skipped
- [ ] Each article ≥ 1,500 words
- [ ] Unique angle vs top 3 competitors
- [ ] SEO metadata complete (title, description, headings, keyword gaps)
- [ ] ≥ 2 image suggestions per article
- [ ] Humanization pass applied
- [ ] Run report written

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SEO_PIPELINE_DIR` | `./pipeline_data/` | Artifact directory |
| `BROWSER_USE_API_KEY` | — | Browser Use Cloud API key |
| `AUTHOR_NAME` | `Author Name` | Default article author |

Set via `.env` or export. Run `python scripts/setup.py` for interactive setup.

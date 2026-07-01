# SEO Content Pipeline Agent Instructions

> **Platform-agnostic workflow** — works with Hermes Agent, Claude Code, Codex, OpenCode, or any LLM-based agent framework that supports tool calling (web search, file I/O, terminal, browser automation).

A 4-stage pipeline for systematic SEO content research, analysis, and creation. Outputs local files — no CMS integration.

## How This Works

Runs as a **stage-by-stage loop**, one keyword cluster at a time. Each stage feeds the next. If a stage fails on a specific item, log the error and continue.

### Agent Framework Requirements

| Capability | Used In | Purpose |
|-----------|---------|---------|
| Web search API | Stage 1-2 | Keyword research, SERP extraction |
| Browser automation / MCP | Stage 2 | Article content scraping |
| File system read/write | All stages | Data persistence between stages |
| LLM text generation | Stage 3-4 | SEO analysis, content creation |
| Python execution | Stage 2 | Scraping |

---

## Stage 1 — Keyword Research

1. Use web search to research keywords related to the business domain.
2. For each keyword, capture: phrase, estimated search volume, relevance (1-5), commercial intent, cluster name.
3. Prioritize **long-tail keywords** with clear commercial intent.
4. Save to `keywords.json`.

**Schema:**
```json
[{"term":"keyword","search_volume":3200,"difficulty":72,"relevance":5,"intent":"commercial","cluster":"cluster-name"}]
```

---

## Stage 2 — Content Collection

### ⚠️ Step 0 — Credential Check (REQUIRED)

Before attempting any scraping, the agent MUST verify that `BROWSER_USE_API_KEY` is configured:

1. **Check** if the environment variable `BROWSER_USE_API_KEY` is set.
2. **If not set** and a `.env` file exists, load it via:
   ```
   python -c "from pathlib import Path; import os; exec(open(Path('.env')).read().replace('export ',''))"
   ```
   Then re-check the variable.
3. **If still not set**, the agent MUST prompt the user interactively:
   ```
   "BROWSER_USE_API_KEY is not configured. This is required for article extraction.
    Enter your key (starts with 'bu_'): "
   ```
4. **Security rules for the key input:**
   - The key must be captured via a **redacted input method** — never via plain `input()` or echo-enabled prompts.
   - The `python scripts/setup.py` script uses `getpass.getpass()` which masks input; pass control to it when feasible.
   - The key value must **never appear in logs, terminal scrollback, conversation history, or LLM output**.
   - If you write the key to `.env` on the user's behalf, do so with `set +o history` and sanitize any terminal output.
   - After capturing, write to `.env` and source it: `set -a; source .env; set +a`
   - Do not proceed without a valid key.

> **Why this matters:** The Browser Use Cloud SDK uses this key to authenticate API requests. Without it, the primary scraper cannot extract article content. The DuckDuckGo fallback discovers URLs only — it does not fetch content from modern websites.

### Step 1 — Install Package

Install the package once so `seo_pipeline` is importable:

```
pip install -e .
```

### Step 2 — Primary Scraper

```
python -m seo_pipeline --from-json keywords.json
```

- Uses **Browser Use Cloud SDK v3** — an AI agent that searches Google, navigates results, and extracts full article text.
- **REQUIRES `BROWSER_USE_API_KEY`** (get one at https://cloud.browser-use.com/settings?tab=api-keys).
- Run `python scripts/setup.py` for interactive configuration (installs SDK, sets up `.env` with redacted key input).
- Docs: https://docs.browser-use.com/cloud/quickstart

### Step 3 — Fallback

If Browser Use is unavailable or returns no results, the scraper automatically falls back to DuckDuckGo HTML search. The DuckDuckGo path discovers URLs only — it does not fetch article body content (modern sites block plain HTTP requests).

### If both methods yield zero articles

Stop. Do not proceed to Stage 3 with empty data. Report the issue including whether `BROWSER_USE_API_KEY` was set.

---

## Stage 3 — SEO Analysis

For each scraped article, analyze:
- **Keyword usage**: Title, H1, first 100 words, density
- **Keyword gaps**: Related keywords the article misses
- **Content depth**: Missing subtopics
- **Readability**: Jargon, paragraph length
- **Structure**: H2/H3 hierarchy, lists, tables
- **Actionable improvements**: 3-5 things to do better

**Critical output:** Identify the **unique angle** none of the top competitors cover. Save to `pipeline_data/analysis/`.

---

## Stage 4 — Content Creation

For each keyword cluster:
1. Review competitor articles + SEO analysis.
2. Write the article in markdown. Requirements:
   - Minimum 1,500 words
   - Original insight or data point in first 200 words
   - H2/H3 hierarchy targeting primary + secondary keywords
   - At least one bullet/numbered list
   - Concrete example or case study
   - CTA paragraph
3. **Image suggestions:** 2-3 descriptions per article.
4. Save to `pipeline_data/drafts/`.

### Post-Creation — Humanization
After writing, apply a humanization pass: strip AI-isms, adjust tone, vary sentence rhythm, use active voice. The goal: sounds like an experienced professional explaining to a colleague.

---

## Credential Security

The `BROWSER_USE_API_KEY` is a sensitive credential. The pipeline enforces these security measures:

| Measure | Implementation |
|---------|---------------|
| Redacted input | `getpass.getpass()` (no echo) in `scripts/setup.py` |
| Plaintext suppression | Key is masked (e.g. `bu_abc...xyz`) in console output |
| Environment isolation | Key stored to `.env` file at repo root |
| No hardcoding | Key is never embedded in source code or agent instructions |
| AI agent protocol | The agent must not print, log, or echo the key in any tool output, terminal output, or conversation history |

When the agent runs the credential check (Stage 2, Step 0):
1. Check env var → check `.env` → prompt user
2. If prompting, hand over to `python scripts/setup.py` when possible
3. If handling inline, use redacted input (not plain `input()`)
4. Never echo the key in any visible output

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SEO_PIPELINE_DIR` | `./pipeline_data/` | Directory for pipeline artifacts |
| `BROWSER_USE_API_KEY` | — | API key for Browser Use Cloud (starts with `bu_`) |
| `BROWSER_USE_PROXY_COUNTRY` | `us` | Residential proxy country code (ISO 3166-1 alpha-2). Set to `none` to disable |
| `BROWSER_USE_CUSTOM_PROXY_HOST` | — | Custom proxy host. Overrides residential proxy when set |
| `BROWSER_USE_CUSTOM_PROXY_PORT` | `8080` | Custom proxy port |
| `BROWSER_USE_CUSTOM_PROXY_USERNAME` | — | Custom proxy username (optional) |
| `BROWSER_USE_CUSTOM_PROXY_PASSWORD` | — | Custom proxy password (optional) |

## Output Structure

```
pipeline_data/
├── articles/       # Scraped competitor content
├── analysis/       # SEO metadata per article
└── drafts/         # Generated article drafts (JSON + markdown)
```

## Quality Checklist

- [ ] All 4 stages completed or explicitly skipped
- [ ] Each article ≥ 1,500 words
- [ ] Each article has a unique angle vs top 3 competitors
- [ ] SEO metadata complete (title, description, headings, keyword gaps)
- [ ] At least 2 image suggestions per article
- [ ] Humanization pass applied
- [ ] Run report written

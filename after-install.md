# SEO Pipeline — Installed

> **Platform-agnostic:** works with Hermes, Claude Code, Codex, OpenCode, Copilot CLI, Cursor, Windsurf, Cline/Aider, and the Pi agent harness.

## Enable

If you installed without `--enable`:

```bash
hermes plugins enable seo-pipeline
```

## Load the Pipeline Skill

```bash
skill_view(name='seo-pipeline-llm')
```

Then in chat:

> *"run the SEO pipeline for [topic]"*

## CLI Commands

```bash
# Interactive Browser Use setup (masks API key input)
python scripts/setup.py

# Scrape articles for keywords in a JSON file
python -m seo_pipeline --from-json keywords.json

# Scrape articles for one keyword
python -m seo_pipeline "your search keyword"
```

## Schedule (Hermes Cron)

Weekly pipeline on Monday at 9am:

```bash
cronjob action=create schedule="0 9 * * 1" name="weekly-seo" \
  prompt="Run the SEO content pipeline for [topic]. Execute all 4 stages." \
  skills='["seo-pipeline-llm"]'
```

## Configuration

Create a `.env` file in the repo root or set these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `BROWSER_USE_API_KEY` | — | Required for article extraction (get at https://cloud.browser-use.com) |
| `BROWSER_USE_PROXY_COUNTRY` | `us` | Residential proxy country |
| `SEO_PIPELINE_DIR` | `./pipeline_data/` | Output directory |

Run `python scripts/setup.py` for interactive configuration with redacted key input.

## Bundled Skills

| Skill | Description |
|-------|-------------|
| `seo-pipeline-llm` | Full 4-stage LLM-driven pipeline |
| `seo-pipeline-bash` | One-shot bash scraping pipeline |

## Commands (Hermes)

| Command | Description |
|---------|-------------|
| `/run-pipeline` | Execute all 4 stages for a topic |

## Docs

- [AGENTS.md](AGENTS.md) — Full pipeline instructions
- [README.md](README.md) — Overview and agent install matrix
- [examples/](examples/) — Usage examples and walkthroughs

# SEO Pipeline — Usage Examples

## Full Pipeline (all 4 stages)

```
> run the SEO pipeline for "Docker networking best practices"
```

## Single Stage

```
> run stage 1 keyword research for "Kubernetes monitoring tools"
> scrape articles for "Terraform state management"
> analyze the scraped articles for "CI/CD pipeline optimization"
> draft an article for "GitHub Actions security hardening"
```

## From a Keyword File

```bash
python -m seo_pipeline --from-json keywords.json
```

## With a Single Keyword

```bash
python -m seo_pipeline "Docker multi-stage builds optimization"
```

## Scheduled (Hermes Cron)

```bash
cronjob action=create schedule="0 9 * * 1" name="weekly-seo" \
  prompt="Run the SEO content pipeline for 'DevOps tooling best practices'. Execute all 4 stages." \
  skills='["seo-pipeline-llm"]'
```

## Output Structure

```
pipeline_data/
├── articles/       # Scraped competitor content (markdown)
├── analysis/       # SEO metadata JSON per article
└── drafts/         # Generated article drafts (markdown + JSON)
```

## Setup

```bash
# Interactive (sets up BROWSER_USE_API_KEY with masked input)
python scripts/setup.py

# Or manual
export BROWSER_USE_API_KEY=bu_your_key_here
python -m seo_pipeline "your keyword"
```

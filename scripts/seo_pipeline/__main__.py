"""python -m seo_pipeline — run the scraper CLI.

Usage:
    python -m seo_pipeline <keyword> [<keyword>...] [--outdir <path>]
    python -m seo_pipeline --from-json keywords.json [--outdir <path>]
"""
from seo_pipeline.scraper import main

main()

"""SEO Content Pipeline — Hermes plugin entry point.

Registers skills, lifecycle hooks, and the /run-pipeline slash command
with the Hermes Agent runtime.  The plugin.yaml manifest declares what
this module provides via def register(ctx).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

__version__ = "0.3.0"
ROOT = Path(__file__).resolve().parent
SKILLS_DIR = ROOT / "skills"


def register(ctx: Any) -> None:
    """Register seo-pipeline skills, hooks, and commands with Hermes."""

    for child in sorted(SKILLS_DIR.iterdir()) if SKILLS_DIR.exists() else []:
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            ctx.register_skill(child.name, skill_md)

    def pre_llm_call(**_: Any) -> dict[str, str] | None:
        key = (os.environ.get("BROWSER_USE_API_KEY") or "").strip()
        if not key:
            return {
                "context": (
                    "WARNING: BROWSER_USE_API_KEY is not set. "
                    "The pipeline cannot extract article content without it. "
                    "Run `python scripts/setup.py` or configure it in .env"
                )
            }
        return None

    ctx.register_hook("pre_llm_call", pre_llm_call)

    def pipeline_command(raw_args: str = "") -> str:
        topic = raw_args.strip() or "the configured domain"
        return f"Run the SEO pipeline for {topic}. Follow AGENTS.md."

    def pre_gateway_dispatch(event: Any = None, **_: Any) -> dict[str, str] | None:
        text = str(getattr(event, "text", "") or "").strip()
        if not text.startswith("/"):
            return None
        cmd, _, rest = text[1:].partition(" ")
        if cmd != "run-pipeline":
            return None
        return {"action": "rewrite", "text": pipeline_command(rest)}

    ctx.register_hook("pre_gateway_dispatch", pre_gateway_dispatch)
    ctx.register_command(
        "run-pipeline",
        pipeline_command,
        description="Run the 4-stage SEO content pipeline for a topic",
        args_hint="[topic or keyword]",
    )
